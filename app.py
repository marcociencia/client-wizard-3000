import streamlit as st
from supabase import create_client, Client

# Page Configuration
st.set_page_config(page_title="User Registration", page_icon="📋")

# Initialize connection to Supabase
# The @st.cache_resource decorator ensures the connection is only created once
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("Failed to connect to the database. Please check your secrets configuration.")
    st.stop()

# UI Layout
st.title("User Registration Portal")
st.markdown("Please fill out the form below to create your account.")

# Registration Form
with st.form("registration_form"):
    st.subheader("Personal Information")
    name = st.text_input("Full Name", placeholder="John Doe")
    email = st.text_input("Email Address", placeholder="johndoe@example.com")
    
    submit_button = st.form_submit_button("Register Now")

    if submit_button:
        if name.strip() and email.strip():
            try:
                # Insert data into the 'users' table
                data = supabase.table("users").insert({"name": name, "email": email}).execute()
                st.success(f"Registration successful! Welcome, {name}.")
            except Exception as e:
                # Handle duplicate email constraint
                if "duplicate key value" in str(e) or "unique constraint" in str(e).lower():
                    st.error("This email address is already registered. Please use another one.")
                else:
                    st.error(f"An error occurred during registration: {e}")
        else:
            st.warning("Please fill out all fields before submitting.")