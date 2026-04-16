import requests
import os
import streamlit as st
from skill_match.utils import read_uploaded_file

API_URL = os.getenv("API_URL", "http://localhost:8000/api")

def call_matching_api(resume_text: str, job_text: str) -> dict:
    response = requests.post(
        f"{API_URL}/predict",
        json={"resume": resume_text, "job": job_text},
        timeout=120
    )
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="Matching skills")

st.title("🎯 Matching Skills")
st.warning("⚠️ This app is designed for English documents only. Results may be inaccurate for other languages.")
st.write("Analyze the fit between a resume and a job offer")

resume = st.file_uploader(
    "Upload resume", accept_multiple_files=False, type=["txt", "pdf"])
job = st.file_uploader(
    "Upload job offer", accept_multiple_files=False, type=["txt", "pdf"])


if st.button("Compute the matching", use_container_width=True):
    if not resume or not job:
        st.warning("Please fill in both fields.")
    else:
        resume_text = read_uploaded_file(resume)
        job_text = read_uploaded_file(job)

        st.info("⏳ This may take a few minutes depending on document length.")
        with st.spinner("Analyzing documents... Please wait"):
            try:
                result = call_matching_api(resume_text, job_text) 
            except requests.exceptions.ConnectionError:
                st.error("Unable to reach the API. Please check that it is running.")
                st.stop()
            except requests.exceptions.HTTPError as e:
                st.error(f"API error : {e.response.status_code}")
                st.stop()
        # Stockage des données pour la page de dashboard
        st.session_state["matching_result"] = result
        st.session_state["resume_name"] = resume.name
        st.session_state["job_name"] = job.name

        # Redirection vers la page de dashboard
        st.switch_page("pages/dashboard.py")
