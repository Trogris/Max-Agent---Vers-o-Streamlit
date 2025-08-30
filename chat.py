
import streamlit as st

class MaxChatAgent:
    """Agente de chat placeholder. Integração real com OpenAI pode ser adicionada aqui."""
    def __init__(self, rag_store):
        self.rag_store = rag_store

    def respond(self, user_text: str) -> str:
        # Placeholder: ecoa e simula referência
        if not user_text.strip():
            return "Como posso ajudar hoje?"
        results = self.rag_store.search(user_text)
        ref = ", ".join([r["text"] for r in results]) if results else "sem referências"
        return f"Você disse: '{user_text}'. Aqui vai uma resposta simulada (refs: {ref})."

def display_chat_interface(agent: MaxChatAgent):
    st.subheader("💬 Chat (demo)")
    # Histórico
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Campo de entrada direto ao entrar
    prompt = st.chat_input("Digite sua mensagem...")
    if prompt is not None:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        reply = agent.respond(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

def display_search_interface(rag_store):
    st.subheader("🔍 Busca (demo)")
    q = st.text_input("Consulta")
    if q:
        results = rag_store.search(q)
        for r in results:
            st.write(f"- {r['text']}")
