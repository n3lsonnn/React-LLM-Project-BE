import json
from typing import Generator

import faiss
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer

from app.core.config import settings

INDEXES_DIR = "indexes"

model = SentenceTransformer("all-MiniLM-L6-v2")
client = Groq(api_key=settings.GROQ_API_KEY)


def _load_index(document_uuid: str):
    index = faiss.read_index(f"{INDEXES_DIR}/{document_uuid}.faiss")
    with open(f"{INDEXES_DIR}/{document_uuid}.json") as f:
        chunks = json.load(f)
    return index, chunks


def _retrieve_chunks(document_uuid: str, question: str, top_k: int) -> list[str]:
    index, chunks = _load_index(document_uuid)
    query_embedding = model.encode([question])
    query_embedding = np.array(query_embedding).astype("float32")
    _, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0] if i < len(chunks)]


def stream_answer(document_uuid: str, question: str, top_k: int) -> Generator:
    context_chunks = _retrieve_chunks(document_uuid, question, top_k)
    context = "\n\n".join(context_chunks)

    yield f"data: [CITATIONS]{json.dumps(context_chunks)}\n\n"

    system_prompt = (
        "You are a helpful assistant that answers questions based strictly on the "
        "provided document context. If the answer is not in the context, say so clearly."
    )

    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        stream=True,
    )

    for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield f"data: {token}\n\n"

    yield "data: [DONE]\n\n"
