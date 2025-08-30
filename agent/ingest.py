# agent/ingest.py
import streamlit as st

def display_ingestion_interface(rag_store):
    st.subheader("📁 Ingestão de Documentos")

    # Opção A — Upload
    st.markdown("**Opção A — Upload (Cloud e Local)**")
    files = st.file_uploader(
        "Envie arquivos (.pdf, .docx, .txt)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    if files:
        if st.button("➕ Indexar arquivos enviados"):
            with st.spinner("Indexando..."):
                n = rag_store.add_uploaded_files(files)
            st.success(f"{n} chunk(s) indexados a partir do upload.")

    st.divider()

    # Opção B — URLs
    st.markdown("**Opção B — URLs públicas**")
    st.caption("Aceita links diretos para .pdf/.docx/.txt ou um .zip contendo esses arquivos.")
    urls_text = st.text_area("Cole uma ou mais URLs (uma por linha)")
    if st.button("🌐 Baixar e indexar URLs"):
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        if not urls:
            st.warning("Informe pelo menos uma URL.")
        else:
            with st.spinner("Baixando e indexando..."):
                info = rag_store.add_urls(urls)
            st.success(f"Arquivos: {info['files']} | Chunks: {info['chunks']}")
            if info.get("processed"):
                st.write("Detalhe das URLs:")
                for item in info["processed"]:
                    st.write(f"- {item['url']} → {'OK' if item['ok'] else 'ERRO'} ({item.get('type','?')}) {item.get('msg','')}")

    st.divider()

    # Opção C — Pasta local (apenas quando rodando no seu PC)
    st.markdown("**Opção C — Pasta local (somente rodando localmente)**")
    folder = st.text_input("Caminho da pasta (ex.: C:\\docs, /Users/voce/docs)")
    if st.button("📂 Indexar pasta local"):
        if not folder.strip():
            st.warning("Informe um caminho de pasta válido.")
        else:
            with st.spinner(f"Indexando pasta: {folder}..."):
                info = rag_store.add_folder(folder)
            if info.get("ok"):
                st.success(f"Arquivos: {info['files']} | Chunks: {info['chunks']} | Pasta: {info['folder']}")
            else:
                st.error(info.get("msg", "Erro ao indexar pasta."))
