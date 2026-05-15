import streamlit as st

import streamlit as st
@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()

from pymongo import MongoClient
import pandas as pd

st.set_page_config(page_title="Database Info", layout="wide")
st.title("🗄️ Database Information")


db = get_database()

st.subheader("Collections Metadata")

collections = db.list_collection_names()
col_stats = []

for coll in collections:
    size_docs = db[coll].estimated_document_count()
    # Safely fetch indexes
    indexes = list(db[coll].list_indexes())
    index_names = [idx.get("name") for idx in indexes]
    
    col_stats.append({
        "Collection Name": coll,
        "Document Count": size_docs,
        "Defined Indexes": ", ".join(index_names)
    })

df = pd.DataFrame(col_stats)
st.dataframe(df, use_container_width=True)

st.divider()

st.subheader("System Architecture")
st.markdown("""
**Data Layer**
- **MongoDB**: Used as primary NoSQL data lake for products, reviews, and interactions logs. MapReduce job results, model endpoints (`ai_sentiment`), and processed datasets are natively available via indices.

**Logic Layer**
- **Python / Utils**: Helper abstraction libraries (like `recommendation_engine.py`) perform vectorized aggregations statically on loaded datasets if needed, preserving purity of the GUI without importing Notebooks.

**Presentation Layer**
- **Streamlit**: Renders PyMongo DataFrames reactively using mult-page routing (`gui/pages/**`).
""")
