# 🔍 PDF Semantic Search

![PDF Semantic Search Hero](pdf_semantic_search_hero.png)

> **Elevate your document intelligence.** A state-of-the-art Retrieval-Augmented Generation (RAG) platform that transforms static PDFs into interactive, searchable knowledge bases using high-performance Rust parsing and hybrid vector storage.

---

## 🚀 Overview

**PDF Semantic Search** is a powerful, production-ready solution for intelligent document interaction. By combining the speed of **Rust** with the flexibility of **FastAPI** and the precision of **Llama 3.1**, this project enables users to upload vast amounts of PDF data and perform lightning-fast semantic queries that go beyond simple keyword matching.

### 🏆 Key Accomplishments

- **☁️ Supabase Integration**: Leverages Supabase for robust PostgreSQL hosting with `pgvector` and secure JWT-based authentication.
- **⚙️ Asynchronous Processing**: Implemented background workers using FastAPI's `BackgroundTasks` to handle intensive PDF parsing and embedding without blocking the API response.
- **📂 Session-Based Organization**: Introduced "Folders" to group related documents, enabling cleaner context management for complex research projects.
- **🦀 Hybrid Python-Rust Architecture**: Integrated a custom high-performance Rust parser (`lopdf`) via PyO3 to handle complex PDF text extraction with significantly lower latency than traditional Python libraries.
- **Advanced RAG Pipeline**: Built a robust Retrieval-Augmented Generation (RAG) workflow using Groq's high-speed inference (Llama 3.1) and Sentence Transformers.

---

## ✨ Features

- 📁 **Session-Based Upload**: Organize documents into "Folders" for isolated context.
- ⚡ **Lightning Fast Inference**: Sub-second responses using Groq's Llama 3.1 70B model.
- 🦀 **Rust-Powered Extraction**: Clean, accurate text extraction using a custom Rust-based parser.
- 🧠 **Semantic Understanding**: Uses metadata-enriched embeddings for deeper search context.
- 💬 **Smart Citations**: AI-generated answers include direct references and source tracking.
- 🐳 **Dockerized Deployment**: Fully containerized environment for seamless setup and scaling.

---

## 🛠️ Tech Stack

### Backend & AI

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **LLM**: Llama 3.1 (via [Groq](https://groq.com/))
- **Embeddings**: `all-MiniLM-L6-v2` ([Sentence-Transformers](https://www.sbert.net/))
- **Performance Engine**: [Rust](https://www.rust-lang.org/) (via [PyO3](https://pyo3.rs/))
- **Search**: [pgvector](https://github.com/pgvector/pgvector) on Supabase

### Infrastructure

- **Database**: PostgreSQL (Vector-enabled)
- **Auth & Storage**: [Supabase](https://supabase.com/)
- **Dependency Management**: [uv](https://github.com/astral-sh/uv)
- **Deployment**: Docker & Docker Compose

---

## 🏗️ Architecture

```mermaid
graph TD
    User([User/API Client]) --> API[FastAPI Backend]

    subgraph "Processing Pipeline"
        API --> Worker[Background Task]
        Worker --> RustParser[Rust Parser Module]
        RustParser --> Embedder[Sentence Transformer]
        Embedder --> Superbase[(Supabase + pgvector)]
    end

    subgraph "Inference Pipeline"
        API --> Superbase
        API --> LLM[Llama 3.1 via Groq]
        LLM --> Answer[Contextual Answer + Citations]
    end
```

---

## 🚦 Getting Started

### 1. Prerequisites

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- [uv](https://github.com/astral-sh/uv) for high-speed package management
- [Supabase Account](https://supabase.com/)
- [Groq API Key](https://console.groq.com/keys)

### 2. Setup Environment

Create a `.env` file in the root:

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=your_supabase_postgresql_url
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
LOCAL_SECRET_KEY=your_internal_secret
```

### 3. Build and Run

```bash
# 1. Install dependencies
uv sync

# 2. Build Rust parser extension
uv run maturin develop --manifest-path rust_parser/Cargo.toml

# 3. Start Backend
uv run uvicorn app.main:app --reload

# 4. Start Frontend (New Terminal)
cd frontend
npm install
npm run dev
```

### 4. Production Build

To generate optimized assets for production:

```bash
cd frontend
npm run build
```

The static files will be in `frontend/dist`.

The API supports session-based ingestion and retrieval:

- **Swagger UI**: `http://localhost:8000/docs`

### Key Endpoints

- `GET /api/v1/folders`: List all document sessions.
- `POST /api/v2/upload/{folder_id}`: Upload a document to a specific session (Async).
- `POST /api/v2/chat/{folder_id}`: Semantic chat within a session's context.

---

## 🗺️ Roadmap

- [x] **Sub-linear Scaling**: Full migration to `pgvector` on Supabase.
- [x] **Async Processing**: Background document ingestion tasks.
- [ ] **Next.js Frontend**: A sleek React interface for document management.
- [ ] **Cross-file Summarization**: Generate insights across a whole folder.
- [ ] **OCR Support**: For scanned PDFs using Tesseract.

---

<p align="center">
  Developed with ❤️ for high-performance semantic search.
</p>
