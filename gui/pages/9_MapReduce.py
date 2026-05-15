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
        
    return pe, af

pe, af = load_mapreduce()

tab1, tab2 = st.tabs(["Action Frequency", "Product Engagement"])

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
