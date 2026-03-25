from sklearn.metrics.pairwise import cosine_similarity

def top_k_tfidf(cv_index, cv_tfidf, jd_tfidf, k=5):
    cv_vec = cv_tfidf[cv_index]
    sims = cosine_similarity(cv_vec, jd_tfidf)[0]
    top_idx = sims.argsort()[::-1][:k]
    return list(zip(top_idx, sims[top_idx]))

def top_k_cv(jd_index, cv_tfidf, jd_tfidf, k=5):
    jd_vec = jd_tfidf[jd_index]
    sims = cosine_similarity(jd_vec, cv_tfidf)[0]
    top_idx = sims.argsort()[::-1][:k]
    return list(zip(top_idx, sims[top_idx]))
