# --- STAGE 1: Build Rust Extension ---
FROM python:3.12-slim AS builder

# Install system dependencies for Rust and Maturin
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /build

# Copy only the files needed for building
COPY pyproject.toml uv.lock README.md ./
COPY rust_parser/ rust_parser/

# Build the Rust wheel (--no-install-project avoids triggering maturin's build-system
# dep resolution for pdf-semantic-search itself, which would fail due to puccinialin)
RUN uv run --no-install-project maturin build --release --strip --manifest-path rust_parser/Cargo.toml

# --- STAGE 2: Final Production Image ---
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the built wheels from the builder stage
COPY --from=builder /build/rust_parser/target/wheels /tmp/wheels

# Copy application source
COPY . .

# Install dependencies and the built Rust extension
RUN uv sync --no-dev --frozen --no-install-project && \
    uv pip install /tmp/wheels/rust_parser*.whl

# Expose the API port
EXPOSE 8000

# Use the PORT environment variable provided by Render
# Call uvicorn directly from the venv to avoid uv re-syncing (and re-triggering
# build-system resolution) on every container start
CMD ["sh", "-c", "/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
