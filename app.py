import streamlit as st
import requests

BACKEND_URL = "https://modal.com/apps/sumratariq/main/ap-0bL0VThkEm3uxPJgbY7iUr"

st.title("Voice Studio")
tab1, tab2, tab3 = st.tabs(["Text-to-Speech", "Voice Cloning", "Voice Mixing"])

with tab1:
    text = st.text_area("Text", key="tts_text")
    if st.button("Generate", key="tts_btn"):
        res = requests.post(f"{BACKEND_URL}/tts", data={"text": text})
        with open("tts_out.wav", "wb") as f:
            f.write(res.content)
        st.audio("tts_out.wav")

with tab2:
    text = st.text_area("Text", key="clone_text")
    voice_file = st.file_uploader("Voice sample", key="clone_file")
    if st.button("Clone", key="clone_btn") and voice_file:
        files = {"voice_sample": (voice_file.name, voice_file.getvalue())}
        res = requests.post(f"{BACKEND_URL}/clone", data={"text": text}, files=files)
        with open("clone_out.wav", "wb") as f:
            f.write(res.content)
        st.audio("clone_out.wav")

with tab3:
    text = st.text_area("Text", key="mix_text")
    voice_a = st.file_uploader("Voice A", key="mix_a")
    voice_b = st.file_uploader("Voice B", key="mix_b")
    if st.button("Mix & Generate", key="mix_btn") and voice_a and voice_b:
        files = {
            "voice_a": (voice_a.name, voice_a.getvalue()),
            "voice_b": (voice_b.name, voice_b.getvalue())
        }
        res = requests.post(f"{BACKEND_URL}/mix", data={"text": text}, files=files)
        with open("mix_out.wav", "wb") as f:
            f.write(res.content)
        st.audio("mix_out.wav")