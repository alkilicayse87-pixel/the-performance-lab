from pathlib import Path

from dotenv import load_dotenv
from langsmith import evaluate

from app.retrieval.retriever import retrieve_chunks


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATASET_NAME = "THE PERFORMANCE LAB - Evaluation v1"
K = 5


def retrieval_target(inputs: dict) -> dict:
    """Retrieve the top-k transcript chunks for one evaluation question."""

    question = inputs["question"]
    video_id = inputs["video_id"]

    chunks = retrieve_chunks(
        query=question,
        video_id=video_id,
        k=K,
    )

    return {
        "retrieved_chunk_indices": [
            chunk["chunk_index"] for chunk in chunks
        ],
        "retrieved_count": len(chunks),
    }


def hit_rate_at_5(run, example) -> dict:
    """Check whether at least one relevant chunk appears in the top 5."""

    retrieved = run.outputs["retrieved_chunk_indices"]
    relevant = set(example.outputs["relevant_chunks"])

    hit = any(chunk in relevant for chunk in retrieved)

    return {
        "key": "hit_rate_at_5",
        "score": float(hit),
    }


def precision_at_5(run, example) -> dict:
    """Calculate the proportion of relevant chunks in the top 5."""

    retrieved = run.outputs["retrieved_chunk_indices"]
    relevant = set(example.outputs["relevant_chunks"])

    relevant_count = sum(
        1 for chunk in retrieved[:K] if chunk in relevant
    )

    return {
        "key": "precision_at_5",
        "score": relevant_count / K,
    }


if __name__ == "__main__":
    print("Starting LangSmith retrieval evaluation...")

    results = evaluate(
        retrieval_target,
        data=DATASET_NAME,
        evaluators=[
            hit_rate_at_5,
            precision_at_5,
        ],
        experiment_prefix="performance-lab-retrieval-k5",
        metadata={
            "evaluation_type": "retrieval",
            "k": K,
            "dataset_version": "v1",
        },
    )

    print("\nEvaluation completed.")
    print(results)