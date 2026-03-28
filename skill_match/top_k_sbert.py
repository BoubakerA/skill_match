from sklearn.metrics.pairwise import cosine_similarity

def top_k_sbert(cv_index, cv_embeddings, jd_embeddings, k=5):
    cv_vec = cv_embeddings[cv_index].reshape(1, -1)
    sims = cosine_similarity(cv_vec, jd_embeddings)[0]
    top_idx = sims.argsort()[::-1][:k]
    return list(zip(top_idx, sims[top_idx]))
