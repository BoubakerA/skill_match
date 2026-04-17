import logging
import nltk
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import PorterStemmer
import numpy as np
from transformers import pipeline

nltk.download("punkt", quiet=True)

logger = logging.getLogger(__name__)

_nlp = None
_stemmer = None
_ner_pipeline = None
_sentence_model = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        logger.info("Loading spaCy model...")
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _get_stemmer():
    global _stemmer
    if _stemmer is None:
        _stemmer = PorterStemmer()
    return _stemmer


def _get_models(
    ner_model_name: str = "jjzha/jobbert-base-cased",
    sentence_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
):
    """
    Initialise (once) and return the NER pipeline and the sentence encoder.
    Pass custom model names to override defaults.
    """
    global _ner_pipeline, _sentence_model

    if _ner_pipeline is None:
        logger.info("Loading NER model: %s", ner_model_name)
        _ner_model = AutoModelForTokenClassification.from_pretrained(ner_model_name)
        _ner_tokenizer = AutoTokenizer.from_pretrained(ner_model_name)
        _ner_pipeline = pipeline(
                        "ner",
                        model="feliponi/hirly-ner-multi",
                        aggregation_strategy="simple")

    if _sentence_model is None:
        logger.info("Loading sentence-transformer: %s", sentence_model_name)
        _sentence_model = SentenceTransformer(sentence_model_name)

    return _ner_pipeline, _sentence_model


def normalize_skill(skill: str) -> str:
    """Lemmatise and clean a skill string."""
    nlp = _get_nlp()
    doc = nlp(skill.lower().strip())
    tokens = [
        token.lemma_
        for token in doc
        if token.text not in STOP_WORDS and not token.is_punct
    ]
    result = " ".join(tokens)
    return result if result else skill.lower().strip()


def stem_skill(skill: str) -> str:
    """Apply Porter stemming to a (already normalised) skill string."""
    stemmer = _get_stemmer()
    return " ".join(stemmer.stem(word) for word in skill.lower().split())


def _split_into_chunks(text: str, tokenizer, max_tokens: int = 512):
    """
    Split *text* into sentence-aligned chunks that fit within *max_tokens*
    after tokenisation — avoids the silent character-truncation bug.
    """
    sentences = [s.strip() for s in text.split("\n") if s.strip()]
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        token_len = len(tokenizer.tokenize(sentence))
        if current_len + token_len > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_len = token_len
        else:
            current_chunk.append(sentence)
            current_len += token_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def extract_skills(text: str, ner_pipe, tokenizer, confidence: float = 0.7) -> list[str]:
    """
    Extract skills from *text* using NER + lemmatisation.

    Each line is tokenizer-aware chunked to avoid silent truncation,
    then passed through the NER pipeline. Only HSKILL / SSKILL entities
    above *confidence* are kept.
    """
    chunks = _split_into_chunks(str(text), tokenizer)
    skills = {}

    for chunk in chunks:
        entities = ner_pipe(chunk)
        for e in entities:
            if e["entity_group"] in ("SKILL", "SOFT_SKILL") and e["score"] >= confidence:
                word = e["word"].strip()
            if word:
                skills[normalize_skill(word)] = word

    return skills

def _semantic_similarity(skill_a: str, skill_b: str, model: SentenceTransformer) -> float:
    emb = model.encode([skill_a, skill_b])
    return float(cosine_similarity([emb[0]], [emb[1]])[0][0])


