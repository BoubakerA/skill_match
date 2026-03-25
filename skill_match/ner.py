#

from huggingface_hub import snapshot_download
import spacy

# 1️⃣ Charger le modèle NER (à appeler une fois dans le notebook)
def load_skill_ner(model_name="amjad-awad/skill-extractor"):
    model_path = snapshot_download(model_name, repo_type="model")
    nlp = spacy.load(model_path)
    return nlp

# 2️⃣ Extraire les compétences d'un texte
def extract_skills(text, nlp):
    """
    text : str, texte de JD ou CV
    nlp : modèle spaCy NER
    return : liste de compétences détectées (lowercase)
    """
    doc = nlp(text)
    return [ent.text.lower() for ent in doc.ents if "SKILL" in ent.label_]

# 3️⃣ Normaliser les compétences d'une liste de skills CV
def normalize_skills(skills_list):
    """
    skills_list : liste ou None
    return : set de skills en lowercase
    """
    return set([s.lower() for s in skills_list if s])

# 4️⃣ Comparer compétences CV et JD
def compare_skills(cv_idx, jd_idx, cv_skills_sets, jd_skills_lists):
    """
    cv_idx : index du CV
    jd_idx : index de la JD
    cv_skills_sets : liste de sets de skills CV
    jd_skills_lists : liste de lists de skills JD
    return : dict {'present': [...], 'missing': [...]}
    """
    cv_sk = cv_skills_sets[cv_idx]
    jd_sk = set(jd_skills_lists[jd_idx])

    present = cv_sk & jd_sk
    missing = jd_sk - cv_sk

    return {"present": sorted(list(present)), "missing": sorted(list(missing))}
