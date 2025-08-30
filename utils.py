
import streamlit as st
from .config import Config

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents_ingested" not in st.session_state:
        st.session_state.documents_ingested = []
    if "current_model" not in st.session_state:
        st.session_state.current_model = Config.DEFAULT_MODEL

def get_model_info(model: str):
    # Informações breves para a UI (placeholder)
    infos = {
        "gpt-4": {
            "name": "GPT-4",
            "description": "Modelo de alta capacidade para tarefas complexas e respostas robustas.",
            "context": "Até ~128k tokens (varia por versão)."
        },
        "gpt-4-turbo-preview": {
            "name": "GPT-4 Turbo (preview)",
            "description": "Versão otimizada do GPT-4 com custo e latência inferiores.",
            "context": "Até ~128k tokens (varia por versão)."
        },
        "gpt-3.5-turbo": {
            "name": "GPT-3.5 Turbo",
            "description": "Modelo rápido e econômico para tarefas gerais.",
            "context": "Até ~16k-32k tokens (varia por versão)."
        },
        "gpt-3.5-turbo-16k": {
            "name": "GPT-3.5 Turbo 16k",
            "description": "Janela de contexto ampliada para entradas maiores.",
            "context": "Até ~16k tokens."
        },
    }
    return infos.get(model, {
        "name": model,
        "description": "Modelo customizado.",
        "context": "—"
    })
