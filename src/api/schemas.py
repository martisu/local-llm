"""API schemas for the RAG service."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str


class DocumentMetadata(BaseModel):
    id: str
    filename: str
    source: str
    chunks: int


class SearchResult(BaseModel):
    id: str
    content: str
    metadata: Dict
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_found: int
