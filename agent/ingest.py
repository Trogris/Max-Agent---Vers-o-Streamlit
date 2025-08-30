import streamlit as st

def display_ingestion_interface(rag_store):
    st.subheader("📁 Ingestão de Documentos")

    st.markdown("**Upload de arquivos (.pdf, .docx, .txt)**")
    files = st.file_uploader(
        "Envie um ou mais arquivos",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    if files:
        with st.spinner("Indexando seus arquivos..."):
            total, report = rag_store.add_uploaded_files(files)
        if total > 0:
            st.success(f"✅ Indexei {total} chunk(s) de {len(report)} arquivo(s).")
        else:
            st.warning("Nenhum texto foi indexado. Verifique se os PDFs não são escaneados e se as extensões são suportadas.")

        with st.expander("Ver relatório da indexação"):
            for item in report:
                st.write(f"- **{item['name']}** → {item['status']}")

    st.divider()
    st.caption("Dica: apenas .pdf / .docx / .txt. PDFs escaneados (imagem) não têm texto — use OCR primeiro.")
