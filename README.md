# 🎯 skill_match

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

<a target="_blank" href="https://github.com/BoubakerA/skill_match/actions/workflows/test.yml">
  <img src="https://github.com/BoubakerA/skill_match/actions/workflows/test.yml/badge.svg" alt="testing" />
</a>


> Match your resume to a job offer in one click — powered by LLM embeddings and NER skill extraction.

> ⚠️ This app is designed for **English documents only**. Results may be inaccurate for other languages.

---

## Authors

- Roger Kouakou
- Moumy Sokhna Touré
- Oumalheir Souley Na Lado
- Boubaker Asaadi
- Habib Karamoko

---

## Overview

Scrolling through LinkedIn and skimming job offers is a time-consuming reality for students. **skill_match** solves this by computing the compatibility between a resume and a job offer in a single click.

The app combines two complementary approaches:

- An **LLM embedding model** to measure semantic similarity in latent space between the resume and the job offer.
- A **Named Entity Recognition (NER)** model to extract skills from both documents and identify what is present or missing from the resume.

---

## Live Access

| | URL |
|---|---|
| **Web app** | https://skill-match.lab.sspcloud.fr |
| **REST API** | https://skill-match.lab.sspcloud.fr/api |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| ML models | LLM embeddings + NER |
| Containerization | Docker |
| Orchestration | Kubernetes |
| Continuous deployment | ArgoCD |

---

## Deployment

The app is deployed on **Kubernetes** via **ArgoCD** using a public image hosted on Docker Hub. Kubernetes manifests are located in the `deployment/` folder and managed with **Kustomize**.

```bash
kubectl apply -k deployment/
```

---

## Project Structure

```
skill_match/
├── app/
│   ├── api.py
│   ├── app.py
│   └── pages/
│       └── dashboard.py
├── data/
├── deployment/
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── ingress.yaml
│   ├── kustomization.yaml
│   ├── ui-deployment.yaml
│   └── ui-service.yaml
├── notebooks/
│   └── nlp_final.ipynb
├── skill_match/
│   ├── __init__.py
│   ├── predict.py
│   └── utils.py
├── tests/
│   ├── cv.txt
│   ├── jd.txt
│   └── test_data.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## Getting Started

### Install dependencies

```bash
pip install -e .
```

### Run the API

```bash
uvicorn app.api:app --reload
```

### Run the UI

```bash
streamlit run app/app.py
```

### Run tests

```bash
pytest tests/
```
