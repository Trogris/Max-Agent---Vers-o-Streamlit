import streamlit as st
class MaxChatAgent:
    def __init__(self, rag_store): self.rag_store = rag_store
    def respond(self, user_text): return f"Eco: {user_text}"
def display_chat_interface(agent):
    st.subheader("Chat")
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    prompt = st.chat_input("Digite sua mensagem...")
    if prompt:
        st.session_state.messages.append({"role": "user","content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        reply = agent.respond(prompt)
        st.session_state.messages.append({"role": "assistant","content": reply})
        with st.chat_message("assistant"): st.markdown(reply)
def display_search_interface(rag_store):
    st.subheader("Busca (demo)")
    q = st.text_input("Consulta")
    if q: st.write(rag_store.search(q))
