import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()


@st.cache_data(ttl=3600)
def build_similarity_matrix(target_user=None):
    
    db = get_database()
    
    interactions = pd.DataFrame(list(db["interactions"].find({"action": {"$in": ["purchase", "add_to_cart"]}})))
    # Only fetch required fields to optimize memory
    reviews_df = pd.DataFrame(list(db["reviews"].find(
        {}, 
        {"reviewerID": 1, "asin": 1, "ai_sentiment": 1, "ai_sentiment_score": 1}
    )))
    
    if interactions.empty or reviews_df.empty:
        return None, None
        
    merged_df = interactions.merge(
        reviews_df,
        left_on=["user_id", "product_id"],
        right_on=["reviewerID", "asin"],
        how="left"
    )
    
    def sentiment_weight(sentiment):
        if not isinstance(sentiment, str): return 1
        sentiment = sentiment.lower()
        if sentiment == "positive": return 1.2
        elif sentiment == "negative": return 0.7
        else: return 1
        
    merged_df["sentiment_weight"] = merged_df["ai_sentiment"].apply(sentiment_weight)
    merged_df["final_score"] = merged_df["rating"] * merged_df["sentiment_weight"] * merged_df["ai_sentiment_score"].fillna(1.0)
    
    # Restore original notebook limit to prevent hanging RAM
    active_users = merged_df["user_id"].value_counts().head(1000).index.tolist()
    if target_user and target_user not in active_users:
        active_users.append(target_user)
        
    filtered_df = merged_df[merged_df["user_id"].isin(active_users)]
    
    if filtered_df.empty:
        return None, None

    ai_user_product_matrix = filtered_df.pivot_table(
        index="user_id",
        columns="product_id",
        values="final_score",
        fill_value=0
    )
    
    user_similarity = cosine_similarity(ai_user_product_matrix)
    similarity_df = pd.DataFrame(
        user_similarity,
        index=ai_user_product_matrix.index,
        columns=ai_user_product_matrix.index
    )
    
    return similarity_df, merged_df

def recommend_products(user_id, top_n=5):
    similarity_df, merged_df = build_similarity_matrix(user_id)
    if similarity_df is None or user_id not in similarity_df.index:
        return []
        
    similar_users = similarity_df[user_id].sort_values(ascending=False)
    similar_users = similar_users.iloc[1:6]
    
    recommended_products = set()
    for similar_user in similar_users.index:
        user_products = merged_df[merged_df["user_id"] == similar_user]["product_id"]
        recommended_products.update(user_products)
        
    current_user_products = set(merged_df[merged_df["user_id"] == user_id]["product_id"])
    recommendations = recommended_products - current_user_products
    
    return list(recommendations)[:top_n]
