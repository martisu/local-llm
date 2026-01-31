import os
import uuid
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
from openai import AsyncOpenAI
from pypdf import PdfReader

from config.loader import load_config

logger = logging.getLogger("rag")


class RAGConfig(BaseModel):
    """RAG configuration settings."""
    chromadb_path: str = "data/chromadb"
    embedding_url: str
    embedding_api_key: str = "not-needed"
    embedding_model: str = "text-embedding-3-small"
    embedding_headers: Optional[dict] = None
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_threshold: float = 0.5


class RAGService:
    def __init__(self, config: RAGConfig = None):
        if config is None:
            # Load from config.yaml
            app_config = load_config()
            config = RAGConfig(
                chromadb_path="data/chromadb",
                embedding_url=app_config.backend.base_url,
                embedding_model="text-embedding-3-small"
            )

        self.config = config

        # Initialize ChromaDB
        os.makedirs(config.chromadb_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=config.chromadb_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

        # Initialize embedding client (OpenAI-compatible API)
        self.openai_client = AsyncOpenAI(
            base_url=config.embedding_url,
            api_key=config.embedding_api_key,
            default_headers=config.embedding_headers if config.embedding_headers else None
        )

    async def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text string."""
        text = text.replace("\n", " ")
        response = await self.openai_client.embeddings.create(
            input=[text],
            model=self.config.embedding_model
        )
        return response.data[0].embedding

    def _chunk_text(self, text: str) -> List[str]:
        """Simple text chunking by paragraph or fixed size."""
        chunks = []
        paragraphs = text.split("\n\n")

        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < self.config.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

                while len(current_chunk) > self.config.chunk_size:
                    chunks.append(current_chunk[:self.config.chunk_size])
                    current_chunk = current_chunk[self.config.chunk_size - self.config.chunk_overlap:]

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    async def ingest_document(self, file_path: str, metadata: dict) -> str:
        """Process and store a document (PDF or Markdown)."""
        doc_id = str(uuid.uuid4())
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        text = ""

        try:
            if ext == ".pdf":
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
            elif ext in [".md", ".txt"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file extension: {ext}")

            if not text.strip():
                raise ValueError("Document is empty")

            chunks = self._chunk_text(text)
            logger.info(f"Split {filename} into {len(chunks)} chunks")

            ids = []
            embeddings = []
            metadatas = []
            documents = []

            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_{i}"
                embedding = await self._get_embedding(chunk)

                ids.append(chunk_id)
                embeddings.append(embedding)
                documents.append(chunk)

                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "doc_id": doc_id,
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "source": filename
                })
                metadatas.append(chunk_metadata)

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )

            logger.info(f"Successfully ingested {filename} (ID: {doc_id})")
            return doc_id

        except Exception as e:
            logger.error(f"Error ingesting document {filename}: {str(e)}")
            raise e

    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant document chunks."""
        try:
            query_embedding = await self._get_embedding(query)

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            formatted_results = []

            ids = results.get("ids") if results else None
            if not ids or not ids[0]:
                return formatted_results

            ids_list = ids[0]

            try:
                distances_list = results.get("distances", [[]])[0]
                documents_list = results.get("documents", [[]])[0]
                metadatas_list = results.get("metadatas", [[]])[0]
            except (TypeError, IndexError):
                distances_list = []
                documents_list = []
                metadatas_list = []

            for i in range(len(ids_list)):
                score = 1 - distances_list[i] if i < len(distances_list) else 0

                if score < self.config.similarity_threshold:
                    continue

                formatted_results.append({
                    "id": ids_list[i],
                    "content": documents_list[i] if i < len(documents_list) else "",
                    "metadata": metadatas_list[i] if i < len(metadatas_list) else {},
                    "score": score
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []

    def list_documents(self) -> List[Dict]:
        """List all ingested documents (unique by doc_id)."""
        try:
            result = self.collection.get(include=["metadatas"])

            documents = {}
            metadatas = result.get("metadatas") or []
            for meta in metadatas:
                doc_id = meta.get("doc_id")
                if doc_id and doc_id not in documents:
                    documents[doc_id] = {
                        "id": doc_id,
                        "filename": meta.get("filename"),
                        "source": meta.get("source"),
                        "chunks": meta.get("total_chunks")
                    }

            return list(documents.values())
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and all its chunks."""
        try:
            self.collection.delete(
                where={"doc_id": doc_id}
            )
            logger.info(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            return False
