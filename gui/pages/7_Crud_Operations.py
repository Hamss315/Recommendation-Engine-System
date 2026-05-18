import streamlit as st
@st.cache_resource
def get_database():
    from pymongo import MongoClient
    return MongoClient("mongodb://localhost:27017/")["ecommerce_recommendation"]

db = get_database()

st.set_page_config(page_title="CRUD Operations", layout="wide")
st.title("🛠 Database CRUD Operations")

import pandas as pd

db = get_database()

tab1, tab2, tab3, tab4 = st.tabs(["Add Interaction", "Edit Review", "Delete User", "Read Data"])

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
            try:
                res = db.reviews.update_one(
                    {"reviewerID": r_user, "asin": r_prod},
                    {"$set": {"reviewText": r_text}},
                    upsert=True
                )
                if res.upserted_id:
                    st.success(f"Review didn't exist. Inserted as new record with ID: {res.upserted_id}")
                elif res.modified_count > 0:
                    st.success("Review updated successfully!")
                else:
                    st.warning("No changes made (review text was identical).")
            except Exception as e:
                st.error(f"Error occurred while updating review: {e}")
                
with tab3:
    st.subheader("Delete: Remove User")
    with st.form("delete_form"):
        d_user = st.text_input("User ID to Delete")
        
        if st.form_submit_button("Delete User"):
            try:
                res = db.users.delete_one({"user_id": d_user})
                if res.deleted_count > 0:
                    st.success("User deleted successfully!")
                else:
                    raise ValueError("User not found. Cannot delete non-existent user.")
            except ValueError as ve:
                st.warning(str(ve))
            except Exception as e:
                st.error(f"An error occurred while deleting user: {e}")

with tab4:
    st.subheader("Read: View Collection Data")
    
    collections = db.list_collection_names()
    
    selected_collection = st.selectbox("Select a Collection to View", collections)
    
    if selected_collection:
        st.write(f"Displaying up to 100 recent documents from `{selected_collection}`")
        data = list(db[selected_collection].find().limit(100))
        if data:
            df = pd.DataFrame(data)
            # MongoDB returns ObjectIds and lists of ObjectIds which crash Streamlit's PyArrow backend
            # We cast any column with generic 'object' dtype to string to make it display safely
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("This collection is currently empty.")
