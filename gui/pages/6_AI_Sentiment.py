import streamlit as st

import streamlit as st
@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()

from pymongo import MongoClient
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Sentiment Analysis", layout="wide")
st.title("🧠 AI Sentiment Analysis")

@st.cache_data(ttl=600)
def fetch_sentiment_data():
    
    db = get_database()
    
    # We query enough metrics to visualize confidence score and distribution without iterating entire DB
    cursor = db.reviews.find(
        {"ai_sentiment_score": {"$exists": True}},
        {"reviewText": 1, "analytics.sentiment": 1, "ai_sentiment": 1, "ai_sentiment_score": 1}
    ).limit(3000)
    
    df = pd.DataFrame(list(cursor))
    if not df.empty and "_id" in df.columns:
        df.drop(columns=["_id"], inplace=True)
    return df

df = fetch_sentiment_data()

if df.empty:
    st.warning("No pre-computed AI Sentiment data found in MongoDB.")
else:
    # Rule-Based vs AI Comparison
    col1, col2 = st.columns(2)
    
    df["rule_based_sentiment"] = df["analytics"].apply(lambda x: x.get("sentiment") if isinstance(x, dict) else "unknown")
    
    with col1:
        st.subheader("Rule-Based Sentiment (Original)")
        fig_rule = px.pie(df, names="rule_based_sentiment", hole=0.3)
        st.plotly_chart(fig_rule, use_container_width=True)
        
    with col2:
        st.subheader("Distilbert AI Sentiment")
        fig_ai = px.pie(df, names="ai_sentiment", hole=0.3)
        st.plotly_chart(fig_ai, use_container_width=True)
        
    st.divider()
    
    st.subheader("AI Confidence Score Distribution")
    fig_hist = px.histogram(df, x="ai_sentiment_score", nbins=20, color="ai_sentiment")
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.divider()
    
    st.subheader("Sample Reviews & AI Scoring")
    st.dataframe(df[["reviewText", "rule_based_sentiment", "ai_sentiment", "ai_sentiment_score"]].head(100), use_container_width=True)
