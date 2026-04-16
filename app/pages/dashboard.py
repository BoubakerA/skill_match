import streamlit as st
import plotly.graph_objects as go
import html

result = st.session_state.get("matching_result", None)

if not result:
    st.warning("No results found. Please restart the analysis from the main page.")
    st.stop()

job_skills = result.get("jd_skills", [])
matching_score = result.get("similarity_score", 0)
cv_skill_matches = result.get("present", [])
missing_job_skills = result.get("missing", [])

cv_skill_matches = [
    {"skill": s, "status": "match"} for s in cv_skill_matches
]
# -----------------------------
# CSS Power BI style
# -----------------------------
st.markdown("""
<style>
    /* App globale */
    .stApp {
        background-color: #f3f4f6;
    }

    .block-container {
        max-width: 100%;
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
    }

    /* Masquer éléments Streamlit */
    header[data-testid="stHeader"] {
        display: none;
    }

    section[data-testid="stSidebar"] {
        display: block;
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* Colonnes */
    div[data-testid="column"] > div {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px 22px 18px 22px;
        min-height: 88vh;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
        display: flex;
        flex-direction: column;
    }

    /* Titres */
    .page-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1rem;
        padding-left: 0.15rem;
    }

    .section-title {
        font-size: 1.08rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.9rem;
    }

    .sub-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #374151;
        margin-top: 1.1rem;
        margin-bottom: 0.55rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .section-text {
        color: #6b7280;
        font-size: 0.93rem;
        line-height: 1.6;
    }

    /* KPI */
    .kpi-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 14px 16px;
        margin-top: 0.75rem;
        text-align: center;
    }

    .kpi-label {
        color: #6b7280;
        font-size: 0.85rem;
        margin-bottom: 0.25rem;
    }

    .kpi-value {
        color: #111827;
        font-size: 1.4rem;
        font-weight: 700;
    }

    /* Tags */
    .tags-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 0.35rem;
    }

    .skill-tag {
        display: inline-block;
        background: #eef2ff;
        color: #3730a3;
        padding: 7px 11px;
        border-radius: 999px;
        font-size: 0.87rem;
        font-weight: 600;
        border: 1px solid #e0e7ff;
    }

    /* Lignes compétences */
    .skill-list {
        margin-top: 0.3rem;
    }

    .skill-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #f3f4f6;
    }

    .skill-left {
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 0;
    }

    .skill-icon {
        width: 20px;
        text-align: center;
        font-size: 0.98rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .icon-match {
        color: #16a34a;
    }

    .icon-partial {
        color: #eab308;
    }

    .icon-missing {
        color: #dc2626;
    }

    .skill-text {
        color: #111827;
        font-size: 0.95rem;
    }

    .skill-text-missing {
        color: #9ca3af;
        font-size: 0.95rem;
    }

    .legend-box {
        margin-top: 1rem;
        padding: 12px 14px;
        border-radius: 12px;
        background: #f9fafb;
        border: 1px solid #e5e7eb;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #4b5563;
        font-size: 0.88rem;
        margin: 4px 0;
    }

    /* Plotly */
    div[data-testid="stPlotlyChart"] {
        margin-top: 0.25rem;
        margin-bottom: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Jauge
# -----------------------------
def gauge_chart(value: float):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={
                "suffix": "%",
                "font": {"size": 42, "color": "#111827"}
            },
            title={
                "text": "Resume / Job Match",
                "font": {"size": 22, "color": "#111827"}
            },
            gauge={
                "shape": "angular",
                "axis": {
                    "range": [0, 100],
                    "tickmode": "array",
                    "tickvals": [0, 25, 50, 75, 100],
                    "ticktext": ["0", "25", "50", "75", "100"],
                    "tickwidth": 1,
                    "tickcolor": "#9ca3af",
                    "tickfont": {"color": "#6b7280", "size": 12}
                },
                "bar": {"color": "#111827", "thickness": 0.22},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "#ef4444"},
                    {"range": [40, 70], "color": "#f59e0b"},
                    {"range": [70, 100], "color": "#22c55e"},
                ],
                "threshold": {
                    "line": {"color": "#111827", "width": 4},
                    "thickness": 0.75,
                    "value": value,
                }
            }
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=70, b=10),
        height=360,
    )
    return fig

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="page-title">Matching Dashboard</div>', unsafe_allow_html=True)
st.markdown('<br><br><br>', unsafe_allow_html=True)

# -----------------------------
# Layout 3 colonnes
# -----------------------------
col1, col2, col3 = st.columns([1.30, 1.05, 1.0], gap="large", vertical_alignment="top")


with col1:
    st.markdown('<div class="section-title">Overall Score</div>', unsafe_allow_html=True)
    st.plotly_chart(gauge_chart(matching_score), use_container_width=True)

    st.markdown("""
        <div class="legend-box">
            <div class="legend-item"><span style="color:#ef4444;">●</span> Low match</div>
            <div class="legend-item"><span style="color:#f59e0b;">●</span> Moderate match</div>
            <div class="legend-item"><span style="color:#22c55e;">●</span> Strong Match </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-title">Job Offer Requirements</div>', unsafe_allow_html=True)

    skills_html = "".join([f'<span class="skill-tag">{skill}</span>' for skill in job_skills])
    st.markdown(f'<div class="tags-wrap">{skills_html}</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="legend-box">
            <div class="legend-item">All skills and requirements identified from the job offer</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown('<div class="section-title">Resume Skills Analysis</div>', unsafe_allow_html=True)

    st.markdown('<div class="sub-title">Skills Found in Resume</div>', unsafe_allow_html=True)

    for item in cv_skill_matches:
        col_icon, col_text = st.columns([0.1, 0.9])

        with col_icon:
            if item["status"] == "match":
                st.markdown('<span class="icon-match">✔</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="icon-partial">▬</span>', unsafe_allow_html=True)

        with col_text:
            st.markdown(
                f'''
                <div style="padding: 0 0 10px 0; border-bottom: 1px solid #f3f4f6;">
                    <span class="skill-text">{item["skill"]}</span>
                </div>
                ''',
                unsafe_allow_html=True
            )

    st.markdown('<div class="sub-title">Missing Skills</div>', unsafe_allow_html=True)

    for skill in missing_job_skills:
        col_icon, col_text = st.columns([0.1, 0.9])

        with col_icon:
            st.markdown('<span class="icon-missing">✘</span>', unsafe_allow_html=True)

        with col_text:
            st.markdown(
                f'''
                <div style="padding: 0 0 10px 0; border-bottom: 1px solid #f3f4f6;">
                    <span class="skill-text-missing">{skill}</span>
                </div>
                ''',
                unsafe_allow_html=True
            )