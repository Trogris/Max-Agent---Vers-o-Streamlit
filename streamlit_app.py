import streamlit as st
from agent.config import Config
from agent.utils import init_session_state, get_model_info
from agent.rag_store import RAGStore
from agent.chat import MaxChatAgent, display_chat_interface, display_search_interface
from agent.ingest import display_ingestion_interface

st.set_page_config(page_title="Max - Assistente IA", page_icon="🤖", layout="wide")

def main():
    st.title("🤖 Max - Assistente de IA da Empresa")
    st.markdown("*Seu assistente inteligente para informações internas e suporte*")

    init_session_state()

    try:
        Config.validate()
    except ValueError as e:
        st.error(f"❌ Erro de configuração: {e}")
        st.stop()

    rag_store = RAGStore()
    chat_agent = MaxChatAgent(rag_store)

    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔍 Busca", "📁 Ingestão"])

    with tab1:
        display_chat_interface(chat_agent)
    with tab2:
        display_search_interface(rag_store)
    with tab3:
        display_ingestion_interface(rag_store)

if __name__ == "__main__":
    main()
