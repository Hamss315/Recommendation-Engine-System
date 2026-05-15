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

st.set_page_config(page_title="Users & Interactions", layout="wide")
st.title("👥 Users & Interactions")


db = get_database()

col1, col2 = st.columns(2)

with col1:
    action_type = st.selectbox(
        "Filter by Action Type",
        ["All", "view", "add_to_cart", "purchase", "ignore"]
    )

@st.cache_data(ttl=60)
def fetch_interaction_metrics(action):
    query = {}
    if action != "All":
        query["action"] = action
    df = pd.DataFrame(list(db.interactions.find(query).limit(1000)))
    if not df.empty:
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
    return df

interactions_df = fetch_interaction_metrics(action_type)
st.dataframe(interactions_df)

st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top Active Users")
    user_pipeline = [
        {"$group": {"_id": "$user_id", "actions": {"$sum": 1}}},
        {"$sort": {"actions": -1}},
        {"$limit": 10}
    ]
    users_df = pd.DataFrame(list(db.interactions.aggregate(user_pipeline)))
    if not users_df.empty:
        users_df.rename(columns={"_id": "User ID", "actions": "Action Count"}, inplace=True)
        fig_users = px.bar(users_df, x="User ID", y="Action Count", orientation="v")
        st.plotly_chart(fig_users)

with col4:
    st.subheader("Most Interacted Products")
    prod_pipeline = [
        {"$group": {"_id": "$product_id", "interactions": {"$sum": 1}}},
        {"$sort": {"interactions": -1}},
        {"$limit": 10}
    ]
    prod_df = pd.DataFrame(list(db.interactions.aggregate(prod_pipeline)))
    if not prod_df.empty:
        prod_df.rename(columns={"_id": "Product ID", "interactions": "Interaction Count"}, inplace=True)
        fig_prods = px.bar(prod_df, x="Product ID", y="Interaction Count", orientation="v")
        st.plotly_chart(fig_prods)
