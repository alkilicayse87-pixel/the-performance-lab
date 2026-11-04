
from app.ingestion.youtube_transcript import (
    extract_video_id,
    fetch_youtube_transcript,
)

from app.processing.transcript_processor import (
    clean_segments,
    create_chunks,
)

from app.vector_store.chroma_store import (
    add_video_chunks,
    get_vector_store,
)


VIDEO_URL = "https://www.youtube.com/watch?v=oCNx8Xa-oug"


def main():
    # 1. Retrieve YouTube transcript
    video_id = extract_video_id(VIDEO_URL)

    transcript = fetch_youtube_transcript(
        video_id,
        languages=["en"],
    )

    # 2. Clean transcript
    cleaned_segments = clean_segments(
        transcript["segments"]
    )

    # 3. Create chunks
    chunks = create_chunks(
        cleaned_segments,
        chunk_size=1000,
        overlap=150,
    )

    print("\n--- VECTOR STORE INSERTION ---")

    print("Video ID:", video_id)
    print("Chunks to insert:", len(chunks))

    # 4. Insert chunks into ChromaDB
    ids = add_video_chunks(
        video_id=video_id,
        chunks=chunks,
    )

    print("Inserted chunk IDs:", len(ids))

    # 5. Verify database contents
    vector_store = get_vector_store()

    print("Total documents in database:", vector_store._collection.count())

    # 6. Test semantic retrieval
    query = "Which muscles are involved in the freestyle swimming stroke and in what order?"

    results = vector_store.similarity_search(
        query,
        k=3,
        filter={"video_id": video_id},
    )

    print("\n--- SEMANTIC SEARCH TEST ---")

    print("Query:", query)
    print("Results found:", len(results))

    for index, document in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Video ID:", document.metadata["video_id"])
        print("Chunk:", document.metadata["chunk_index"])
        print(
            "Timestamp:",
            document.metadata["start_time"],
            "-",
            document.metadata["end_time"],
        )
        print("Text:", document.page_content[:300])


if __name__ == "__main__":
    main()
