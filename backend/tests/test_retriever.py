
from app.retrieval.retriever import retrieve_chunks


VIDEO_ID = "oCNx8Xa-oug"


def main():
    test_queries = [
        "Which muscles are involved in the freestyle swimming stroke?",
        "How should the kick and pull timing be coordinated in sprint freestyle?",
        "What is the role of strength training in swimming performance?",
    ]

    print("\n--- RETRIEVAL MODULE TEST ---")

    for query in test_queries:
        print("\n" + "=" * 70)
        print("QUERY:", query)

        results = retrieve_chunks(
            query=query,
            video_id=VIDEO_ID,
            k=3,
        )

        print("Results found:", len(results))

        for rank, result in enumerate(results, start=1):
            print(f"\nResult {rank}")
            print("Video ID:", result["video_id"])
            print("Chunk:", result["chunk_index"])
            print(
                "Timestamp:",
                f"{result['start_time']:.2f}s - "
                f"{result['end_time']:.2f}s",
            )
            print("Text:", result["text"][:350])


if __name__ == "__main__":
    main()
