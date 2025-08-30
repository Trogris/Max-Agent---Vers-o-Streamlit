import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

    AVAILABLE_MODELS = ["gpt-4","gpt-4-turbo-preview","gpt-3.5-turbo","gpt-3.5-turbo-16k"]

    RAG_CHUNK_SIZE = 1000
    RAG_CHUNK_OVERLAP = 200
    RAG_TOP_K = 5

    MAX_TOKENS = 4000
    TEMPERATURE = 0.7

    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY é obrigatória.")
        return True
