import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Matching", layout="wide")

# Sécurité : si l'utilisateur arrive directement ici sans calcul
if "matching_result" not in st.session_state:
    st.warning("Aucun résultat disponible. Veuillez lancer un calcul depuis la page principale.")
    if st.button("← Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

result = st.session_state["matching_result"]
resume_name = st.session_state.get("resume_name", "CV")
job_name = st.session_state.get("job_name", "Offre")

# =========================
# CSS custom inspiré de base.html
# =========================
st.markdown("""
<style>
    .main {
        background-color: #f6f7fb;
    }

    .topbar {
        background: white;
        padding: 14px 24px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }

    .page-subtitle {
        color: #6b7280;
        margin-top: 4px;
        font-size: 14px;
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #3b82f6;
    }

    .section-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        margin-top: 16px;
    }

    .section-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 10px;
        color: #111827;
    }

    .pill {
        display: inline-block;
        padding: 6px 12px;
        margin: 4px 6px 4px 0;
        border-radius: 999px;
        background: #eef2ff;
        color: #3730a3;
        font-size: 13px;
        font-weight: 600;
    }

    .pill-missing {
        background: #fee2e2;
        color: #991b1b;
    }

    .sidebar-fake {
        background: #111827;
        color: white;
        padding: 24px 18px;
        border-radius: 18px;
        min-height: 80vh;
    }

    .sidebar-title {
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 24px;
    }

    .sidebar-link {
        padding: 10px 12px;
        border-radius: 10px;
        margin-bottom: 10px;
        background: rgba(255,255,255,0.06);
    }

    .small-muted {
        color: #6b7280;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Header
# =========================
st.markdown("""
<div class="topbar">
    <div>
        <p class="page-title">Dashboard Matching</p>
        <p class="page-subtitle">Indicateurs et analyse du matching CV / offre</p>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# Layout principal
# =========================


c1, c2, c3 = st.columns(3)

similarity_score = result.get("similarity_score", 0)
jd_skills = result.get("jd_skills", [])
cv_skills = result.get("cv_skills", [])
missing = result.get("missing", [])

with c1:
    st.metric("Score de matching", similarity_score)

with c2:
    st.metric("Nb compétences offre", len(jd_skills))

with c3:
    st.metric("Nb compétences manquantes", len(missing))

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Informations fichiers</div>", unsafe_allow_html=True)
st.write(f"**CV :** {resume_name}")
st.write(f"**Offre :** {job_name}")
st.markdown("</div>", unsafe_allow_html=True)

col_a, col_b = st.columns(2, gap="large")

with col_a:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>💼 Compétences de l'offre</div>", unsafe_allow_html=True)
    if jd_skills:
        for skill in jd_skills:
            st.markdown(f"<span class='pill'>{skill}</span>", unsafe_allow_html=True)
    else:
        st.write("Aucune compétence détectée.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📄 Compétences du CV</div>", unsafe_allow_html=True)
    if cv_skills:
        for skill in cv_skills:
            st.markdown(f"<span class='pill'>{skill}</span>", unsafe_allow_html=True)
    else:
        st.write("Aucune compétence détectée.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>❌ Compétences manquantes</div>", unsafe_allow_html=True)
if missing:
    for skill in missing:
        st.markdown(f"<span class='pill pill-missing'>{skill}</span>", unsafe_allow_html=True)
else:
    st.success("Aucune compétence manquante détectée.")
st.markdown("</div>", unsafe_allow_html=True)

# Zone placeholder pour futurs graphiques
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📊 Zone graphiques</div>", unsafe_allow_html=True)

df = pd.DataFrame({
    "Catégorie": ["Compétences offre", "Compétences CV", "Compétences manquantes"],
    "Valeur": [len(jd_skills), len(cv_skills), len(missing)]
})
st.bar_chart(df.set_index("Catégorie"))

st.caption("Tu pourras remplacer ce graphique par ceux que tu veux.")
st.markdown("</div>", unsafe_allow_html=True)

if st.button("← Retour à l'accueil"):
    st.switch_page("app.py")