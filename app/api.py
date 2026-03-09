import logging
from fastapi import FastAPI


logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG,
    handlers=[logging.FileHandler("api.log"), logging.StreamHandler()],
)


app = FastAPI(
    title="Matching des compétences entre un candidat et une offre d'emploi",
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


@app.get("/predict", tags=["Predict"])
async def predict(resume: str, job: str) -> float:
    """
    Match a resume against a job description.
    """
    # score = model.predict(resume, job)
    score = 0.9
    return score