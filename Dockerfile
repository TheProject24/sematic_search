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
COPY pyproject.toml uv.lock ./
COPY rust_parser/ rust_parser/

# Build the Rust wheel
RUN uv run maturin build --release --strip --manifest-path rust_parser/Cargo.toml

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
COPY --from=builder /build/target/wheels /tmp/wheels

# Copy application source
COPY . .

# Install dependencies and the built Rust extension
RUN uv sync --no-dev --frozen && \
    uv pip install /tmp/wheels/rust_parser*.whl

# Expose the API port
EXPOSE 8000

# Use the PORT environment variable provided by Render
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
