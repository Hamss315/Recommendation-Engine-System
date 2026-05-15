import streamlit as st

import streamlit as st
@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()

from pymongo import MongoClient
import pandas as pd

st.set_page_config(page_title="Products", layout="wide")
st.title("📦 Product Catalog Analysis")

@st.cache_data(ttl=600)
def get_products_data():
    
    db = get_database()
    df = pd.DataFrame(list(db.products.find().limit(1000)))
    if not df.empty:
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
    return df

# Get Top Products dynamically from Reviews since "products" collection schema might be light
@st.cache_data(ttl=600)
def get_top_rated_analytics():
    
    db = get_database()
    
    pipeline = [
        {"$group": {
            "_id": "$asin", 
            "avg_rating": {"$avg": "$overall"},
            "review_count": {"$sum": 1},
            "avg_ai_sentiment": {"$avg": "$ai_sentiment_score"}
        }},
        {"$match": {"review_count": {"$gt": 5}}},
        {"$sort": {"avg_rating": -1, "review_count": -1}},
        {"$limit": 50}
    ]
    df = pd.DataFrame(list(db.reviews.aggregate(pipeline)))
    if not df.empty:
        df.rename(columns={"_id": "Product ID"}, inplace=True)
    return df

tab1, tab2 = st.tabs(["Products List", "Top Rated Analytics"])

with tab1:
    st.subheader("Raw Products Collection")
    prod_df = get_products_data()
    st.dataframe(prod_df)

with tab2:
    st.subheader("Top Rated Products (Derived from Reviews)")
    st.write("Products with the best overall average ratings and AI sentiment context (min 5 reviews).")
    top_df = get_top_rated_analytics()
    st.dataframe(top_df)
