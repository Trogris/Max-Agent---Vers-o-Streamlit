class RAGStore:
    def __init__(self):
        self._docs = []
    def add_documents(self, docs): self._docs.extend(docs)
    def search(self, query, top_k=3): return [{"text": f"Resultado {i}"} for i in range(top_k)]
    def get_collection_stats(self): return {"total_documents": len(self._docs), "embedding_model": "demo"}
