import re
import requests
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

API_KEY = "95f3f1aa91ee4621a4b8cba7cfbab0a5"

model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------------------
# 1. QUERY BUILDER
# ---------------------------
def build_query(text):

    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    words = text.split()

    stopwords = {
        "is","are","was","were","the","a","an","and","or","of","to",
        "in","on","for","with","has","have","had","this","that","it",
        "will","be","by","as","from","ai","has","have"
    }

    keywords = [w for w in words if w not in stopwords]

    # 🔥 fallback logic
    if len(keywords) < 2:
        return text[:60]

    return " ".join(keywords[:6])

# ---------------------------
# 2. NEWS FETCHER (MUST BE ABOVE fact_check)
# ---------------------------
def get_news(query):

    url = "https://newsapi.org/v2/everything"

    search_query = build_query(query)

    params = {
    "q": search_query,
    "language": "en",
    "sortBy": "publishedAt",   # 🔥 change this
    "pageSize": 20,
    "searchIn": "title",
    "apiKey": API_KEY
}

    response = requests.get(url, params=params)
    data = response.json()

    print("SEARCH QUERY:", search_query)

    if data.get("status") != "ok":
        print("API ERROR:", data)
        return []

    return data.get("articles", [])
    print("FINAL QUERY:", search_query)
    print("RESPONSE STATUS:", data.get("status"))
    print("ARTICLES FOUND:", len(data.get("articles", [])))


# ---------------------------
# 3. SIMILARITY
# ---------------------------
def get_similarity(text1, text2):

    emb = model.encode([text1, text2], normalize_embeddings=True)
    return cosine_similarity([emb[0]], [emb[1]])[0][0]


# ---------------------------
# 4. FACT CHECK ENGINE
# ---------------------------
def fact_check(claim):

    articles = get_news(claim)

    if not articles:
        return {
            "verdict": "⚠ Insufficient Evidence",
            "score": 0,
            "explanation": "No matching news articles found."
        }, []

    scores = []
    best_article = None
    best_score = -1

    for a in articles:

        text = (a.get("title") or "") + " " + (a.get("description") or "")

        score = get_similarity(claim, text)
        scores.append(score)

        if score > best_score:
            best_score = score
            best_article = a

    avg_score = np.mean(scores)

    if avg_score > 0.60:
        verdict = "✅ Supported by Evidence"
        explanation = "Strong match found in multiple news sources."

    elif avg_score > 0.40:
        verdict = "🟡 Partially Supported"
        explanation = "Some related news found but not strong confirmation."

    else:
        verdict = "❌ Not Supported"
        explanation = "No strong evidence found."

    return {
        "verdict": verdict,
        "score": round(avg_score * 100, 2),
        "explanation": explanation,
        "best_title": best_article["title"] if best_article else None,
        "best_source": best_article["source"]["name"] if best_article else None,
        "best_url": best_article["url"] if best_article else None
    }, articles