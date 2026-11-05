
from app.vector_store.chroma_store import get_vector_store


def retrieve_chunks(
    query: str,
    video_id: str | None = None,
    k: int = 5,
) -> list[dict]:
    """
    Retrieve the most relevant transcript chunks
    from ChromaDB.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if k <= 0:
        raise ValueError("k must be greater than zero.")

    vector_store = get_vector_store()

    # Apply a video-specific filter when provided
    search_filter = None

    if video_id:
        search_filter = {"video_id": video_id}

    # Perform semantic search
    documents = vector_store.similarity_search(
        query=query,
        k=k,
        filter=search_filter,
    )

    results = []

    for document in documents:
        results.append({
            "text": document.page_content,
            "video_id": document.metadata["video_id"],
            "chunk_index": document.metadata["chunk_index"],
            "start_time": document.metadata["start_time"],
            "end_time": document.metadata["end_time"],
            "segment_count": document.metadata["segment_count"],
        })

    return results

def retrieve_all_chunks(video_id: str) -> list[dict]:
    """
    Retrieve all transcript chunks for a specific video.
    """

    if not video_id:
        raise ValueError("Video ID cannot be empty.")

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
        key=lambda item: item["start_time"],
    )
