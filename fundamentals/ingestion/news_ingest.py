import requests
from datetime import date
from textblob import TextBlob
from sqlalchemy import text
from database.engine import engine
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # NEWS_API_KEY   # put in .env later
BASE_URL = "https://newsapi.org/v2/top-headlines"


def get_sentiment(title: str):
    blob = TextBlob(title)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        label = "POSITIVE"
    elif polarity < -0.1:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"

    return polarity, label


def fetch_market_news():
    params = {
        "category": "business",
        "language": "en",
        "apiKey": NEWS_API_KEY,
        "pageSize": 50
    }
    return requests.get(BASE_URL, params=params).json()


def fetch_stock_news(symbol):
    params = {
        "q": symbol,
        "language": "en",
        "apiKey": NEWS_API_KEY,
        "pageSize": 10
    }
    return requests.get("https://newsapi.org/v2/everything", params=params).json()


def insert_news(trade_date, symbol, title, source, score, label):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO news_headlines
                (trade_date, symbol, title, source, sentiment_score, sentiment_label)
                VALUES
                (:trade_date, :symbol, :title, :source, :score, :label)
            """),
            {
                "trade_date": trade_date,
                "symbol": symbol,
                "title": title,
                "source": source,
                "score": score,
                "label": label
            }
        )


def run_news_ingest():
    today = date.today()

    # 1️⃣ Market-wide news
    data = fetch_market_news()
    for article in data.get("articles", []):
        title = article["title"]
        source = article["source"]["name"]
        score, label = get_sentiment(title)
        insert_news(today, None, title, source, score, label)

    # 2️⃣ Stock-specific news (NIFTY50 only)
    with engine.connect() as conn:
        symbols = conn.execute(
            text("""
                SELECT symbol FROM symbols_master
                WHERE index_name = 'NIFTY50'
            """)
        ).fetchall()

    for (symbol,) in symbols:
        data = fetch_stock_news(symbol)
        for article in data.get("articles", []):
            title = article["title"]
            source = article["source"]["name"]
            score, label = get_sentiment(title)
            insert_news(today, symbol, title, source, score, label)

    print("✅ News ingestion complete")


if __name__ == "__main__":
    run_news_ingest()
