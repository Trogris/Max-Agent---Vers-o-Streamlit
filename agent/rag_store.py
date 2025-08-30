# agent/rag_store.py
import os
import uuid
from typing import List, Dict, Any
from dataclasses import dataclass
from io import BytesIO
import zipfile

# --- Patch do sqlite para Chroma no Streamlit Cloud ---
try:
    import sys
    import pysqlite3  # fornecido por pysqlite3-binary
    sys.modules["sqlite3"] = pysqlite3
    sys.modules["sqlite3.dbapi2"] = pysqlite3.dbapi2
except Exception:
    # Se falhar, segue com sqlite3 do sistema (pode funcionar localmente)
    pass

import chromadb

import chromadb
from chromadb.utils import embedding_functions
import requests  # <— novo

from .config import Config

# --- Leitores simples (PDF/DOCX/TXT) ---
def read_pdf_bytes(data: bytes) -> str:
    from PyPDF2 import PdfReader
    import io
    reader = PdfReader(io.BytesIO(data))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    return "\n".join(texts)

def read_docx_bytes(data: bytes) -> str:
    import io
    from docx import Document
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)

def read_txt_bytes(data: bytes, encoding="utf-8") -> str:
    try:
        return data.decode(encoding)
    except Exception:
        return data.decode("latin-1", errors="ignore")

def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
    return [c for c in chunks if c.strip()]

@dataclass
class RAGStats:
    total_documents: int
    embedding_model: str

class RAGStore:
    """
    RAGStore com ChromaDB:
    - add_uploaded_files: upload (Cloud e local)
    - add_folder: varrer pasta local (apenas local)
    - add_urls: baixar por URLs públicas (arquivo direto ou ZIP)
    """
    def __init__(self):
        persist_dir = Config.CHROMA_PERSIST_DIRECTORY
        os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="max_docs",
            metadata={"hnsw:space": "cosine"},
            embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                api_key=Config.OPENAI_API_KEY,
                model_name=Config.EMBEDDING_MODEL,
            ),
        )

        self.chunk_size = int(Config.RAG_CHUNK_SIZE)
        self.chunk_overlap = int(Config.RAG_CHUNK_OVERLAP)
        self.top_k = int(Config.RAG_TOP_K)

    # ---------- Ingestão: Upload ----------
    def add_uploaded_files(self, files) -> int:
        total_chunks = 0
        for f in files:
            name = f.name
            raw = f.read()
            total_chunks += self._index_bytes(name, raw, meta_type="upload")
        return total_chunks

    # ---------- Ingestão: Pasta local ----------
    def add_folder(self, folder_path: str) -> Dict[str, Any]:
        folder_path = os.path.abspath(folder_path)
        if not os.path.isdir(folder_path):
            return {"ok": False, "msg": f"Pasta não encontrada: {folder_path}"}

        exts = {".pdf", ".docx", ".txt"}
        total_files = 0
        total_chunks = 0

        for root, _, files in os.walk(folder_path):
            for fn in files:
                ext = os.path.splitext(fn)[1].lower()
                if ext not in exts:
                    continue
                total_files += 1
                path = os.path.join(root, fn)
                try:
                    with open(path, "rb") as fh:
                        raw = fh.read()
                    total_chunks += self._index_bytes(fn, raw, meta_type="folder", source_override=path)
                except Exception as e:
                    print(f"[INGEST] Falha ao ler {path}: {e}")

        return {"ok": True, "files": total_files, "chunks": total_chunks, "folder": folder_path}

    # ---------- Ingestão: URLs ----------
    def add_urls(self, urls: List[str]) -> Dict[str, Any]:
        """
        Aceita URLs http(s) de:
          - Arquivos .pdf, .docx, .txt (diretos)
          - ZIP contendo .pdf/.docx/.txt
        """
        total_files = 0
        total_chunks = 0
        processed = []

        for url in urls:
            u = url.strip()
            if not u:
                continue
            try:
                resp = requests.get(u, timeout=60)
                resp.raise_for_status()
                content = resp.content

                # ZIP?
                if u.lower().endswith(".zip") or _looks_like_zip(content):
                    # extrai somente arquivos suportados do zip
                    z = zipfile.ZipFile(BytesIO(content))
                    for name in z.namelist():
                        if not _is_supported_ext(name):
                            continue
                        raw = z.read(name)
                        total_files += 1
                        total_chunks += self._index_bytes(name, raw, meta_type="url-zip", source_override=f"{u}::{name}")
                    processed.append({"url": u, "type": "zip", "ok": True})
                else:
                    # Arquivo direto
                    if not _is_supported_ext(u):
                        processed.append({"url": u, "type": "file", "ok": False, "msg": "Extensão não suportada"})
                        continue
                    total_files += 1
                    total_chunks += self._index_bytes(u, content, meta_type="url")
                    processed.append({"url": u, "type": "file", "ok": True})
            except Exception as e:
                processed.append({"url": u, "type": "unknown", "ok": False, "msg": str(e)})

        return {"ok": True, "files": total_files, "chunks": total_chunks, "processed": processed}

    # ---------- Busca ----------
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        k = top_k or self.top_k
        if not query.strip():
            return []
        result = self.collection.query(query_texts=[query], n_results=k)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]
        out = []
        for i, txt in enumerate(docs):
            md = metas[i] if i < len(metas) else {}
            out.append({
                "text": txt,
                "source": md.get("source", "desconhecido"),
                "chunk_idx": md.get("chunk_idx", i),
                "score": dists[i] if i < len(dists) else None,
            })
        return out

    def get_collection_stats(self) -> Dict[str, Any]:
        count = self.collection.count()
        return {"total_documents": int(count), "embedding_model": Config.EMBEDDING_MODEL}

    # ---------- Internos ----------
    def _index_bytes(self, name: str, raw: bytes, meta_type: str, source_override: str = None) -> int:
        text = self._read_any(name, raw)
        if not text.strip():
            return 0
        chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{
            "source": source_override or name,
            "type": meta_type,
            "chunk_idx": i
        } for i, _ in enumerate(chunks)]
        self.collection.add(documents=chunks, metadatas=metadatas, ids=ids)
        return len(chunks)

    def _read_any(self, filename: str, raw: bytes) -> str:
        ext = os.path.splitext(filename.split("?")[0])[1].lower()
        if ext == ".pdf":
            return read_pdf_bytes(raw)
        elif ext == ".docx":
            return read_docx_bytes(raw)
        elif ext == ".txt":
            return read_txt_bytes(raw)
        else:
            return read_txt_bytes(raw)  # fallback

def _is_supported_ext(name: str) -> bool:
    ext = os.path.splitext(name.split("?")[0])[1].lower()
    return ext in {".pdf", ".docx", ".txt"}

def _looks_like_zip(content: bytes) -> bool:
    # ZIP files start with bytes: PK\x03\x04
    return content[:2] == b"PK"
