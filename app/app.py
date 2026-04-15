import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import os
import requests
import streamlit as st
from skill_match.utils import read_uploaded_file

API_URL = os.getenv("API_URL", "http://localhost:8000/api")

st.set_page_config(page_title="Matching Compétences")

st.title("🎯 Matching Compétences")
st.write("Comparez un CV avec une offre d'emploi")

resume = st.file_uploader(
    "Upload resume", accept_multiple_files=False, type=["txt", "pdf"])
job = st.file_uploader(
    "Upload job offer", accept_multiple_files=False, type=["txt", "pdf"])


if st.button("Calculer le matching", use_container_width=True):
    if not resume or not job:
        st.warning("Veuillez remplir les deux champs.")
    else:
        resume_text = read_uploaded_file(resume)
        job_text = read_uploaded_file(job)

        print(f"resume_text: {resume_text}")
        print(f"job_text: {job_text}")
        with st.spinner("Analyse en cours..."):
            response = requests.get(
                f"{API_URL}/predict",
                params={"resume": resume_text, "job": job_text}
            )
            response.raise_for_status()
            result = response.json()

        # Stockage des données pour la page de dashboard
        st.session_state["matching_result"] = result
        st.session_state["resume_name"] = resume.name
        st.session_state["job_name"] = job.name

        # Redirection vers la page de dashboard
        st.switch_page("pages/dashboard.py")
