import pytest

from evaluation.retrieval_evaluation import precision_at_k


def test_precision_at_k_with_two_relevant_results():
    retrieved = [50, 51, 23]
    relevant = {50, 51}

    result = precision_at_k(retrieved, relevant, k=3)

    assert result == pytest.approx(2 / 3)


def test_precision_at_k_when_all_results_are_relevant():
    retrieved = [50, 51, 52]
    relevant = {50, 51, 52}

    result = precision_at_k(retrieved, relevant, k=3)

    assert result == 1.0


def test_precision_at_k_when_no_results_are_relevant():
    retrieved = [23, 24, 25]
    relevant = {50, 51}

    result = precision_at_k(retrieved, relevant, k=3)

    assert result == 0.0

def test_precision_at_k_rejects_zero_k():
    with pytest.raises(ValueError):
        precision_at_k([50, 51], {50}, k=0)


def test_precision_at_k_rejects_empty_relevant_chunks():
    with pytest.raises(ValueError):
        precision_at_k([50, 51], set(), k=2)


def test_precision_at_k_with_empty_retrieved_chunks():
    result = precision_at_k([], {50, 51}, k=3)

    assert result == 0.0