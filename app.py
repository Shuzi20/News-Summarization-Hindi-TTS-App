import streamlit as st
from utils import fetch_news_gnews, perform_sentiment_analysis, generate_hindi_tts

st.set_page_config(page_title="📰 News Summarization & Hindi TTS App", layout="wide")

st.title("📰 News Summarization & Hindi TTS App")
st.markdown("### Enter a Company Name")

# Company input
company = st.text_input("Company Name", placeholder="Enter company name (e.g., Tesla)")

if st.button("Fetch News"):
    if company.strip():
        with st.spinner("Fetching news articles..."):
            articles = fetch_news_gnews(company)

            if not articles:
                st.error("No valid articles found. Try a different company.")
            else:
                valid_articles, analysis = perform_sentiment_analysis(articles)

                st.success(f"📄 Extracted {len(valid_articles)} articles for '{company}'")

                # Show articles
                for i, article in enumerate(valid_articles, start=1):
                    st.markdown(f"### {i}. {article['title']}")
                    st.write(f"**Summary:** {article['summary']}")
                    st.write(f"**Sentiment:** {article['sentiment']}")
                    st.write(f"**Topics:** {', '.join(article['topics'])}")
                    st.write(f"[Read More]({article['url']})")
                    st.write("---")

                # Comparative analysis
                st.markdown("### 📊 Comparative Analysis")
                st.json(analysis)

                # Generate Hindi summary
                sentiment_report = analysis.get("Sentiment Distribution", {})
                hindi_summary = ""

                for sentiment, count in sentiment_report.items():
                    if sentiment == "Positive":
                        hindi_summary += f"सकारात्मक खबरों की संख्या {count} है। "
                    elif sentiment == "Negative":
                        hindi_summary += f"नकारात्मक खबरों की संख्या {count} है। "
                    elif sentiment == "Neutral":
                        hindi_summary += f"तटस्थ खबरों की संख्या {count} है। "

                tts_path = generate_hindi_tts(hindi_summary)

                st.markdown("### 🔊 Hindi TTS Output")
                audio_bytes = open(tts_path, "rb").read()
                st.audio(audio_bytes, format="audio/mp3")

    else:
        st.warning("Please enter a company name.")
