# ---------------- Bibliothèques ----------------
import re
import pandas as pd
from pathlib import Path
import PyPDF2
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# ----------------------
def preprocess_text(text: str) -> str:
    """
    Nettoie un texte : minuscules, supprime chiffres et caractères spéciaux.
    """
    text = text.lower()
    text = re.sub(r'[^a-z]', ' ', text)
    text = re.sub(r'\d+', '', text)
    return ' '.join(text.split())

# ----------------------------

def load_cv_csv(csv_path: str, clean: bool = True) -> pd.DataFrame:
    """
    Charge un CSV contenant une colonne 'cv_text' et renvoie un DataFrame prêt pour NLP.
    """
    df = pd.read_csv(csv_path)

    # S'assurer qu'il n'y a pas de NaN
    df['cv_text'] = df['cv_text'].fillna("")

    if clean:
        df['cv_text'] = df['cv_text'].apply(preprocess_text)

    return df

# ----------------------
def prepare_jobs(jobs: pd.DataFrame, clean: bool = True) -> pd.DataFrame:
    selected_columns = [
        "Job Title", "Job Description", "skills", "Role",
        "Responsibilities", "Qualifications", "Company"
    ]

    jobs_precis = jobs[selected_columns].copy()

    jobs_precis["job_text"] = (
        jobs_precis["Job Title"].fillna("") + " " +
        jobs_precis["Job Description"].fillna("") + " " +
        jobs_precis["skills"].fillna("") + " " +
        jobs_precis.get("Role", "").fillna("") + " " +
        jobs_precis.get("Responsibilities", "").fillna("") + " " +
        jobs_precis.get("Qualifications", "").fillna("") + " " +
        jobs_precis.get("Company", "").fillna("")
    )

    if clean:
        jobs_precis["job_text"] = jobs_precis["job_text"].apply(preprocess_text)

    return jobs_precis
# ----------------------
def load_cv_folder(folder_path: str, clean: bool = True) -> pd.DataFrame:
    cv_folder = Path(folder_path).expanduser()
    cv_data = []
    for file_path in cv_folder.rglob("*.pdf"):
        try:
            pdf = PyPDF2.PdfReader(str(file_path))
            text = "".join([page.extract_text() or "" for page in pdf.pages])
            if clean:
                text = preprocess_text(text)
            category = file_path.parent.name
            cv_data.append({
                "cv_path": str(file_path),
                "cv_text": text,
                "category": category
            })
        except Exception as e:
            print(f"Erreur PDF {file_path}: {e}")
    return pd.DataFrame(cv_data)

# ----------------------
def create_tagged_documents(jobs_df: pd.DataFrame, cv_df: pd.DataFrame):
    tagged_jobs = [TaggedDocument(words=text.split(), tags=[f'JOB_{i}'])
                   for i, text in enumerate(jobs_df['job_text'])]
    tagged_cvs = [TaggedDocument(words=text.split(), tags=[f'CV_{i}'])
                  for i, text in enumerate(cv_df['cv_text'])]
    return tagged_jobs, tagged_cvs

# ----------------------
def train_doc2vec(tagged_documents, vector_size=100, window=5, min_count=2, workers=4, epochs=40):
    """
    Entraîne un modèle Doc2Vec sur une liste de TaggedDocument.
    """
    model = Doc2Vec(vector_size=vector_size, window=window, min_count=min_count,
                    workers=workers, epochs=epochs)
    model.build_vocab(tagged_documents)
    print(f"Taille du vocabulaire : {len(model.wv.key_to_index)}")
    model.train(tagged_documents, total_examples=model.corpus_count, epochs=model.epochs)
    return model

# ----------------------
def load_single_cv(file_path: str, clean: bool = True) -> str:
    pdf = PyPDF2.PdfReader(str(file_path))
    text = "".join([page.extract_text() or "" for page in pdf.pages])
    if clean:
        text = preprocess_text(text)
    return text

# ----------------------
def compute_matching_score(model: Doc2Vec, job_text: str, cv_text: str) -> float:
    """
    Calcule le score de similarité entre un CV et une description de job.
    """
    job_vector = model.infer_vector(job_text.split())
    cv_vector = model.infer_vector(cv_text.split())
    score = cosine_similarity([cv_vector], [job_vector])[0][0]
    return score

# ----------------------
def init_ner_pipeline(model_name: str = "Nucha/Nucha_SkillNER_BERT"):
    """
    Initialise le pipeline NER pour détecter les compétences.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    ner_pipeline = pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple"
    )
    return ner_pipeline

def extract_skills_list_clean(text: str, ner_pipeline) -> list:
    entities = ner_pipeline(text)
    skills = []
    for ent in entities:
        word = ent['word'].lower().strip()
        # Ignorer les sous-tokens BERT et les mots trop courts
        if word.startswith("##"):
            continue
        if len(word) <= 2:
            continue
        if ent['entity_group'] in ["HSKILL", "SSKILL"]:
            skills.append(word)
    # Dédoublonner
    return list(set(skills))
