
def precision_at_k(
    retrieved_chunks: list[int],
    relevant_chunks: set[int],
    k: int = 3,
) -> float:
    """
    Calculate Precision@K for retrieved transcript chunks.

    Args:
        retrieved_chunks: Chunk indices returned by the retriever.
        relevant_chunks: Chunk indices manually judged as relevant.
        k: Number of top results to evaluate.

    Returns:
        Precision@K score between 0 and 1.
    """

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
