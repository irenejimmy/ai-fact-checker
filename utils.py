import re
import requests
from difflib import SequenceMatcher

API_KEY = "95f3f1aa91ee4621a4b8cba7cfbab0a5"

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

    if len(keywords) < 2:
        return text[:60]

    return " ".join(keywords[:6])


# ---------------------------
# 2. NEWS FETCHER
# ---------------------------
def get_news(query):

    url = "https://newsapi.org/v2/everything"

    search_query = build_query(query)

    params = {
        "q": search_query,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 5,
        "searchIn": "title,description",
        "apiKey": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as e:
        print("API ERROR:", e)
        return []

    print("SEARCH QUERY:", search_query)
    print("ARTICLES FOUND:", len(data.get("articles", [])))

    if data.get("status") != "ok":
        return []

    return data.get("articles", [])


# ---------------------------
# 3. SIMILARITY
# ---------------------------
def get_similarity(text1, text2):
    return SequenceMatcher(
        None,
        text1.lower(),
        text2.lower()
    ).ratio()


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

    best_score = 0
    best_article = None

    for article in articles:

        text = " ".join(filter(None, [
            article.get("title"),
            article.get("description"),
            article.get("content")
        ]))

        score = get_similarity(claim, text)

        if score > best_score:
            best_score = score
            best_article = article

    if best_score >= 0.65:
        verdict = "✅ Supported by Evidence"
        explanation = "Strong match found in news."

    elif best_score >= 0.40:
        verdict = "🟡 Partially Supported"
        explanation = "Some related news found."

    else:
        verdict = "❌ Not Supported"
        explanation = "No strong evidence found."

    return {
        "verdict": verdict,
        "score": round(best_score * 100, 2),
        "explanation": explanation,
        "best_title": best_article.get("title"),
        "best_source": best_article.get("source", {}).get("name"),
        "best_url": best_article.get("url")
    }, articles


# ---------------------------
# TEST
# ---------------------------
if __name__ == "__main__":

    claim = input("Enter a claim: ")

    result, articles = fact_check(claim)

    print("\nVerdict:", result["verdict"])
    print("Score:", result["score"])
    print("Explanation:", result["explanation"])

    if result.get("best_title"):
        print("\nBest Match")
        print("Title :", result["best_title"])
        print("Source:", result["best_source"])
        print("URL   :", result["best_url"])
