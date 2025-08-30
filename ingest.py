
import streamlit as st

def display_ingestion_interface(rag_store):
    st.subheader("📁 Ingestão de Documentos (demo)")
    files = st.file_uploader(
        "Envie arquivos (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    if files:
        # Apenas guarda nomes em memória para demo
        new_docs = [{"name": f.name, "size": f.size} for f in files]
        rag_store.add_documents(new_docs)
        if "documents_ingested" not in st.session_state:
            st.session_state.documents_ingested = []
        st.session_state.documents_ingested.extend(new_docs)
        st.success(f"Ingeridos {len(new_docs)} documento(s).")
        with st.expander("Ver documentos ingeridos"):
            for d in new_docs:
                st.write(f"- {d['name']} ({d['size']} bytes)")
