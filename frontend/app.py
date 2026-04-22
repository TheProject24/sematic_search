import streamlit as st
import requests
from supabase import create_client, Client

# --- CONFIGURATION ---
# In production, these should be in .streamlit/secrets.toml
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] # Use the 'anon' key for frontend
API_URL = st.secrets["API_URL"] # e.g., https://your-app.railway.app/api/v1

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Academic PDF Tutor", layout="wide", page_icon="📚")

# --- AUTH HELPERS ---
def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.token = res.session.access_token
        st.session_state.user_id = res.user.id
        return True
    except Exception as e:
        st.error(f"Login error: {e}")
        return False

def signup(email, password):
    try:
        supabase.auth.sign_up({"email": email, "password": password})
        st.info("Check your email for a confirmation link!")
    except Exception as e:
        st.error(f"Signup error: {e}")

# --- SESSION STATE INITIALIZATION ---
if "token" not in st.session_state:
    st.title("🚀 Welcome to PDF Tutor")
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        pw = st.text_input("Password", type="password", key="login_pw")
        if st.button("Log In"):
            if login(email, pw): st.rerun()
            
    with tab2:
        s_email = st.text_input("Email", key="sig_email")
        s_pw = st.text_input("Password", type="password", key="sig_pw")
        if st.button("Sign Up"):
            signup(s_email, s_pw)
    st.stop()

# --- APP START ---
headers = {"Authorization": f"Bearer {st.session_state.token}"}

with st.sidebar:
    st.header("Your Study Sessions")
    
    # New Folder UI
    with st.expander("➕ New Session"):
        new_title = st.text_input("Session Title")
        if st.button("Create"):
            res = requests.post(f"{API_URL}/folders", json={"title": new_title}, headers=headers)
            if res.status_code == 200: st.rerun()

    # Load Folders
    try:
        folders_res = requests.get(f"{API_URL}/folders", headers=headers)
        folders = folders_res.json() if folders_res.status_code == 200 else []
    except:
        folders = []

    selected_folder = st.radio(
        "Select a chat", 
        options=folders, 
        format_func=lambda x: x['title'] if x else "No sessions yet"
    )
    
    st.divider()
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# --- CHAT INTERFACE ---
if selected_folder:
    st.title(f"📖 {selected_folder['title']}")
    f_id = selected_folder['id']

    # 1. File Management
    with st.expander("📄 Manage Documents"):
        files = st.file_uploader("Upload PDFs for this session", type="pdf", accept_multiple_files=True)
        if st.button("Upload & Process"):
            with st.spinner("Analyzing PDFs..."):
                payload = [("files", (f.name, f.getvalue(), "application/pdf")) for f in files]
                res = requests.post(f"{API_URL}/upload/{f_id}", files=payload, headers=headers)
                if res.status_code == 200:
                    st.success("Documents ready!")

    # 2. Chat Display
    # We maintain a local cache of the messages for instant UI updates
    if "messages" not in st.session_state:
        st.session_state.messages = {}

    if f_id not in st.session_state.messages:
        # Fetch history from backend
        history_res = requests.get(f"{API_URL}/history/{f_id}", headers=headers) # You'll need this simple endpoint
        st.session_state.messages[f_id] = history_res.json() if history_res.status_code == 200 else []

    for msg in st.session_state.messages[f_id]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 3. Chat Input
    if prompt := st.chat_input("Ask about your documents..."):
        # Display user message
        st.session_state.messages[f_id].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                res = requests.post(
                    f"{API_URL}/search", 
                    json={"query": prompt, "folder_id": f_id}, 
                    headers=headers
                )
                if res.status_code == 200:
                    answer = res.json()["ai_answer"]
                    st.markdown(answer)
                    st.session_state.messages[f_id].append({"role": "assistant", "content": answer})
                else:
                    st.error("Failed to get answer.")
else:
    st.info("👈 Create or select a session in the sidebar to start.")