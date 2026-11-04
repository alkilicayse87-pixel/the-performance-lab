
from evaluation.retrieval_evaluation import precision_at_k


def main():
    print("\n--- PRECISION@K TEST ---")

    # Test 1: Three results, two relevant
    retrieved = [50, 51, 23]
    relevant = {50, 51}

    score = precision_at_k(
        retrieved_chunks=retrieved,
        relevant_chunks=relevant,
        k=3,
    )

    print("\nTest 1: Two relevant results out of three")
    print("Expected:", 2 / 3)
    print("Actual:", score)
    print("Passed:", abs(score - 2 / 3) < 0.000001)

    # Test 2: All results relevant
    retrieved = [50, 51, 52]
    relevant = {50, 51, 52}

    score = precision_at_k(retrieved, relevant, k=3)

    print("\nTest 2: All results relevant")
    print("Expected: 1.0")
    print("Actual:", score)
    print("Passed:", score == 1.0)

    # Test 3: No results relevant
    retrieved = [23, 24, 25]
    relevant = {50, 51}

    score = precision_at_k(retrieved, relevant, k=3)

    print("\nTest 3: No results relevant")
    print("Expected: 0.0")
    print("Actual:", score)
    print("Passed:", score == 0.0)


if __name__ == "__main__":
    main()