import streamlit as st
import requests
from auth import sign_up, sign_in, sign_out
from library import save_to_library, get_library, delete_from_library

st.set_page_config(page_title="Voice Studio", layout="wide")
st.markdown("""
<style>
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    div[data-testid="stAudio"] {
        margin-top: 0.5rem;
    }
    .app-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }
    .app-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.2rem;
    }
    .app-header p {
        color: #A0A0B0;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

BACKEND_URL = "https://sumratariq--voice-studio-fastapi-app.modal.run"

# Initialize session state for tracking logged-in user
if "user" not in st.session_state:
    st.session_state.user = None

def login_signup_screen():
    st.markdown("""
    <div class="app-header">
        <h1>🎙️ Voice Studio</h1>
        <p>Your personal AI voice lab</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])

        with tab1:
            email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pw", placeholder="••••••••")
            if st.button("Log In", key="login_submit", use_container_width=True):
                try:
                    result = sign_in(email, password)
                    st.session_state.user = result.user
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

        with tab2:
            email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="signup_pw", placeholder="••••••••")
            if st.button("Sign Up", key="signup_submit", use_container_width=True):
                try:
                    sign_up(email, password)
                    st.success("Account created! Check your email to confirm, then log in.")
                except Exception as e:
                    st.error(f"Signup failed: {e}")

# Gate the whole app behind login
if st.session_state.user is None:
    login_signup_screen()
    st.stop()  # this halts execution here — nothing below runs until logged in

# ---- Everything below only runs once the user is logged in ----

with st.sidebar:
    st.markdown("### 👤 Profile")
    st.markdown(f"**{st.session_state.user.email}**")
    st.divider()
    if st.button("Log Out", use_container_width=True):
        sign_out()
        st.session_state.user = None
        st.rerun()
st.markdown("""
<div class="app-header">
    <h1>🎙️ Voice Studio</h1>
    <p>Generate, clone, and mix voices — powered by AI</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Text-to-Speech", "Voice Cloning", "Voice Mixing", "My Library"])
MALE_VOICES = {
    "Andrew": "Andrew Chipper",
    "Badr": "Badr Odhiambo",
    "Dionisio": "Dionisio Schuyler",
    "Royston": "Royston Min",
    "Viktor": "Viktor Eka",
    "Damien": "Damien Black",
}

FEMALE_VOICES = {
    "Claribel": "Claribel Dervla",
    "Daisy": "Daisy Studious",
    "Gracie": "Gracie Wise",
    "Alison": "Alison Dietlinde",
    "Ana": "Ana Florence",
    "Sofia": "Sofia Hellen",
}

with tab1:
    text = st.text_area("Text", key="tts_text")
    gender = st.radio("Voice type", ["Male", "Female"], key="tts_gender", horizontal=True)
    voice_options = MALE_VOICES if gender == "Male" else FEMALE_VOICES
    display_name = st.selectbox("Choose a voice", list(voice_options.keys()), key="tts_voice")
    actual_speaker = voice_options[display_name]

    if st.button("Generate", key="tts_btn"):
        res = requests.post(f"{BACKEND_URL}/tts", data={"text": text, "speaker": actual_speaker})
        st.session_state.tts_audio = res.content
        with open("tts_out.wav", "wb") as f:
            f.write(res.content)
        st.audio("tts_out.wav")

    if st.session_state.get("tts_audio") and st.button("💾 Save to Library", key="tts_save"):
        save_to_library(st.session_state.user.id, "generated", text, st.session_state.tts_audio)
        st.success("Saved!")
with tab2:
    text = st.text_area("Text", key="clone_text")
    voice_file = st.file_uploader("Voice sample", key="clone_file")

    if st.button("Clone", key="clone_btn") and voice_file:
        files = {"voice_sample": (voice_file.name, voice_file.getvalue())}
        res = requests.post(f"{BACKEND_URL}/clone", data={"text": text}, files=files)
        st.session_state.clone_audio = res.content
        with open("clone_out.wav", "wb") as f:
            f.write(res.content)
        st.audio("clone_out.wav")

    if st.session_state.get("clone_audio") and st.button("💾 Save to Library", key="clone_save"):
        save_to_library(st.session_state.user.id, "cloned", text, st.session_state.clone_audio)
        st.success("Saved!")

with tab3:
    text = st.text_area("Text", key="mix_text")

    col1, col2 = st.columns(2)
    with col1:
        voice_a = st.file_uploader("Voice A", key="mix_a")
    with col2:
        voice_b = st.file_uploader("Voice B", key="mix_b")

    weight_a = st.slider("Voice A strength (%)", min_value=0, max_value=100, value=50, key="mix_weight")
    weight_b = 100 - weight_a

    st.table({
        "Voice": ["Voice A", "Voice B"],
        "Percentage": [f"{weight_a}%", f"{weight_b}%"]
    })

    if st.button("Mix & Generate", key="mix_btn") and voice_a and voice_b:
        files = {
            "voice_a": (voice_a.name, voice_a.getvalue()),
            "voice_b": (voice_b.name, voice_b.getvalue())
        }
        res = requests.post(
            f"{BACKEND_URL}/mix",
            data={"text": text, "weight_a": weight_a},
            files=files
        )
        st.session_state.mix_audio = res.content
        with open("mix_out.wav", "wb") as f:
            f.write(res.content)
        st.audio("mix_out.wav")

    if st.session_state.get("mix_audio") and st.button("💾 Save to Library", key="mix_save"):
        save_to_library(st.session_state.user.id, "mixed", text, st.session_state.mix_audio)
        st.success("Saved!")
with tab4:
    st.subheader("My Library")
    lib_tab1, lib_tab2, lib_tab3 = st.tabs(["Generated", "Cloned", "Mixed"])

    def render_library(voice_type, tab):
        with tab:
            entries = get_library(st.session_state.user.id, voice_type)
            if not entries:
                st.info("Nothing saved here yet.")
            for entry in entries:
                st.write(entry["text_input"])
                st.audio(entry["audio_url"])
                if st.button("🗑️ Delete", key=f"del_{entry['id']}"):
                    delete_from_library(entry["id"], entry["storage_path"])
                    st.rerun()
                st.divider()

    render_library("generated", lib_tab1)
    render_library("cloned", lib_tab2)
    render_library("mixed", lib_tab3)       