import streamlit as st
from supabase import create_client

@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def sign_up(email, password):
    supabase = get_supabase_client()
    return supabase.auth.sign_up({"email": email, "password": password})

def sign_in(email, password):
    supabase = get_supabase_client()
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def sign_out():
    supabase = get_supabase_client()
    supabase.auth.sign_out()