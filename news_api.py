import requests

API_KEY = "95f3f1aa91ee4621a4b8cba7cfbab0a5"

url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"

response = requests.get(url)
data = response.json()

for article in data["articles"]:
    print("Title:", article["title"])
    print("Source:", article["source"]["name"])
    print("Published:", article["publishedAt"])
    print("URL:", article["url"])
    print("-" * 50)