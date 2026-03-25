# preprocessing_cv.py

import pandas as pd

def ensure_list(x):
    """
    Garantit que la valeur est une liste. Si NaN ou None, retourne une liste vide.
    """
    if isinstance(x, list):
        return x
    if pd.isna(x):
        return []
    return []

def safe_join(lst, sep):
    """
    Joint une liste d'éléments en une chaîne de caractères, en ignorant les NaN.
    """
    if not lst:
        return ""
    clean = [str(x) for x in lst if pd.notna(x)]
    return sep.join(clean)

def build_cv(row):
    """
    Construit un texte unique pour un CV à partir des colonnes :
    'skills', 'abilities', 'education', 'experience'.
    """
    skills = safe_join(row.get("skills", []), ", ")
    abilities = safe_join(row.get("abilities", []), ", ")
    education = safe_join(row.get("education", []), "; ")
    experience = safe_join(row.get("experience", []), "; ")

    text = ""

    if skills:
        text += f"Skills: {skills}. "
    if abilities:
        text += f"Abilities: {abilities}. "
    if experience:
        text += f"Experience: {experience}. "
    if education:
        text += f"Education: {education}. "

    if text.strip() == "":
        text = "No information available."

    return text.strip()
