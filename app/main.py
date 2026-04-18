from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from app.service.file_extractor import extract_text
from app.service.job_parser import parse_job_with_mistral
from app.service.llm_parser import parse_cv_with_mistral
from app.service.llm_parser import parse_cv_with_mistral
from app.service.matcher import compute_match_score
from pydantic import BaseModel


class MatchRequest(BaseModel):
    cv_skills: list[str]
    job_skills: list[str]

# ⚠️ IMPORTANT : root_path pour le proxy Onyxia
app = FastAPI(
    title="Skill Match API",
    root_path="/proxy/8001"
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root() -> dict:
    return {"message": "Skill Match API is running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    allowed_extensions = {".pdf", ".txt"}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilise un fichier PDF ou TXT."
        )

    file_path = UPLOAD_DIR / file.filename

    content = await file.read()
    file_path.write_bytes(content)

    try:
        extracted_text = extract_text(str(file_path))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'extraction du texte : {str(exc)}"
        ) from exc

    return {
        "message": "Fichier traité avec succès",
        "filename": file.filename,
        "file_type": file_extension,
        "stored_path": str(file_path),
        "extracted_text": extracted_text[:3000]
    }

@app.post("/parse-job")
async def parse_job(job_text: str):
    try:
        parsed_job = parse_job_with_mistral(job_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "message": "Job parsé avec succès",
        "parsed_job": parsed_job
    }

@app.post("/parse-cv")
async def parse_cv(file: UploadFile = File(...)) -> dict:
    file_path = UPLOAD_DIR / file.filename

    content = await file.read()
    file_path.write_bytes(content)

    try:
        extracted_text = extract_text(str(file_path))
        parsed_cv = parse_cv_with_mistral(extracted_text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "message": "CV parsé",
        "parsed_cv": parsed_cv
    }

@app.post("/parse-cv")
async def parse_cv(file: UploadFile = File(...)) -> dict:
    allowed_extensions = {".pdf", ".txt"}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilise un fichier PDF ou TXT."
        )

    file_path = UPLOAD_DIR / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    try:
        extracted_text = extract_text(str(file_path))
        parsed_cv = parse_cv_with_mistral(extracted_text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du parsing du CV : {str(exc)}"
        ) from exc

    return {
        "message": "CV parsé avec succès",
        "filename": file.filename,
        "parsed_cv": parsed_cv
    }

@app.post("/match")
def match_skills(data: MatchRequest):
    result = compute_match_score(
        cv_skills=data.cv_skills,
        job_skills=data.job_skills
    )

    return result