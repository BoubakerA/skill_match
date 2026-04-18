from matcher import compute_match_score

cv = ["Python", "SQL", "Docker"]
job = ["Python", "FastAPI", "SQL"]

result = compute_match_score(cv, job)

print(result)