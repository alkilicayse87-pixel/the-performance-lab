
from app.ingestion.youtube_transcript import (
    extract_video_id,
    fetch_youtube_transcript,
)

from app.processing.transcript_processor import (
    clean_segments,
    create_chunks,
)


VIDEO_URL = "https://www.youtube.com/watch?v=oCNx8Xa-oug"


def main():
    video_id = extract_video_id(VIDEO_URL)

    transcript = fetch_youtube_transcript(
        video_id,
        languages=["en"],
    )

    raw_segments = transcript["segments"]

    cleaned_segments = clean_segments(raw_segments)

    chunks = create_chunks(
        cleaned_segments,
        chunk_size=1000,
        overlap=150,
    )

    print("\n--- TRANSCRIPT PROCESSING TEST ---")

    print("Original segments:", len(raw_segments))
    print("Cleaned segments:", len(cleaned_segments))
    print("Removed segments:", len(raw_segments) - len(cleaned_segments))
    print("Generated chunks:", len(chunks))

    print(
        "All chunks within 1000 characters:",
        all(len(chunk["text"]) <= 1000 for chunk in chunks),
    )

    print(
        "Valid timestamps:",
        all(chunk["start_time"] < chunk["end_time"] for chunk in chunks),
    )

    print("\n--- CHUNK DETAILS ---")

    for chunk in chunks:
        print(
            f"Chunk {chunk['chunk_index']}: "
            f"{len(chunk['text'])} chars | "
            f"{chunk['start_time']:.2f}s - "
            f"{chunk['end_time']:.2f}s | "
            f"{chunk['segment_count']} segments"
        )
    
    print("\n--- OVERLAP TEST ---")

    for i in range(1, len(chunks)):
        previous_indices = chunks[i - 1]["segment_indices"]
        current_indices = chunks[i]["segment_indices"]

        overlap_count = 0
        max_overlap = min(
            len(previous_indices),
            len(current_indices),
        )

        for size in range(1, max_overlap + 1):
            if previous_indices[-size:] == current_indices[:size]:
                overlap_count = size

        print(
            f"Chunk {i - 1} -> Chunk {i}: "
            f"{overlap_count} shared segments"
        )

        print("Shared segment indices:", current_indices[:overlap_count])

if __name__ == "__main__":
    main()
