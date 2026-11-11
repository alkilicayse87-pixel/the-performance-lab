from app.vector_store.neon_store import (
    retrieve_chunks as neon_retrieve_chunks,
    retrieve_all_chunks as neon_retrieve_all_chunks,
)


def retrieve_chunks(
    query: str,
    video_id: str | None = None,
    k: int = 5,
) -> list[dict]:
    """Retrieve the most relevant transcript chunks from Neon."""

    return neon_retrieve_chunks(
        query=query,
        video_id=video_id,
        k=k,
    )


def retrieve_all_chunks(video_id: str) -> list[dict]:
    """Retrieve all transcript chunks for a specific video from Neon."""

    return neon_retrieve_all_chunks(video_id)
