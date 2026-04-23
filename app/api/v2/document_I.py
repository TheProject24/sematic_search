from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body, BackgroundTasks, status
from typing import List, Annotated
from app.db import SessionLocal
from app.models import User, Folder, Document, ChatMessage
from app.core.auth import get_current_user
from app.services.ml_service import generate_embeddings, store
from app.services.pdf_service import extract_text_from_pdf, chunk_text
from app.services.llm_service import generate_answer
from app.services.worker import process_pdf_task

router = APIRouter()

@router.post("/upload/{folder_id}", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    folder_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id = Depends(get_current_user)
):
    db = SessionLocal()

    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.owner_id == user_id
    ).first()

    if not folder: raise HTTPException(404, "Folder not found")

    doc = Document(folder_id=folder_id, filename=file.filename, status = "processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    file_bytes = await file.read()

    background_tasks.add_task(process_pdf_task, str(doc.id), file_bytes)

    db.close()
    return {
        "document_id": doc.id,
        "status": "processing",
        "message": "File uploaded. Processing started in background."
    }


@router.get("/status/{document_id}")
async def get_document_status(document_id: str, user_id = Depends(get_current_user)):
    db = SessionLocal()
    # Ensure the document belongs to a folder owned by the user
    doc = db.query(Document).join(Folder).filter(
        Document.id == document_id, 
        Folder.owner_id == user_id
    ).first()
    
    if not doc:
        db.close()
        raise HTTPException(404, "Document not found")
    
    status = doc.status
    db.close()
    return {"document_id": document_id, "status": status}

@router.post("/chat/{folder_id}")
async def chat(
    folder_id: str,
    query: str = Body(..., embed=True), 
    user_id=Depends(get_current_user), 
):
    db = SessionLocal()
    
    # 1. Security & History
    folder = db.query(Folder).filter(Folder.id == folder_id, Folder.owner_id == user_id).first()
    if not folder: raise HTTPException(404)

    history = db.query(ChatMessage).filter(ChatMessage.folder_id == folder_id).order_by(ChatMessage.created_at.desc()).limit(6).all()
    formatted_history = [{"role": m.role, "content": m.content} for m in reversed(history)]

    # 2. Search
    q_emb = generate_embeddings([query])
    search_results = store.search(q_emb, folder_id=folder_id) # Returns [{"text":..., "source":...}]

    # 3. LLM Generate
    ans = await generate_answer(query, search_results, formatted_history)

    # 4. Persistence
    db.add(ChatMessage(folder_id=folder_id, role="user", content=query))
    db.add(ChatMessage(folder_id=folder_id, role="assistant", content=ans))
    db.commit()

    return {
        "answer": ans,
        "sources": list(set([r["source"] for r in search_results])), # UX: Unique list of files cited
        "context": search_results  # This contains [{text:..., source:...}]
    }