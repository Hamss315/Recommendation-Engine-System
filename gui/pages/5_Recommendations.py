import streamlit as st

@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()

import sys
import os

# Ensure the parent directory is available for importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

st.set_page_config(page_title="Recommendations", layout="wide")
st.title("🎯 AI-Enhanced Product Recommendations")

st.info("💡 Recommendations are processed behind-the-scenes using our encapsulated abstraction module `utils/recommendation_engine.py`. This leverages the previously defined math completely outside dynamic Streamlit execution.")

user_id = st.text_input("Enter User ID (e.g. AO94DHGC771SJ)", "AO94DHGC771SJ")

if st.button("Generate Recommendations", type="primary"):
    with st.spinner("Connecting to external engine to process matrix paths..."):
        try:
            from utils.recommendation_engine import recommend_products
            
            recs = recommend_products(user_id, top_n=5)
            
            if not recs:
                st.warning("No recommendations found. User might not have enough history.")
            else:
                st.success(f"Top 5 Recommended Products for {user_id}")
                for i, prod in enumerate(recs):
                    st.write(f"{i+1}. **{prod}**")
                    
        except Exception as e:
            st.error(f"Error accessing recommendation engine: {e}")
