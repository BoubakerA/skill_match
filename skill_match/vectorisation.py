def vectorize_texts(cv_texts, jd_texts, max_features=50000):
    from sklearn.feature_extraction.text import TfidfVectorizer

    all_texts = cv_texts + jd_texts
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    cv_tfidf = tfidf_matrix[:len(cv_texts)]
    jd_tfidf = tfidf_matrix[len(cv_texts):]
    return cv_tfidf, jd_tfidf, vectorizer
