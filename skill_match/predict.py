from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity 
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


def extract_skills(text, ner_pipeline):
    """Extrait les compétences via Nucha_SkillNER_BERT en découpant par phrases"""
    lines = str(text).split("\n")
    all_skills = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        entities = ner_pipeline(line[:512])
        skills = [
            e["word"].lower().strip()
            for e in entities
            if e["entity_group"] in ("HSKILL", "SSKILL")
            and e["score"] >= 0.7
        ]
        all_skills.extend(skills)
    return list(set(all_skills))


def compare_skills(cv_skills, jd_skills):
    """Compare les compétences d'un CV avec celles d'une offre d'emploi"""
    cv_set = set(s.lower().strip() for s in cv_skills)
    jd_set = set(s.lower().strip() for s in jd_skills)

    present = cv_set & jd_set
    missing = jd_set - cv_set

    return {
        "cv_skills": sorted(cv_set),
        "jd_skills": sorted(jd_set),
        "present": sorted(present),
        "missing": sorted(missing),
    }


def match_cv_jd(cv_text, jd_text, ner_pipeline, embedding_model):
    ner = ner_pipeline

    jd_emb = embedding_model.encode([jd_text])
    cv_emb = embedding_model.encode([cv_text])
    score = cosine_similarity(cv_emb, jd_emb)[0][0]

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
    cv_text, jd_text = "Data scientist Python Java English", "Data Science Python C R"
    results = predict(cv_text, jd_text)
