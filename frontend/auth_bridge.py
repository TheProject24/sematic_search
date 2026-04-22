import streamlit as st
from supabase import create_client

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def login_user(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.token = res.session.access_token
        st.session_state.user = res.user
        return True

    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

def signup_user(email, password):
    try:
        supabase.auth.sign_up({ "email": email, "password": password})
        st.success("Check your email for a confirmation link!")
    except Exception as e:
        st.error(f"signup failed: {e}")

    