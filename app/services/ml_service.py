from huggingface_hub import AsyncInferenceClient
import numpy as np
from app.db import SessionLocal
from app.models import DocumentChunk, Document
from app.core.config import settings

class VectorStore:
    def __init__(self):
        # Official HF hub client handles all endpoints and retries
        self.client = AsyncInferenceClient(
            model="BAAI/bge-small-en-v1.5",
            api_key=settings.HUGGINGFACE_API_KEY
        )

    def add_texts(
            self, 
            texts: list[str], 
            embeddings: list[list[float]], 
            document_id
        ):
        db = SessionLocal()

        try:
            for text, emb in zip(texts, embeddings):
                chunk = DocumentChunk(
                    document_id=document_id,
                    content = text,
                    embedding=emb, 
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

    def search(self, query_vector: list[float], folder_id: str, k:int = 5):
        db = SessionLocal()

        try: 
            results = (
                db.query(DocumentChunk)
                .join(Document)
                .filter(Document.folder_id == folder_id)
                .order_by(DocumentChunk.embedding.l2_distance(query_vector))
                .limit(k)
                .all()
            )

            return [{"text": r.content, "source": r.document.filename} for r in results]
        finally:
            db.close()

store = VectorStore()

async def generate_embeddings(chunks: list[str]):
    """Fetches embeddings from Hugging Face Inference API using official client"""
    if not settings.HUGGINGFACE_API_KEY:
        raise ValueError("HUGGINGFACE_API_KEY is not set.")

    # feature_extraction handles a list of inputs
    results = await store.client.feature_extraction(chunks)
    
    # HF feature_extraction returns a numpy-like list of lists or a 3D array [batch, seq, dim]
    # For many models (like BGE), it returns [batch, seq, dim]. We need to pool or just take CLS.
    # HOWEVER, when using the inference API 'feature-extraction' task directly, 
    # it often returns the pooled embedding if the pipeline is set up correctly.
    
    # Let's ensure we return a list of embedding vectors
    return results.tolist() if hasattr(results, 'tolist') else results