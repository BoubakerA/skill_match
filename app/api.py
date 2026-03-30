import logging
from fastapi import FastAPI

from pydantic import BaseModel
from typing import List

class MatchResponse(BaseModel):
    similarity_score: float
    cv_skills: List[str]
    jd_skills: List[str]
    present: List[str]
    missing: List[str]

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG,
    handlers=[logging.FileHandler("api.log"), logging.StreamHandler()],
)


app = FastAPI(
    title="Matching des compétences entre un candidat et une offre d'emploi",
    root_path="/api",
    description=
    "Application de matching des compétences entre un candidat et une offre d'emploi." +\
        "<br><br><img src=\"https://www.mykonekti.fr/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fpuzzle.9ccecc64.png&w=3840&q=75\" width=\"200\">"
    )


@app.get("/", tags=["Welcome"])
def show_welcome_page():
    """
    Show welcome page.
    """

    return {
        "Message": "API de matching des compétences entre un candidat et une offre d'emploi",
        "Model_name": 'Skill Match ML',
        "Model_version": "0.1",
    }


@app.get("/predict", tags=["Predict"], response_model=MatchResponse)
async def predict(resume: str, job: str) -> MatchResponse:
    """
    Match a resume against a job description.
    """
    from skill_match.predict import predict as predict_fn
    resutls = predict_fn(resume, job)
    return resutls
