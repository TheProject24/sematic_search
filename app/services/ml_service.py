from sentence_transformers import SentenceTransformer
import numpy as np
from app.db import SessionLocal
from app.models import DocumentChunk, Document
import json

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def add_texts(
            self, 
            texts: list[str], 
            embeddings: np.ndarray, 
            document_id
        ):
        db = SessionLocal()

        try:
            for text, emb in zip(texts, embeddings):
                chunk = DocumentChunk(
                    document_id=document_id,
                    content = text,
                    embedding=emb.tolist(),
                    meta={}
                )
                db.add(chunk)
            db.commit()
            print(f"DB: Persisted {len(texts)} chunks for Doc ID: {document_id}")        
        except Exception as e:
            db.rollback()
            print(f"DB Error: {e}")
            raise e
        finally:
            db.close()

    def search(self, query_vector: np.ndarray, folder_id: str, k:int = 5):
        db = SessionLocal()

        try: 
            v = query_vector[0].tolist()

            results = (
                db.query(DocumentChunk)
                .join(Document)
                .filter(Document.folder_id == folder_id)
                .order_by(DocumentChunk.embedding.l2_distance(v))
                .limit(k)
                .all()
            )

            return [{"text": r.content, "source": r.document.filename} for r in results]
        finally:
            db.close()

store = VectorStore()

def generate_embeddings(chunks: list[str]):
    return store.model.encode(chunks)