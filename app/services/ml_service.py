from fastembed import TextEmbedding
import numpy as np
from app.db import SessionLocal
from app.models import DocumentChunk, Document
from app.core.config import settings

class VectorStore:
    def __init__(self):
        # fastembed is MUCH lighter than sentence-transformers/torch.
        # BAAI/bge-small-en-v1.5 is exactly 384 dimensions.
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def add_texts(
            self, 
            texts: list[str], 
            embeddings: list[np.ndarray], 
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

def generate_embeddings(chunks: list[str]):
    # Returns a generator, so we convert to a list
    embeddings_generator = store.model.embed(chunks)
    return list(embeddings_generator)