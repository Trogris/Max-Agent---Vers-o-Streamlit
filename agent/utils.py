import streamlit as st
from .config import Config

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_model" not in st.session_state:
        st.session_state.current_model = Config.DEFAULT_MODEL

def get_model_info(model: str):
    return {"name": model, "description": "Modelo OpenAI", "context": "—"}
