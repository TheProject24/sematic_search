from app.db import SessionLocal
from app.models import Document
from app.services.pdf_service import extract_text_from_pdf, chunk_text
from app.services.ml_service import generate_embeddings, store

async def process_pdf_task(doc_id: str, file_bytes: bytes):
    db = SessionLocal()
    try:
        text = await extract_text_from_pdf(file_bytes)

        chunks = chunk_text(text)
        embs = generate_embeddings(chunks)
        store.add_texts(chunks, embs, document_id=doc_id)

        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.status = "completed"
        db.commit()
        print(f"Processing complete for {doc_id}")

    except Exception as e:
        db.rollback()
        doc = db.query(Document).filter(Document.id == doc_id).first()
        doc.status = f"error: {str(e)}"
        db.commit()
        print(f"Error processing {doc_id}: {e}")

    finally:
        db.close()