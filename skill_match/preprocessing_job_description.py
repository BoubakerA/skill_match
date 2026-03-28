# preprocessing_job_description.py

import pandas as pd
import numpy as np
import re
import string
from tqdm import tqdm
import nltk
from nltk.corpus import stopwords


nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def clean_text(text):
    """
    Nettoyage du texte :
    - passage en minuscules
    - suppression des URLs et emails
    - suppression des chiffres
    - suppression de la ponctuation
    - suppression des stopwords
    - normalisation des espaces
    """
    if pd.isna(text):
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"\d+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = " ".join([word for word in text.split() if word not in stop_words])
    text = re.sub(r"\s+", " ", text).strip()

    return text

def build_full_text(row):
    """
    Concatène les différentes colonnes pertinentes d'une offre d'emploi
    pour construire un texte complet à nettoyer.
    Colonnes prises en compte : 'Job Title', 'Job Description', 'skills', 'Responsibilities'
    """
    parts = []

    if pd.notna(row.get("Job Title")):
        parts.append(str(row["Job Title"]))

    if pd.notna(row.get("Job Description")):
        parts.append(str(row["Job Description"]))

    if pd.notna(row.get("skills")):
        parts.append(str(row["skills"]))

    if pd.notna(row.get("Responsibilities")):
        parts.append(str(row["Responsibilities"]))

    return " ".join(parts)

def enable_tqdm_pandas():
    """
    Active la progress bar tqdm pour les apply pandas.
    """
    tqdm.pandas()
