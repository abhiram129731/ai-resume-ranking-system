from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_resumes(resumes, job_desc):
    documents = resumes + [job_desc]

    tfidf = TfidfVectorizer(ngram_range=(1,2))
    vectors = tfidf.fit_transform(documents)

    job_vector = vectors[-1]
    resume_vectors = vectors[:-1]

    scores = cosine_similarity(resume_vectors, job_vector)

    return scores.flatten()
