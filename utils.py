import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from gtts import gTTS
import os
import random
import string
from keybert import KeyBERT

# Create audio folder if it doesn't exist
os.makedirs("audio", exist_ok=True)

# GNews API Configuration
GNEWS_API_KEY = "ec4fa9e968b17549ec0ad78e970ac34e"  # Replace with your actual key
GNEWS_URL = "https://gnews.io/api/v4/search"

def fetch_news_gnews(company_name, max_articles=30, min_unique=10):
    """Fetches at least min_unique unique news articles using multiple GNews queries with pagination."""
    
    query_variations = [
        company_name, f"{company_name} Inc.", f"{company_name} Motors"
    ]

    params = {
        "token": GNEWS_API_KEY,
        "lang": "en",
        "max": 10,            # Fetch max articles per page (API limit)
        "page": 1
    }

    articles = []
    seen_titles = set()

    try:
        for query in query_variations:
            params["q"] = query

            # Use pagination to fetch multiple pages
            while len(articles) < min_unique:
                response = requests.get(GNEWS_URL, params=params, timeout=15)
                response.raise_for_status()

                data = response.json()

                if "articles" not in data or not data["articles"]:
                    print(f"No more articles found for {query} on page {params['page']}")
                    break

                for article in data["articles"]:
                    title = article.get("title", "No title")
                    summary = article.get("description", "No summary")

                    # Skip duplicates
                    if title in seen_titles or summary in seen_titles:
                        continue

                    seen_titles.add(title)
                    seen_titles.add(summary)

                    articles.append({
                        "title": title,
                        "summary": summary,
                        "url": article.get("url"),
                        "published": article.get("publishedAt")
                    })

                    # Stop once you reach the required number of unique articles
                    if len(articles) >= min_unique:
                        print(f"✅ Fetched {len(articles)} unique articles.")
                        return articles

                # Move to the next page
                params["page"] += 1

        print(f"⚠️ Returning {len(articles)} unique articles.")
        return articles

    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def perform_sentiment_analysis(articles):
    """Performs sentiment and comparative analysis."""
    analyzer = SentimentIntensityAnalyzer()
    kw_model = KeyBERT()

    valid_articles = []
    sentiments = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        sentiment_score = analyzer.polarity_scores(article['summary'])

        if sentiment_score['compound'] >= 0.05:
            sentiment = "Positive"
        elif sentiment_score['compound'] <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        sentiments[sentiment] += 1

        # Extracting topics with KeyBERT
        topics = kw_model.extract_keywords(
            article['summary'],
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=3
        )

        topic_list = [t[0] for t in topics]

        valid_articles.append({
            "title": article['title'],
            "summary": article['summary'],
            "sentiment": sentiment,
            "topics": topic_list,
            "url": article['url']
        })

    # Comparative Analysis
    comparative_analysis = {
        "Sentiment Distribution": sentiments,
        "Coverage Differences": [],
        "Topic Overlap": {}
    }

    # Add comparative differences
    for i in range(len(valid_articles) - 1):
        comparison = f"Article {i + 1} vs. Article {i + 2}"

        # Dynamic coverage difference description
        impact = (
            f"Article {i + 1} focuses on {', '.join(valid_articles[i]['topics'])}, "
            f"while Article {i + 2} covers {', '.join(valid_articles[i + 1]['topics'])}. "
            f"The sentiment difference is {valid_articles[i]['sentiment']} vs. {valid_articles[i + 1]['sentiment']}."
        )

        comparative_analysis["Coverage Differences"].append({
            "Comparison": comparison,
            "Impact": impact
        })

    return valid_articles, comparative_analysis

def generate_hindi_tts(text):
    """Generates Hindi TTS from the provided text."""
    tts = gTTS(text=text, lang='hi')
    
    # Generate a unique filename
    filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + ".mp3"
    filepath = f"audio/{filename}"
    
    tts.save(filepath)
    return filepath
