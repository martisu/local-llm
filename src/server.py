"""
FastAPI Server - RAG API endpoints
"""
import logging
import sys
from pathlib import Path
from typing import List, Annotated
import shutil
import os

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from config.loader import load_config
from modules.rag import RAGService, RAGConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load configuration
app_config = load_config()

# Initialize RAG service
rag_config = RAGConfig(
    chromadb_path="data/chromadb",
    embedding_url=app_config.backend.base_url,
    embedding_model="text-embedding-3-small"
)
rag_service = RAGService(rag_config)

app = FastAPI(
    title="Local LLM API",
    description="RAG knowledge base and LLM inference",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    return {"status": "ok", "message": "Local LLM API", "version": "1.0.0"}


@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy",
        "chromadb_path": rag_config.chromadb_path,
        "embedding_model": rag_config.embedding_model
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return 204 No Content to prevent 404 errors in browser."""
    from fastapi.responses import Response
    return Response(status_code=204)


@app.post("/documents/upload", tags=["Knowledge Base"])
async def upload_document(file: Annotated[UploadFile, File(description="PDF, Markdown, or Text file to upload")]):
    allowed = {".pdf", ".md", ".markdown", ".txt"}
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()

    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {ext}")

    temp_dir = Path("./data/uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / filename

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc_id = await rag_service.ingest_document(str(temp_path), {"original_filename": filename})
        return {"document_id": doc_id, "filename": filename, "status": "completed"}

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path.exists():
            os.remove(temp_path)


@app.get("/documents", tags=["Knowledge Base"])
async def list_documents():
    docs = rag_service.list_documents()
    return docs


@app.delete("/documents/{document_id}", tags=["Knowledge Base"])
async def delete_document(document_id: str):
    success = rag_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Deleted"}


@app.post("/documents/search", tags=["Knowledge Base"])
async def search_knowledge_base(query: str = Query(...), top_k: int = Query(default=5)):
    results = await rag_service.search(query, top_k=top_k)
    return {"query": query, "results": results, "total_found": len(results)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
