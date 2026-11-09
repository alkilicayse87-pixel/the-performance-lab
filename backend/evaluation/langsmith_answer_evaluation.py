
import json
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langsmith import evaluate
from langchain_openai import ChatOpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.retrieval.retriever import retrieve_all_chunks
from app.services.agent_service import generate_agent_answer


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATASET_NAME = "THE PERFORMANCE LAB - Evaluation v1"

judge = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0,
)


def answer_target(inputs: dict) -> dict:
    """Generate an answer and collect the transcript evidence."""

    question = inputs["question"]
    video_id = inputs["video_id"]

    conversation_id = f"evaluation-{uuid.uuid4()}"

    answer = generate_agent_answer(
        message=question,
        video_id=video_id,
        conversation_id=conversation_id,
    )

    chunks = retrieve_all_chunks(video_id)

    context = "\n\n".join(
        chunk["text"] for chunk in chunks
    )

    return {
        "answer": answer,
        "context": context,
    }


def judge_answer(question, reference, answer, context, criterion):
    """Use an LLM judge to score one answer-quality criterion."""

    prompt = f"""
You are an independent evaluator of an AI sports science assistant.

Evaluate the answer using the criterion below.

CRITERION:
{criterion}

QUESTION:
{question}

REFERENCE ANSWER:
{reference}

TRANSCRIPT EVIDENCE:
{context}

AI ANSWER:
{answer}

Scoring:
- 1.0 = fully satisfies the criterion
- 0.5 = partially satisfies the criterion
- 0.0 = fails the criterion

Return ONLY valid JSON with this structure:
{{
    "score": 0.0,
    "reason": "Brief explanation of the score."
}}

Use only the supplied question, reference answer and transcript evidence.
Do not reward unsupported claims.
"""

    response = judge.invoke(prompt)
    result = json.loads(response.content)

    score = float(result["score"])

    if score not in (0.0, 0.5, 1.0):
        raise ValueError(f"Invalid evaluation score: {score}")

    return {
        "score": score,
        "comment": result["reason"],
    }


def evaluate_correctness(run, example):
    result = judge_answer(
        question=example.inputs["question"],
        reference=example.outputs["reference_answer"],
        answer=run.outputs["answer"],
        context=run.outputs["context"],
        criterion=(
            "CORRECTNESS: Is the answer factually correct and consistent "
            "with the reference answer and transcript?"
        ),
    )

    return {"key": "correctness", **result}


def evaluate_relevance(run, example):
    result = judge_answer(
        question=example.inputs["question"],
        reference=example.outputs["reference_answer"],
        answer=run.outputs["answer"],
        context=run.outputs["context"],
        criterion=(
            "RELEVANCE: Does the answer directly address the question "
            "without unnecessary or unrelated information?"
        ),
    )

    return {"key": "relevance", **result}


def evaluate_groundedness(run, example):
    result = judge_answer(
        question=example.inputs["question"],
        reference=example.outputs["reference_answer"],
        answer=run.outputs["answer"],
        context=run.outputs["context"],
        criterion=(
            "GROUNDEDNESS: Are the factual claims in the answer supported "
            "by the supplied transcript evidence? Penalize unsupported claims."
        ),
    )

    return {"key": "groundedness", **result}


if __name__ == "__main__":
    print("Starting LangSmith answer-quality evaluation...")

    results = evaluate(
        answer_target,
        data=DATASET_NAME,
        evaluators=[
            evaluate_correctness,
            evaluate_relevance,
            evaluate_groundedness,
        ],
        experiment_prefix="performance-lab-answer-quality",
        metadata={
            "evaluation_type": "answer_quality",
            "dataset_version": "v1",
            "judge_model": OPENAI_MODEL,
        },
    )

    print("\nAnswer-quality evaluation completed.")
    print(results)