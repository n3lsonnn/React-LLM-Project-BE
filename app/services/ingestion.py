import json
import os

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from app.core.database import SessionLocal
from app.models.document import Document

INDEXES_DIR = "indexes"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

model = SentenceTransformer("all-MiniLM-L6-v2")


def _extract_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    return " ".join(page.extract_text() or "" for page in reader.pages)


def _chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if c]


def _set_status(document_uuid: str, status: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.uuid == document_uuid).first()
        if doc:
            doc.status = status
            db.commit()
    finally:
        db.close()


def run_ingestion(file_path: str, document_uuid: str):
    try:
        _set_status(document_uuid, "processing")

        text = _extract_text(file_path)
        chunks = _chunk_text(text)

        embeddings = model.encode(chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        os.makedirs(INDEXES_DIR, exist_ok=True)
        faiss.write_index(index, f"{INDEXES_DIR}/{document_uuid}.faiss")

        with open(f"{INDEXES_DIR}/{document_uuid}.json", "w") as f:
            json.dump(chunks, f)

        _set_status(document_uuid, "complete")

    except Exception as e:
        print(f"Ingestion failed for {document_uuid}: {e}")
        _set_status(document_uuid, "failed")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
