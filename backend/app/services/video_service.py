from app.ingestion.youtube_transcript import (
    extract_video_id,
    fetch_youtube_transcript,
)

from app.processing.transcript_processor import (
    clean_segments,
    create_chunks,
)

from app.vector_store.chroma_store import add_video_chunks


def ingest_youtube_video(
    youtube_url: str,
    languages: list[str] | None = None,
) -> dict:
    """
    Process a YouTube video and store its transcript
    chunks in ChromaDB.
    """

    # Step 1: Extract video ID
    video_id = extract_video_id(youtube_url)

    # Step 2: Fetch transcript
    transcript = fetch_youtube_transcript(
        video_id=video_id,
        languages=languages,
    )

    # Step 3: Clean transcript segments
    cleaned_segments = clean_segments(
        transcript["segments"]
    )

    if not cleaned_segments:
        raise ValueError(
            "The video transcript contains no usable text."
        )

    # Step 4: Create transcript chunks
    chunks = create_chunks(
        segments=cleaned_segments,
        chunk_size=1000,
        overlap=150,
    )

    if not chunks:
        raise ValueError(
            "No transcript chunks could be created."
        )

    # Step 5: Store chunks in ChromaDB
    stored_ids = add_video_chunks(
        video_id=video_id,
        chunks=chunks,
    )

    # Step 6: Return ingestion metadata
    return {
        "video_id": video_id,
        "language": transcript["language"],
        "language_code": transcript["language_code"],
        "is_generated": transcript["is_generated"],
        "original_segments": len(transcript["segments"]),
        "cleaned_segments": len(cleaned_segments),
        "total_chunks": len(chunks),
        "stored_chunks": len(stored_ids),
        "status": "success",
    }