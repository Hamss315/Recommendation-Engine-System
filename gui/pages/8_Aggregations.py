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

st.set_page_config(page_title="Aggregations", layout="wide")
st.title("🧮 Aggregation Pipelines")
st.info("Visualizing output generated dynamically by aggregation pipelines (from the generated PyMongo scripts) and cached to the database collections directly.")

@st.cache_data(ttl=600)
def load_aggregations():
    
    db = get_database()
    
    rating_yr = pd.DataFrame(list(db.rating_per_year.find()))
    if not rating_yr.empty and "_id" in rating_yr.columns:
        rating_yr.rename(columns={"_id": "Year", "value": "Total Ratings"}, inplace=True)
        # Type cast _id if it was float from MapReduce output style commonly stored
        rating_yr["Year"] = rating_yr["Year"].astype(int, errors='ignore')
        rating_yr.sort_values(by="Year", inplace=True)
        
    return rating_yr

rating_yr = load_aggregations()

st.subheader("Total Ratings Provided Per Year")

if rating_yr.empty:
    st.warning("`rating_per_year` collection is empty or not found. This aggregation might not have been executed yet.")
else:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(rating_yr, use_container_width=True)
    with col2:
        try:
            fig = px.line(rating_yr, x="Year", y="Total Ratings", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.bar_chart(rating_yr.set_index("Year"))
