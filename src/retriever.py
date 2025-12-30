"""
Retriever module for InvestIQ.
"""

from sentence_transformers import SentenceTransformer
import faiss

class FinanceRetriever:
    def __init__(self, documents):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.documents = documents
        self.embeddings = self.model.encode(documents)
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def retrieve(self, query, k=3):
        query_embedding = self.model.encode([query])
        _, indices = self.index.search(query_embedding, k)
        return [self.documents[i] for i in indices[0]]
