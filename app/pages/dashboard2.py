import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Matching", layout="wide")

if "matching_result" not in st.session_state:
    st.warning("Aucun résultat disponible. Veuillez lancer un calcul depuis la page principale.")
    if st.button("← Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

result = st.session_state["matching_result"]
resume_name = st.session_state.get("resume_name", "CV")
job_name = st.session_state.get("job_name", "Offre")

similarity_score = result.get("similarity_score", 0)
jd_skills = result.get("jd_skills", [])
cv_skills = result.get("cv_skills", [])
missing = result.get("missing", [])
present = result.get("present", [])

# --------------------------------------------------
# CSS style Power BI
# --------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #f3f4f6;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    .dashboard-title {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    .kpi-card {
        background: white;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e7eb;
    }

    .kpi-label {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #111827;
        line-height: 1.1;
    }

    .card {
        background: white;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 8px rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e7eb;
        margin-top: 1rem;
    }

    .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.8rem;
    }

    .meta-text {
        color: #374151;
        font-size: 0.95rem;
        margin-bottom: 0.35rem;
    }

    .pill {
        display: inline-block;
        background: #eef2f7;
        color: #1f2937;
        border-radius: 999px;
        padding: 6px 10px;
        margin: 4px 6px 4px 0;
        font-size: 0.82rem;
        border: 1px solid #e5e7eb;
    }

    .pill-missing {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }

    .section-gap {
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown('<div class="dashboard-title">Matching Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-subtitle">Analyse CV vs offre d’emploi — vue synthétique</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# KPI row
# --------------------------------------------------
k1, k2, k3, k4 = st.columns(4, gap="large")

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Score de matching</div>
        <div class="kpi-value">{similarity_score}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Compétences offre</div>
        <div class="kpi-value">{len(jd_skills)}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Compétences CV</div>
        <div class="kpi-value">{len(cv_skills)}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Compétences manquantes</div>
        <div class="kpi-value">{len(missing)}</div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# Row 1
# --------------------------------------------------
col1, col2 = st.columns([1.2, 1.8], gap="large")

with col1:
    st.markdown('<div class="card-title">Informations</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card">
        <div class="meta-text"><b>CV :</b> {resume_name}</div>
        <div class="meta-text"><b>Offre :</b> {job_name}</div>
        <div class="meta-text"><b>Compétences présentes :</b> {len(present)}</div>
        <div class="meta-text"><b>Compétences manquantes :</b> {len(missing)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Compétences manquantes</div>', unsafe_allow_html=True)

    if missing:
        for skill in missing:
            st.markdown(f"<span class='pill pill-missing'>{skill}</span>", unsafe_allow_html=True)
    else:
        st.success("Aucune compétence manquante.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Vue d’ensemble</div>', unsafe_allow_html=True)

    df_overview = pd.DataFrame({
        "Catégorie": ["Compétences offre", "Compétences CV", "Présentes", "Manquantes"],
        "Valeur": [len(jd_skills), len(cv_skills), len(present), len(missing)]
    })
    st.bar_chart(df_overview.set_index("Catégorie"))

    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Row 2
# --------------------------------------------------
col3, col4 = st.columns(2, gap="large")

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Compétences de l’offre</div>', unsafe_allow_html=True)

    if jd_skills:
        for skill in jd_skills:
            st.markdown(f"<span class='pill'>{skill}</span>", unsafe_allow_html=True)
    else:
        st.write("Aucune compétence détectée.")

    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Compétences du CV</div>', unsafe_allow_html=True)

    if cv_skills:
        for skill in cv_skills:
            st.markdown(f"<span class='pill'>{skill}</span>", unsafe_allow_html=True)
    else:
        st.write("Aucune compétence détectée.")

    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Row 3
# --------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Détail des compétences présentes</div>', unsafe_allow_html=True)

if present:
    for skill in present:
        st.markdown(f"<span class='pill'>{skill}</span>", unsafe_allow_html=True)
else:
    st.write("Aucune compétence commune détectée.")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
if st.button("← Retour à l'accueil"):
    st.switch_page("app.py")