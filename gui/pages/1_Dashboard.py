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

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("📊 Core Dashboard")

@st.cache_data(ttl=600)
def get_dashboard_metrics():
    
    db = get_database()
    
    metrics = {
        "users": db.users.count_documents({}),
        "products": db.products.count_documents({}),
        "reviews": db.reviews.count_documents({}),
        "interactions": db.interactions.count_documents({})
    }
    
    # Simple distribution sampling
    ratings_cursor = db.reviews.aggregate([
        {"$group": {"_id": "$overall", "count": {"$sum": 1}}}
    ])
    ratings_df = pd.DataFrame(list(ratings_cursor))
    
    sentiment_cursor = db.reviews.aggregate([
        {"$group": {"_id": "$ai_sentiment", "count": {"$sum": 1}}}
    ])
    sentiment_df = pd.DataFrame(list(sentiment_cursor))
    
    return metrics, ratings_df, sentiment_df

metrics, ratings_df, sentiment_df = get_dashboard_metrics()

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Users", metrics["users"])
col2.metric("Total Products", metrics["products"])
col3.metric("Total Reviews", metrics["reviews"])
col4.metric("Total Interactions", metrics["interactions"])

st.divider()

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.subheader("Rating Distribution")
    if not ratings_df.empty:
        ratings_df.rename(columns={"_id": "Rating"}, inplace=True)
        fig1 = px.bar(ratings_df, x="Rating", y="count", color="Rating")
        st.plotly_chart(fig1, use_container_width=True)

with col_c2:
    st.subheader("AI Sentiment Distribution")
    if not sentiment_df.empty:
        sentiment_df.rename(columns={"_id": "Sentiment"}, inplace=True)
        # Handle cases where ai_sentiment might be missing
        sentiment_df.dropna(subset=["Sentiment"], inplace=True)
        fig2 = px.pie(sentiment_df, names="Sentiment", values="count", hole=0.3)
        st.plotly_chart(fig2, use_container_width=True)
