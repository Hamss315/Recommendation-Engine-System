import streamlit as st

@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()

import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MapReduce Results", layout="wide")
st.title("🗺 MapReduce Operations")
st.info("Visualizes the outputs from the MapReduce job runs that were pre-loaded into the MongoDB.")

@st.cache_data(ttl=600)
def load_mapreduce():
    db = get_database()
    
    pe = pd.DataFrame(list(db.product_engagement.find().limit(500)))
    if not pe.empty and "_id" in pe.columns:
        pe.rename(columns={"_id": "Product ID", "value": "Engagement Metric"}, inplace=True)
        pe.sort_values(by="Engagement Metric", ascending=False, inplace=True)
        
    af = pd.DataFrame(list(db.action_frequency.find()))
    if not af.empty and "_id" in af.columns:
        af.rename(columns={"_id": "Action Type", "value": "Frequency"}, inplace=True)
        af.sort_values(by="Frequency", ascending=False, inplace=True)
        
    rating_yr = pd.DataFrame(list(db.rating_per_year.find()))
    if not rating_yr.empty and "_id" in rating_yr.columns:
        rating_yr.rename(columns={"_id": "Year", "value": "Total Ratings"}, inplace=True)
        rating_yr["Year"] = rating_yr["Year"].astype(int, errors='ignore')
        rating_yr.sort_values(by="Year", inplace=True)
        
    return pe, af, rating_yr

pe, af, rating_yr = load_mapreduce()

tab1, tab2, tab3 = st.tabs(["Action Frequency", "Product Engagement", "Rating Per Year"])

with tab1:
    st.subheader("Overall Action Frequency MapReduce")
    if af.empty:
        st.warning("No data in `action_frequency`.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(af, use_container_width=True)
        with col2:
            fig1 = px.bar(af, x="Action Type", y="Frequency", color="Action Type")
            st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Top Product Engagements MapReduce")
    if pe.empty:
        st.warning("No data in `product_engagement`.")
    else:
        st.write("Displaying Top 500 Engaged Products (computed by MR jobs).")
        st.dataframe(pe, use_container_width=True)

with tab3:
    st.subheader("Total Ratings Provided Per Year (MapReduce)")
    if rating_yr.empty:
        st.warning("No data in `rating_per_year`.")
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

