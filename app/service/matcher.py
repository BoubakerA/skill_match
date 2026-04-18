def normalize_skills(skills: list[str]) -> set[str]:
    return {skill.strip().lower() for skill in skills if skill.strip()}


def compute_match_score(cv_skills: list[str], job_skills: list[str]) -> dict:
    cv_set = normalize_skills(cv_skills)
    job_set = normalize_skills(job_skills)

    matched = cv_set & job_set
    missing = job_set - cv_set

    if len(job_set) == 0:
        score = 0
    else:
        score = round((len(matched) / len(job_set)) * 100, 2)

    return {
        "score": score,
        "matched_skills": list(matched),
        "missing_skills": list(missing)
    }

