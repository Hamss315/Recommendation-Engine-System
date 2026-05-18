import streamlit as st

@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()

from pymongo import MongoClient
import pandas as pd

st.set_page_config(page_title="Reviews", layout="wide")
st.title("📝 Customer Reviews")


db = get_database()

col1, col2, col3 = st.columns(3)
search_user = col1.text_input("Search by User ID (reviewerID)")
search_product = col2.text_input("Search by Product ID (asin)")
min_rating = col3.slider("Minimum Rating", 1, 5, 1)

col4, col5 = st.columns(2)
sentiment_filter = col4.selectbox("Filter by Analytics Sentiment", ["All", "positive", "neutral", "negative"])
ai_sentiment_filter = col5.selectbox("Filter by AI Sentiment", ["All", "POSITIVE", "NEGATIVE", "NEUTRAL"])

@st.cache_data(ttl=60)
def get_reviews_data(search_user, search_product, min_rating, sentiment_filter, ai_sentiment_filter):
    query = {"overall": {"$gte": min_rating}}
    
    if search_user:
        query["reviewerID"] = {"$regex": search_user, "$options": "i"}
    if search_product:
        query["asin"] = {"$regex": search_product, "$options": "i"}
        
    if sentiment_filter != "All":
        query["analytics.sentiment"] = sentiment_filter.lower()
        
    if ai_sentiment_filter != "All":
        # Keep consistent with how it's stored in MongoDB
        query["ai_sentiment"] = {"$regex": f"^{ai_sentiment_filter}$", "$options": "i"}
        
    cursor = db.reviews.find(query).limit(500)
    df = pd.DataFrame(list(cursor))
    if not df.empty:
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
    return df

df = get_reviews_data(search_user, search_product, min_rating, sentiment_filter, ai_sentiment_filter)

if df.empty:
    st.info("No reviews found matching the filters.")
else:
    st.write(f"Showing top {len(df)} matching results:")
    st.dataframe(df)
