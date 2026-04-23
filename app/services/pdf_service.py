# app/services/pdf_service.py

import fitz
import re
from rust_parser import extract_and_clean_pdf

async def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        # Try high-performance Rust parser first
        return extract_and_clean_pdf(file_bytes)
    except Exception as e:
        print(f"Rust parser failed: {e}. Falling back to PyMuPDF (fitz)...")
        # Fallback to robust PyMuPDF
        text = ""
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        
        # Clean up the fallback text a bit
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 20) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            space_index = text.rfind(' ', start, end)
            if space_index != -1:
                end = space_index
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        
    return chunks