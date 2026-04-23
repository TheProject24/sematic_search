from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body, BackgroundTasks, status
from typing import List, Annotated
from app.db import SessionLocal
from app.models import User, Folder, Document, ChatMessage
from app.core.auth import get_current_user
from app.services.ml_service import generate_embeddings, store
from app.services.pdf_service import extract_text_from_pdf, chunk_text
from app.services.llm_service import generate_answer

router = APIRouter()

@router.post("/folders")
async def create_folder(
    name: str = Body(..., embed=True), 
    user_id: str = Depends(get_current_user)
):
    db = SessionLocal()
    folder = Folder(name=name, owner_id=user_id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    db.close()
    return folder



@router.post("/upload/{folder_id}")
async def upload(
    folder_id: str, 
    file: UploadFile = File(...), # Changed from files: List[UploadFile]
    user_id = Depends(get_current_user)
):
    db = SessionLocal()
    # 1. Verify folder exists and belongs to user
    folder = db.query(Folder).filter(
        Folder.id == folder_id, 
        Folder.owner_id == user_id
    ).first()

    if not folder: 
        db.close()
        raise HTTPException(404, "Folder not found")

    # 2. Process the single file
    content = await file.read()
    text = await extract_text_from_pdf(content)

    doc = Document(folder_id=folder_id, filename=file.filename)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    chunks = chunk_text(text)
    embs = await generate_embeddings(chunks)
    store.add_texts(chunks, embs, document_id=doc.id)

    db.close()
    return {"status": "success", "filename": file.filename}

@router.post("/chat/{folder_id}")
async def chat(
    folder_id: str, 
    query: str =Body(..., embed=True), 
    user_id = Depends(get_current_user)
):
    db = SessionLocal()

    history_records = db.query(ChatMessage).filter(
        ChatMessage.folder_id == folder_id
    ).order_by(ChatMessage.created_at.desc()).limit(5).all()

    formatted_history = [{"role": m.role, "content": m.content} for m in reversed(history_records)]

    folder = db.query(Folder).filter(
        Folder.id == folder_id, 
        Folder.owner_id == user_id
    ).first()

    if not folder: raise HTTPException(404)

    results = await generate_embeddings([query])
    q_emb = results[0]
    context = store.search(q_emb, folder_id=folder_id)

    ans = await generate_answer(query, context, formatted_history)

    db.add(ChatMessage(folder_id=folder_id, role="user", content=query))
    db.add(ChatMessage(folder_id=folder_id, role="assistant", content=ans))

    db.commit()
    db.close()
    return {"answer": ans, "context": context}
    