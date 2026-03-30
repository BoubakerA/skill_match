import os
import requests
import streamlit as st
from skill_match.utils import read_uploaded_file



API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("🎯 Matching Compétences")
st.write("Comparez un CV avec une offre d'emploi")

resume = st.file_uploader(
    "Upload resume", accept_multiple_files=False, type="txt")
job = st.file_uploader(
    "Upload job offer", accept_multiple_files=False, type="txt")


if st.button("Calculer le matching"):
    if not resume or not job:
        st.warning("Veuillez remplir les deux champs.")
    else:
        resume_text = read_uploaded_file(resume)
        job_text = read_uploaded_file(job)

        with st.spinner("Analyse en cours..."):
            response = requests.get(
                f"{API_URL}/predict",
                params={"resume": resume_text, "job": job_text}
            )
            result = response.json()
            st.metric("Score de matching", result["similarity_score"])

            st.subheader("💼 Compétences de l'offre")
            st.write(result["jd_skills"])

            st.subheader("📄 Compétences du CV")
            st.write(result["cv_skills"])

            st.subheader("❌ Compétences manquantes")
            st.write(result["missing"])