def compare_skills(
    cv_skills: dict[str, str],
    jd_skills: dict[str, str],
    sentence_model: SentenceTransformer,
    semantic_threshold: float = 0.75,
) -> dict:
    """
    Compare CV and JD skill sets using a two-pass strategy:

    Returns a dict with cv_skills, jd_skills, present, missing, and
    semantic_matches (skills matched via embedding rather than stem).
    """
    cv_set = {s.lower().strip() for s in cv_skills.keys() if s.strip()}
    jd_set = {s.lower().strip() for s in jd_skills.keys() if s.strip()}

    # --- Pass 1: stem matching ---
    cv_stemmed = {stem_skill(s): s for s in cv_set}
    jd_stemmed = {stem_skill(s): s for s in jd_set}

    present_stems = set(cv_stemmed) & set(jd_stemmed)
    unmatched_jd_stems = set(jd_stemmed) - present_stems

    present = sorted(jd_stemmed[s] for s in present_stems)
    unmatched_jd = [jd_stemmed[s] for s in unmatched_jd_stems]

    # --- Pass 2: semantic matching for remaining JD skills ---
    semantic_matches = []
    truly_missing = []

    if unmatched_jd and cv_set:
        cv_list = list(cv_set)
        cv_embeddings = sentence_model.encode(cv_list)

        for jd_skill in unmatched_jd:
            jd_embedding = sentence_model.encode([jd_skill])
            sims = cosine_similarity(jd_embedding, cv_embeddings)[0]
            best_idx = int(np.argmax(sims))
            best_score = float(sims[best_idx])

            if best_score >= semantic_threshold:
                semantic_matches.append(
                    {
                        "jd_skill": jd_skill,
                        "cv_skill": cv_list[best_idx],
                        "score": round(best_score, 4),
                    }
                )
            else:
                truly_missing.append(jd_skill)
    else:
        truly_missing = unmatched_jd

    return {
        "cv_skills": sorted([cv_skills[skill] for skill in cv_set]),
        "jd_skills": sorted([jd_skills[skill] for skill in jd_set]),
        "present": present,
        "semantic_matches": semantic_matches,
        "missing": sorted(truly_missing),
    }

def match_cv_jd(
    cv_text: str,
    jd_text: str,
    ner_pipe,
    tokenizer,
    embedding_model: SentenceTransformer,
) -> dict:
    """
    Full pipeline: embed → NER extract → compare skills.
    Logs progress instead of printing.
    """
    logger.info("Computing document-level similarity...")
    jd_emb = embedding_model.encode([jd_text])
    cv_emb = embedding_model.encode([cv_text])
    score = cosine_similarity(cv_emb, jd_emb)[0][0] * 100

    logger.info("Extracting skills from CV...")
    cv_skills = extract_skills(cv_text, ner_pipe, tokenizer)
    print(f"============> raw cv_skills: {cv_skills}")
    logger.info("Extracting skills from JD...")
    jd_skills = extract_skills(jd_text, ner_pipe, tokenizer)
    print(f"============> raw jd_skills: {jd_skills}")

    result = compare_skills(cv_skills, jd_skills, embedding_model)
    result["similarity_score"] = round(float(score), 4)

    logger.info("=" * 50)
    logger.info("JD skills      : %s", result["jd_skills"])
    logger.info("CV skills      : %s", result["cv_skills"])
    logger.info("Present        : %s", result["present"])
    logger.info("Semantic match : %s", result["semantic_matches"])
    logger.info("Missing        : %s", result["missing"])
    logger.info("=" * 50)

    return result

def predict(cv_text: str, jd_text: str) -> dict:
    """
    Match a CV against a job description.
    Models are loaded on first call and reused on subsequent calls.
    """
    if not isinstance(cv_text, str) or not cv_text.strip():
        raise ValueError("cv_text must be a non-empty string.")
    if not isinstance(jd_text, str) or not jd_text.strip():
        raise ValueError("jd_text must be a non-empty string.")

    ner_pipe, sentence_model = _get_models()

    # Retrieve the tokenizer from the pipeline to use in chunking
    tokenizer = ner_pipe.tokenizer

    return match_cv_jd(cv_text, jd_text, ner_pipe, tokenizer, sentence_model)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    from skill_match.utils import read_uploaded_file

    resume_path = "/home/onyxia/work/skill_match/cv.txt"
    jd_path = "/home/onyxia/work/skill_match/jd.txt"

    with open(resume_path, "rb") as f:
        resume_txt = read_uploaded_file(f)

    with open(jd_path, "rb") as f:
        jd_txt = read_uploaded_file(f)

    result = predict(resume_txt, jd_txt)
