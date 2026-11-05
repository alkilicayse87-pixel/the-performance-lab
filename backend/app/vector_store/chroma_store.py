
import hashlib
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from app.config import OPENAI_API_KEY


# Persistent database location
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIRECTORY = PROJECT_ROOT / "storage" / "chroma_db"

# ChromaDB collection
COLLECTION_NAME = "youtube_transcripts"

# OpenAI embedding model
EMBEDDING_MODEL = "text-embedding-3-small"


def get_embeddings() -> OpenAIEmbeddings:
    """
    Initialize the OpenAI embedding model.
    """

    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )


def get_vector_store() -> Chroma:
    """
    Initialize or load the persistent ChromaDB vector store.
    """

    CHROMA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIRECTORY),
    )


def generate_chunk_id(video_id: str, chunk: dict) -> str:
    """
    Generate a deterministic ID for each transcript chunk.
    """

    content = (
        f"{video_id}|"
        f"{chunk['chunk_index']}|"
        f"{chunk['text']}"
    )

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


def add_video_chunks(
    video_id: str,
    chunks: list[dict],
) -> list[str]:
    """
    Convert transcript chunks into LangChain Documents
    and store them in ChromaDB.
    """

    if not video_id:
        raise ValueError("video_id cannot be empty.")

    if not chunks:
        raise ValueError("No chunks provided.")

    documents = []
    ids = []

    for chunk in chunks:
        document = Document(
            page_content=chunk["text"],
            metadata={
                "video_id": video_id,
                "chunk_index": chunk["chunk_index"],
                "start_time": float(chunk["start_time"]),
                "end_time": float(chunk["end_time"]),
                "segment_count": chunk["segment_count"],
                "segment_indices": ",".join(
                    str(index)
                    for index in chunk["segment_indices"]
                ),
            },
        )

        documents.append(document)
        ids.append(generate_chunk_id(video_id, chunk))

    vector_store = get_vector_store()

    vector_store.add_documents(
        documents=documents,
        ids=ids,
    )

    return ids

def get_cached_video_chunks(video_id: str) -> list[dict]:
    """
    Retrieve existing transcript chunks for a video from ChromaDB.
    """

    if not video_id:
        raise ValueError("video_id cannot be empty.")

    vector_store = get_vector_store()

    results = vector_store.get(
        where={"video_id": video_id},
        include=["documents", "metadatas"],
    )

    chunks = []

    for document, metadata in zip(
        results["documents"],
        results["metadatas"],
    ):
        chunks.append({
            "text": document,
            "video_id": metadata["video_id"],
            "chunk_index": metadata["chunk_index"],
            "start_time": metadata["start_time"],
            "end_time": metadata["end_time"],
            "segment_count": metadata["segment_count"],
        })

    return sorted(
        chunks,
        key=lambda chunk: chunk["chunk_index"],
    )