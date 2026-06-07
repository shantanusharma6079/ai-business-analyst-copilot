# AI Business Analyst Copilot

AI-powered Business Analyst Assistant built using FastAPI, PostgreSQL, pgvector, LangChain, and Groq.

## Features

* PDF Upload
* Document Parsing
* Recursive Chunking
* Vector Embeddings
* Semantic Search
* Retrieval-Augmented Generation (RAG)
* PostgreSQL + pgvector
* FastAPI REST APIs

## Tech Stack

* FastAPI
* PostgreSQL
* pgvector
* Alembic
* LangChain
* Groq
* Sentence Transformers
* Docker

## Architecture

PDF Upload
→ Text Extraction
→ Chunking
→ Embeddings
→ pgvector
→ Semantic Search
→ LLM
→ Answer

## Setup

```bash
git clone <repo-url>

cd ai-business-analyst-copilot

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

docker compose up -d

alembic upgrade head

uvicorn app.main:app --reload
```

## API Documentation

```text
http://localhost:8000/docs
```
