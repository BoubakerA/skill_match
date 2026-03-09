import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"  

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
        with st.spinner("Analyse en cours..."):
            response = requests.get(
                f"{API_URL}/predict",
                params={"resume": resume, "job": job}
            )
            print(response.status_code)
            print(response.text)
            result = response.json()
            st.metric("Score de matching", result)