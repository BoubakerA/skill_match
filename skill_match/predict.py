import nltk
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import PorterStemmer

nltk.download('punkt', quiet=True)

nlp = spacy.load("en_core_web_sm")
stemmer = PorterStemmer()

def normalize_skill(skill: str) -> str:
    """Lemmatise et nettoie une compétence"""
    doc = nlp(skill.lower().strip())
    tokens = [token.lemma_ for token in doc if token.text not in STOP_WORDS and not token.is_punct]
    return " ".join(tokens)


def stem_skill(skill: str) -> str:
    """Applique le stemming sur une compétence"""
    return " ".join([stemmer.stem(word) for word in skill.lower().split()])


def extract_skills(text, ner_pipeline):
    """Extrait les compétences via NER + lemmatisation + matching ESCO"""
    lines = str(text).split("\n")

    # on reprend l'extraction ner
    ner_skills = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        entities = ner_pipeline(line[:512])
        skills = [
            normalize_skill(e["word"])
            for e in entities
            if e["entity_group"] in ("HSKILL", "SSKILL")
            and e["score"] >= 0.7
        ]
        ner_skills.extend(skills)


    return ner_skills


def compare_skills(cv_skills, jd_skills):
    """Compare les compétences avec stemming pour matcher les variantes"""
    cv_set = set(s.lower().strip() for s in cv_skills)
    jd_set = set(s.lower().strip() for s in jd_skills)

    # Stemming 
    cv_stemmed = {stem_skill(s): s for s in cv_set}
    jd_stemmed = {stem_skill(s): s for s in jd_set}

    present_stems = set(cv_stemmed.keys()) & set(jd_stemmed.keys())
    missing_stems = set(jd_stemmed.keys()) - set(cv_stemmed.keys())

    present = sorted([jd_stemmed[s] for s in present_stems])
    missing = sorted([jd_stemmed[s] for s in missing_stems])

    return {
        "cv_skills": sorted(cv_set),
        "jd_skills": sorted(jd_set),
        "present": present,
        "missing": missing,
    }


def match_cv_jd(cv_text, jd_text, ner_pipeline, embedding_model):
    ner = ner_pipeline

    jd_emb = embedding_model.encode([jd_text])
    cv_emb = embedding_model.encode([cv_text])
    score = cosine_similarity(cv_emb, jd_emb)[0][0]*100

    print("Extraction des compétences du CV...")
    cv_skills = extract_skills(cv_text, ner)

    print("Extraction des compétences de la JD...")
    jd_skills = extract_skills(jd_text, ner)

    result = compare_skills(cv_skills, jd_skills)
    result["similarity_score"] = round(float(score), 4)

    print("\n" + "="*50)
    print("\n💼 Compétences de l'offre :")
    print(result["jd_skills"])
    print("\n📄 Compétences du CV :")
    print(result["cv_skills"])
    print("\n❌ Compétences manquantes dans le CV :")
    print(result["missing"])
    print("="*50)

    return result


def predict(cv_text, jd_text):
    _ner_model_name = "Nucha/Nucha_SkillNER_BERT"
    _ner_model = AutoModelForTokenClassification.from_pretrained(_ner_model_name)
    _ner_tokenizer = AutoTokenizer.from_pretrained(_ner_model_name)
    _ner_pipeline = pipeline("ner", model=_ner_model, tokenizer=_ner_tokenizer, aggregation_strategy="simple")
    _sentence_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    return match_cv_jd(cv_text, jd_text, _ner_pipeline, _sentence_model)

if __name__ == "__main__":
    from skill_match.utils import read_uploaded_file
    resume_path = "/home/onyxia/work/skill_match/data/resume.txt"
    jd_path = "/home/onyxia/work/skill_match/data/job_description.txt"

    with open(resume_path, "rb") as f:
        resume_txt = read_uploaded_file(f)

    with open(jd_path, "rb") as f:
        jd_txt = read_uploaded_file(f)

    predict(resume_txt, jd_txt)