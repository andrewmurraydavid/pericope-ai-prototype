import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os

CHROMA_HOST = os.environ.get('CHROMA_HOST', 'localhost')
CHROMA_PORT = int(os.environ.get('CHROMA_PORT', '8000'))
CHROMA_SSL = int(os.environ.get('CHROMA_SSL', '0')) == 1
MODEL_NAME = os.environ.get('MODEL_NAME', 'all-distilroberta-v1')

print("ChromaDB client configuration:", CHROMA_HOST, CHROMA_PORT, CHROMA_SSL, MODEL_NAME)


class ChromaClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaClient, cls).__new__(cls)
            cls._instance.init_chroma()
        return cls._instance

    def init_chroma(self):
        print("Initializing ChromaDB client...")
        self.client = chromadb.HttpClient(host=CHROMA_HOST, port=443, ssl=True)
        sentence_transformer_ef = SentenceTransformerEmbeddingFunction(
            model_name=MODEL_NAME
        )
        self.collection = self.client.get_collection("bible_pericopes-v2", embedding_function=sentence_transformer_ef)

    def query(self, user_input, n):
        results = self.collection.query(
            query_texts=user_input,
            n_results=n,
            include=["metadatas", "distances"]
        )
        return results
