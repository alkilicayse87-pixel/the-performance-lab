from app.retrieval.retriever import retrieve_chunks


VIDEO_ID = "oCNx8Xa-oug"

QUESTION = "How does the swimmer perform the freestyle arm stroke?"


def main():
    print("\n--- EVALUATION CHUNK INSPECTION ---")
    print("\nQUESTION:", QUESTION)

    results = retrieve_chunks(
        query=QUESTION,
        video_id=VIDEO_ID,
        k=5,
    )

    for rank, result in enumerate(results, start=1):
        print("\n" + "=" * 80)
        print(f"RANK: {rank}")
        print(f"CHUNK: {result['chunk_index']}")
        print(
            f"TIMESTAMP: {result['start_time']:.2f}s - "
            f"{result['end_time']:.2f}s"
        )
        print("\nFULL TEXT:")
        print(result["text"])


if __name__ == "__main__":
    main()