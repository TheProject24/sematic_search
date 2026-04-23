from fastapi import APIRouter, UploadFile, File, HTTPException, Body, Depends
from app.services.pdf_service import extract_text_from_pdf, chunk_text
from app.services.ml_service import generate_embeddings, store
from app.services.storage_service import cloud_storage
from typing import List, Annotated
from pydantic import BaseModel
from app.services.llm_service import generate_answer
from app.db import SessionLocal # Using the new db.py
from app.models.message import ChatMessage
from app.models.folder import ChatFolder
from app.core.auth import get_current_user
import hashlib

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    folder_id: str
    k: int = 3

@router.post("/upload/folder/{folder_id}")
async def upload_documents(
    folder_id: str,
    files: Annotated[List[UploadFile], File(description="Multiple PDF files")],
    user_id = Depends(get_current_user)
):
    # user_id = "e86a94f4-6c08-46de-94e7-c13a2293e01f"
    db = SessionLocal()

    try:
        folder = db.query(ChatFolder).filter(
            ChatFolder.id == folder_id,
            ChatFolder.user_id == user_id
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Chat folder not found or access denied")
        
        total_chunks_added = 0
        processed_files = []

        for file in files:

            file_bytes = await file.read()
            storage_path = await cloud_storage.upload_file(file_bytes, file.filename, user_id)

            text = await extract_text_from_pdf(file_bytes)
            chunks = chunk_text(text)
            embeddings = await generate_embeddings(chunks)

            # Note: endpoints.py seems to use an older DB schema pattern. 
            # Passing folder_id in meta as a workaround if needed, but VectorStore.add_texts expects document_id.
            # We'll use None for now or create a dummy doc if necessary.
            store.add_texts(chunks, embeddings, document_id=None)

            total_chunks_added += len(chunks)
            processed_files.append(file.filename)

        return {
            "folder_id":folder_id,
            "filenames": processed_files,
            "total_chunks": total_chunks_added
        }
    finally:
        db.close()


@router.post("/search")
async def search_documents(request: SearchRequest, user_id: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        # Verify folder ownership
        folder = db.query(ChatFolder).filter(
            ChatFolder.id == request.folder_id,
            ChatFolder.user_id == user_id
        ).first()
        
        if not folder:
            raise HTTPException(status_code=404, detail="Chat folder not found or access denied")

        history = db.query(ChatMessage).filter(
            ChatMessage.folder_id == request.folder_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()

        formatted_history = [{ "role": m.role, "content": m.content } for m in reversed(history)]

        user_msg = ChatMessage(folder_id=request.folder_id, role='user', content=request.query)
        db.add(user_msg)
        db.commit()

        results = await generate_embeddings([request.query])
        query_vector = results[0]
        results = store.search(query_vector, folder_id=request.folder_id, k=request.k)

        ai_answer = await generate_answer(
            query = request.query,
            search_results=results,
            chat_history=formatted_history
        )

        ai_msg = ChatMessage(folder_id=request.folder_id, role="assistant", content=ai_answer)
        db.add(ai_msg)
        db.commit()

        return {
            "folder_id": request.folder_id,
            "ai_answer": ai_answer,
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/folders")
async def create_folder(title: str = Body(..., embed=True), user_id: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        new_folder = ChatFolder(title=title, user_id=user_id)
        db.add(new_folder)
        db.commit()
        db.refresh(new_folder)
        return {"id": new_folder.id, "title": new_folder.title}
    finally:
        db.close()

@router.get("/folders")
async def list_folders(user_id: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        folders = db.query(ChatFolder).filter(ChatFolder.user_id == user_id).all()
        return [{"id": f.id, "title": f.title} for f in folders]
    finally:
        db.close()



@router.get("/history/{folder_id}")
async def get_chat_history(folder_id: str, user_id: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        # We filter by folder_id, and RLS in Supabase handles the user_id safety
        messages = db.query(ChatMessage).filter(
            ChatMessage.folder_id == folder_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return [{"role": m.role, "content": m.content} for m in messages]
    finally:
        db.close()