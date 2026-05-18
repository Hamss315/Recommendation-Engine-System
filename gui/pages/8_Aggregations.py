import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()

st.set_page_config(page_title="Aggregations", layout="wide")
st.title("🧮 Aggregation Pipelines")
st.info("Dynamically executing complex aggregation pipelines against the raw data in MongoDB.")

# --- DATA LOADERS ---
@st.cache_data(ttl=600)
def load_top_rated():
    pipeline = [
        {"$group": {"_id": "$asin", "average_rating": {"$avg": "$overall"}, "total_reviews": {"$sum": 1}}},
        {"$sort": {"average_rating": -1}},
        {"$limit": 5}
    ]
    df = pd.DataFrame(list(get_database().reviews.aggregate(pipeline)))
    if not df.empty: df.rename(columns={"_id": "Product ID"}, inplace=True)
    return df

@st.cache_data(ttl=600)
def load_sentiment_dist():
    pipeline = [
        {"$group": {"_id": "$analytics.sentiment", "average_rating": {"$avg": "$overall"}, "review_count": {"$sum": 1}}}
    ]
    df = pd.DataFrame(list(get_database().reviews.aggregate(pipeline)))
    if not df.empty: df.rename(columns={"_id": "Sentiment"}, inplace=True)
    return df

@st.cache_data(ttl=600)
def load_active_users():
    pipeline = [
        {"$group": {"_id": "$user_id", "total_interactions": {"$sum": 1}}},
        {"$sort": {"total_interactions": -1}},
        {"$limit": 10}
    ]
    df = pd.DataFrame(list(get_database().interactions.aggregate(pipeline)))
    if not df.empty: df.rename(columns={"_id": "User ID"}, inplace=True)
    return df

@st.cache_data(ttl=600)
def load_positive_prods():
    pipeline = [
        {"$match": {"analytics.sentiment": "positive"}},
        {"$group": {"_id": "$asin", "positive_reviews": {"$sum": 1}}},
        {"$sort": {"positive_reviews": -1}},
        {"$limit": 5}
    ]
    df = pd.DataFrame(list(get_database().reviews.aggregate(pipeline)))
    if not df.empty: df.rename(columns={"_id": "Product ID"}, inplace=True)
    return df

@st.cache_data(ttl=600)
def load_helpful_dist():
    pipeline = [
        {"$unwind": "$helpful"},
        {"$group": {"_id": "$helpful", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    df = pd.DataFrame(list(get_database().reviews.aggregate(pipeline)))
    if not df.empty: df.rename(columns={"_id": "Helpful Votes"}, inplace=True)
    return df

@st.cache_data(ttl=600)
def load_engagement():
    pipeline = [
        {"$project": {"_id": 0, "product_id": "$asin", "rating": "$overall", "sentiment": "$analytics.sentiment", "review_length": "$analytics.review_length", "helpful_ratio": "$analytics.helpful_ratio", "engagement_score": {"$multiply": ["$analytics.helpful_ratio", "$analytics.review_length"]}}},
        {"$sort": {"engagement_score": -1}},
        {"$limit": 10}
    ]
    df = pd.DataFrame(list(get_database().reviews.aggregate(pipeline)))
    return df


# --- UI DISPLAY ---
tab1, tab2, tab3 = st.tabs(["Products Analysis", "Users & Sentiment", "Engagement"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 Highest Rated Products")
        df_top = load_top_rated()
        if not df_top.empty:
            st.dataframe(df_top, use_container_width=True)
        else:
            st.warning("No data.")
            
    with col2:
        st.subheader("Products with Most Positive Reviews")
        df_pos = load_positive_prods()
        if not df_pos.empty:
            fig = px.bar(df_pos, x="Product ID", y="positive_reviews", color="Product ID")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data.")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribution by Sentiment")
        df_sent = load_sentiment_dist()
        if not df_sent.empty:
            fig = px.pie(df_sent, names="Sentiment", values="review_count", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data.")
            
    with col2:
        st.subheader("Top 10 Most Active Users")
        df_users = load_active_users()
        if not df_users.empty:
            st.dataframe(df_users, use_container_width=True)
        else:
            st.warning("No data.")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Helpful Vote Distribution")
        df_help = load_helpful_dist()
        if not df_help.empty:
            # helpful array typically contains boolean or [votes, total]. If scalar, bar chart is fine.
            df_help["Helpful Votes"] = df_help["Helpful Votes"].astype(str)
            fig = px.bar(df_help.head(10), x="Helpful Votes", y="count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data.")
            
    with col2:
        st.subheader("Top 10 Engaged Products")
        st.write("Score = Helpful Ratio × Review Length")
        df_eng = load_engagement()
        if not df_eng.empty:
            st.dataframe(df_eng[["product_id", "engagement_score", "sentiment"]], use_container_width=True)
        else:
            st.warning("No data.")

