from app.ingestion.youtube_transcript import extract_video_id
from app.vector_store.chroma_store import get_cached_video_chunks


def ingest_youtube_video(
    youtube_url: str,
    languages: list[str] | None = None,
) -> dict:
    """
    Retrieve a video from the preloaded local catalog.
    New YouTube ingestion is disabled.
    """

    video_id = extract_video_id(youtube_url)

    cached_chunks = get_cached_video_chunks(video_id)

    if not cached_chunks:
        raise ValueError(
            "This video is not available in the supported catalog. "
            "Please select one of the five supported videos."
        )

    return {
        "video_id": video_id,
        "transcription_method": "local_catalog",
        "original_segments": sum(
            chunk["segment_count"] for chunk in cached_chunks
        ),
        "cleaned_segments": sum(
            chunk["segment_count"] for chunk in cached_chunks
        ),
        "total_chunks": len(cached_chunks),
        "stored_chunks": len(cached_chunks),
        "status": "success",
        "cached": True,
    }