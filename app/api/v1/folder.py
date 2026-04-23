from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, status, HTTPException
from app.db import SessionLocal 
from app.models import Folder, Document
from app.core.auth import get_current_user
from app.services.worker import process_pdf_task

router = APIRouter()

# --- FOLDERS ---
@router.get("/folders")
async def list_folders(user_id=Depends(get_current_user)):
    db = SessionLocal()
    try:
        folders = db.query(Folder).filter(Folder.owner_id == user_id).all()
        return [
            {
                "id": f.id,
                "name": f.name,
                "doc_count": len(f.documents),
                # Removed 'last_active' because Document model has no 'created_at'
            } for f in folders
        ]
    finally:
        db.close()

# --- DOCUMENTS ---
@router.get("/folders/{folder_id}/documents")
async def list_documents(folder_id: str, user_id=Depends(get_current_user)):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id, Folder.owner_id == user_id).first()
        if not folder: 
            raise HTTPException(status_code=404, detail="Folder not found")
        
        return [
            {
                "id": d.id,
                "filename": d.filename,
                "status": d.status,
            } for d in folder.documents
        ]
    finally:
        db.close()

# --- UPLOAD ---
@router.post("/upload/{folder_id}", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    folder_id: str, 
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    user_id = Depends(get_current_user),
):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id, Folder.owner_id == user_id).first()
        if not folder: 
            raise HTTPException(status_code=404, detail="Folder not found")

        doc = Document(folder_id=folder_id, filename=file.filename, status="processing")
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        file_bytes = await file.read()
        background_tasks.add_task(process_pdf_task, str(doc.id), file_bytes)
        
        return {"id": doc.id, "status": "processing", "filename": doc.filename}
    finally:
        db.close()

# --- DELETE ---
@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: str, user_id=Depends(get_current_user)):
    db = SessionLocal()
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id, Folder.owner_id == user_id).first()
        if not folder: 
            raise HTTPException(status_code=404, detail="Folder not found")
        
        db.delete(folder)
        db.commit()
        return {"message": "Folder and associated data wiped."}
    finally:
        db.close()