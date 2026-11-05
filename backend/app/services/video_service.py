
from youtube_transcript_api._errors import (
    IpBlocked,
    NoTranscriptFound,
    TranscriptsDisabled,
)

from app.ingestion.youtube_transcript import (
    extract_video_id,
    fetch_youtube_transcript,
)
from app.ingestion.youtube_audio import transcribe_youtube_audio

from app.processing.transcript_processor import (
    clean_segments,
    create_chunks,
)

from app.vector_store.chroma_store import (
    add_video_chunks,
    get_cached_video_chunks,
)


def ingest_youtube_video(
    youtube_url: str,
    languages: list[str] | None = None,
) -> dict:
    """
    Ingest a YouTube video using its transcript or audio transcription.
    """

    video_id = extract_video_id(youtube_url)

# Check whether the video is already stored in ChromaDB.
    cached_chunks = get_cached_video_chunks(video_id)

    if cached_chunks:
        return {
            "video_id": video_id,
            "transcription_method": "cache",
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

    # Step 1: Try to retrieve YouTube subtitles.
    try:
        transcript = fetch_youtube_transcript(
            video_id=video_id,
            languages=languages,
        )
        transcription_method = "youtube_transcript"

    # Step 2: Fall back to audio transcription if subtitles are unavailable.
    except (
        TranscriptsDisabled,
        NoTranscriptFound,
        IpBlocked,
    ):
        transcript = transcribe_youtube_audio(video_id)
        transcription_method = "openai_transcription"

    # Step 3: Clean transcript segments.
    cleaned_segments = clean_segments(transcript["segments"])

    if not cleaned_segments:
        raise ValueError("The video transcript contains no usable text.")

    # Step 4: Create transcript chunks.
    chunks = create_chunks(
        segments=cleaned_segments,
        chunk_size=1000,
        overlap=150,
    )

    if not chunks:
        raise ValueError("No transcript chunks could be created.")

    # Step 5: Store chunks in ChromaDB.
    stored_ids = add_video_chunks(
        video_id=video_id,
        chunks=chunks,
    )

    # Step 6: Return ingestion metadata.
    return {
        "video_id": video_id,
        "language": transcript["language"],
        "language_code": transcript["language_code"],
        "is_generated": transcript["is_generated"],
        "transcription_method": transcription_method,
        "original_segments": len(transcript["segments"]),
        "cleaned_segments": len(cleaned_segments),
        "total_chunks": len(chunks),
        "stored_chunks": len(stored_ids),
        "status": "success",
    }
