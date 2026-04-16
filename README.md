# skill_match

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

<a target="_blank" href="https://github.com/BoubakerA/skill_match/actions/workflows/test.yml">
  <img src="https://github.com/BoubakerA/skill_match/actions/workflows/test.yml/badge.svg" alt="testing" />
</a>

Web application that matches a resume to a job offer.

## Project Organization

```
├── app
│   ├── api.py
│   ├── app.py
│   └── pages
│       └── dashboard.py
├── data
├── deployment
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── ingress.yaml
│   ├── ui-deployment.yaml
│   └── ui-service.yaml
├── Dockerfile
├── docs
├── LICENSE
├── notebooks
│   └── nlp_final.ipynb
├── pyproject.toml
├── README.md
├── skill_match
│   ├── __init__.py
│   ├── predict.py
│   └── utils.py
├── tests
│   ├── cv.txt
│   ├── jd.txt
│   └── test_data.py
└── uv.lock
```

--------

