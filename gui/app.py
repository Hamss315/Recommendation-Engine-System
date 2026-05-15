import streamlit as st

st.set_page_config(
    page_title="E-Commerce Recommendation Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("E-Commerce Recommendation System Dashboard")
st.markdown("""
Welcome to the E-Commerce Recommendation Dashboard.
Navigation is available on the left sidebar.

### 🌐 Pages Available:
- **1_Dashboard**: Core KPIs and system overview
- **2_Reviews**: Drilldown into customer reviews
- **3_Products**: Catalog and product analysis
- **4_Users_Interactions**: User behavior mapping
- **5_Recommendations**: Product recommendation engine
- **6_AI_Sentiment**: NLP-enhanced review analysis
- **7_Crud_Operations**: Database management tooling
- **8_Aggregations**: Native MongoDB data pipelines
- **9_MapReduce**: Hadoop-style reduced analytics
- **10_Database_Info**: System structure configuration
""")