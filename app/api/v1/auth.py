from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import User
from app.core.security import hash_password, verify_password, create_access_token
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserAuth(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(data: UserAuth):
    db = SessionLocal()
    if db.query(User).filter(User.email == data.email).first():
        db.close()
        raise HTTPException(400, "Email already registered")
    
    user = User(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.close()
    return {"msg": "User created successfully"}


@router.post("/login")
def login(data: UserAuth):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        db.close()
        raise HTTPException(401, "invalid credentials")
    
    token = create_access_token(data={"sub": str(user.id)})
    db.close()
    return {"access_token": token, "token_type": "bearer"}