from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.services.ml_service import store
from app.api.v1 import auth, document
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError # Added for the retry logic
from app.models import Base
# from app.core.settings import settings
import os
import time # Added for sleep

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STARTING UPPP...")
    
    # 1. Attempt to connect to DB with retries
    from app.db import engine
    retries = 5
    connected = False
    
    while retries > 0:
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            Base.metadata.create_all(engine)
            print("✅ Database and pgvector initialized")
            connected = True
            break
        except OperationalError as e:
            retries -= 1
            print(f"⌛ Waiting for Postgres... ({retries} retries left)")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Unexpected DB Error: {e}")
            break

    if not connected:
        print("🛑 Critical: Could not connect to Database. Search will be unavailable.")

    yield

    print("SHUTTING DOWN . . . ")

app = FastAPI(
    lifespan=lifespan,
    title="PDF Semantic Search API",
    description="API for semantic search in PDF documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(document.router, prefix="/api/v1", tags=["RAG"])
# app.include_router(api_router_v2, prefix="/api/v2")

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Welcome, Peter. The Semantic Search API is running."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)