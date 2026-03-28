

import argparse
import pdfplumber
from preprocessing_job_description import clean_text
from model_nlp import match_cv_jd


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cv", type=str, default="/home/onyxia/work/skill_match/cv_test/cv_english.pdf")
    parser.add_argument("--jd", type=str, default="/home/onyxia/work/skill_match/offre_test/offre.txt")
    args = parser.parse_args()

    raw_cv_text = extract_text_from_pdf(args.cv)
    cv_text = clean_text(raw_cv_text)

    with open(args.jd, "r", encoding="utf-8") as f:
        jd_raw = f.read()

    match_cv_jd(cv_text, jd_raw)


if __name__ == "__main__":
    main()