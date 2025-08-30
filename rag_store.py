
from dataclasses import dataclass
from .config import Config

@dataclass
class RAGStats:
    total_documents: int
    embedding_model: str

class RAGStore:
    """Stub simples para evitar erros de import e permitir testes de UI."""
    def __init__(self):
        # Em uma versão real, aqui você iniciaria o ChromaDB/FAISS, etc.
        self._docs = []

    def add_documents(self, docs):
        self._docs.extend(docs)

    def search(self, query: str, top_k: int = None):
        # Placeholder: retorna títulos fictícios
        return [{"id": i, "text": f"Resultado {i} para '{query}'"} for i in range(1, 4)]

    def get_collection_stats(self):
        return {
            "total_documents": len(self._docs),
            "embedding_model": Config.EMBEDDING_MODEL,
        }
