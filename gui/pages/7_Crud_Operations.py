import streamlit as st

import streamlit as st
@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()

from pymongo import MongoClient

st.set_page_config(page_title="CRUD Operations", layout="wide")
st.title("🛠 Database CRUD Operations")


db = get_database()

tab1, tab2, tab3 = st.tabs(["Add Interaction", "Edit Review", "Delete User"])

with tab1:
    st.subheader("Insert: Add User Interaction")
    with st.form("insert_form"):
        i_user = st.text_input("User ID")
        i_prod = st.text_input("Product ID")
        i_action = st.selectbox("Action", ["view", "add_to_cart", "purchase", "ignore"])
        i_rating = st.slider("Interaction Rating", 1, 5)
        
        if st.form_submit_button("Add Interaction"):
            db.interactions.insert_one({
                "user_id": i_user,
                "product_id": i_prod,
                "action": i_action,
                "rating": i_rating
            })
            st.success("Interaction inserted successfully!")

with tab2:
    st.subheader("Update: Edit Review Text")
    with st.form("update_form"):
        r_user = st.text_input("Reviewer ID")
        r_prod = st.text_input("Product ID (asin)")
        r_text = st.text_area("Updated Review Text")
        
        if st.form_submit_button("Update Review"):
            res = db.reviews.update_one(
                {"reviewerID": r_user, "asin": r_prod},
                {"$set": {"reviewText": r_text}}
            )
            if res.modified_count > 0:
                st.success("Review updated successfully!")
            else:
                st.warning("Review not found or no changes made.")
                
with tab3:
    st.subheader("Delete: Remove User")
    with st.form("delete_form"):
        d_user = st.text_input("User ID to Delete")
        
        if st.form_submit_button("Delete User"):
            res = db.users.delete_one({"user_id": d_user})
            if res.deleted_count > 0:
                st.success("User deleted successfully!")
            else:
                st.warning("User not found.")
