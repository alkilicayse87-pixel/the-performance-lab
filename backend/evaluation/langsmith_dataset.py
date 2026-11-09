
import os
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client

from evaluation.evaluation_dataset import EVALUATION_DATASET


# Load environment variables from the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATASET_NAME = "THE PERFORMANCE LAB - Evaluation v1"

REFERENCE_ANSWERS = [
    "Exercise can improve mood, focus and memory. Team sports also develop trust, cooperation and mutual support.",
    "Team sports can improve self-esteem and confidence through skill development and a growth mindset. Experiencing defeat can help build resilience.",
    "A single workout can improve attention, focus and reaction time. The attention improvement can last at least two hours.",
    "Long-term exercise can increase hippocampal volume, support long-term memory and improve attention functions associated with the prefrontal cortex.",
    "Heart rate and stroke volume both increase during exercise.",
    "Exercise increases the number of capillaries in muscle tissue, allowing more oxygen to reach the muscles.",
    "Injury prevention involves a comprehensive approach including warm-ups, strength training, recovery and movement practice.",
    "The transcript recommends practising the movements every day for two sets. It also emphasizes precise and controlled execution. The exact repetition count is unclear in the transcript.",
    "Sleep supports muscle repair, hormone release and immune function. Nutrition and hydration provide energy and support muscle rebuilding.",
    "Ice is recommended for acute injuries and new swelling. Heat is recommended for chronic pain, muscle spasms and stiff joints, but not for new injuries.",
    "Maximal strength is the maximum force a muscle can produce. Explosive strength is the ability to produce force rapidly.",
    "Explosive training produces neural adaptations specific to the ability to generate force quickly."
]


def create_langsmith_dataset():
    api_key = os.getenv("LANGSMITH_API_KEY")

    if not api_key:
        raise ValueError("LANGSMITH_API_KEY is missing from the project .env file.")

    client = Client(api_key=api_key)

    # Check whether the dataset already exists
    existing_datasets = list(
        client.list_datasets(dataset_name=DATASET_NAME)
    )

    if existing_datasets:
        print(f"Dataset already exists: {DATASET_NAME}")
        print("No duplicate dataset was created.")
        return

    # Create the dataset
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=(
            "Evaluation dataset for THE PERFORMANCE LAB. "
            "Contains 12 questions across six YouTube sports science videos, "
            "with reference answers and relevant transcript chunk IDs."
        ),
    )

    inputs = []
    outputs = []

    for item, reference_answer in zip(
        EVALUATION_DATASET,
        REFERENCE_ANSWERS,
    ):
        inputs.append({
            "question": item["question"],
            "video_id": item["video_id"],
        })

        outputs.append({
            "reference_answer": reference_answer,
            "relevant_chunks": sorted(item["relevant_chunks"]),
        })

    # Add all evaluation examples
    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        dataset_id=dataset.id,
    )

    print("LangSmith dataset created successfully.")
    print(f"Dataset name: {DATASET_NAME}")
    print(f"Total examples: {len(inputs)}")


if __name__ == "__main__":
    create_langsmith_dataset()