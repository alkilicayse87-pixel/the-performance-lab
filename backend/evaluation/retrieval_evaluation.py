from app.retrieval.retriever import retrieve_chunks
from evaluation.evaluation_dataset import EVALUATION_DATASET


def precision_at_k(
    retrieved_chunks: list[int],
    relevant_chunks: set[int],
    k: int = 3,
) -> float:
    """Calculate Precision@K for retrieved transcript chunks."""

    if k <= 0:
        raise ValueError("k must be greater than zero.")

    if not relevant_chunks:
        raise ValueError("Relevant chunks cannot be empty.")

    top_k = retrieved_chunks[:k]

    relevant_count = sum(
        1 for chunk in top_k
        if chunk in relevant_chunks
    )

    return relevant_count / k


def evaluate_retrieval(
    dataset: list[dict] | None = None,
    k: int = 3,
) -> dict:
    """Evaluate video-specific retrieval using Precision@K."""

    if k <= 0:
        raise ValueError("k must be greater than zero.")

    evaluation_data = (
        EVALUATION_DATASET if dataset is None else dataset
    )

    if not evaluation_data:
        raise ValueError("Evaluation dataset cannot be empty.")

    results = []

    for item in evaluation_data:
        retrieved = retrieve_chunks(
            query=item["question"],
            video_id=item["video_id"],
            k=k,
        )

        retrieved_indices = [
            chunk["chunk_index"]
            for chunk in retrieved
        ]

        score = precision_at_k(
            retrieved_chunks=retrieved_indices,
            relevant_chunks=item["relevant_chunks"],
            k=k,
        )

        results.append({
            "question": item["question"],
            "video_id": item["video_id"],
            "relevant_chunks": sorted(item["relevant_chunks"]),
            "retrieved_chunks": retrieved_indices,
            "precision_at_k": score,
        })

    average_precision = sum(
        result["precision_at_k"] for result in results
    ) / len(results)

    return {
        "k": k,
        "total_questions": len(results),
        "average_precision_at_k": average_precision,
        "results": results,
    }