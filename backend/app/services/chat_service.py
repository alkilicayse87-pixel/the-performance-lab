from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.retrieval.retriever import retrieve_chunks


# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# Temporary video ID for development
# This will later be replaced by the video selected by the user

def format_timestamp(seconds: float) -> str:
    """
    Convert seconds into MM:SS format.
    """

    total_seconds = int(seconds)

    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60

    return f"{minutes:02d}:{remaining_seconds:02d}"


def generate_answer(message: str, video_id: str) -> str:
    """
    Generate an answer using Retrieval-Augmented Generation.

    1. Retrieve relevant transcript chunks.
    2. Build the context from retrieved information.
    3. Generate an answer grounded in the video transcript.
    4. Include timestamps as references.
    """

    # Step 1: Retrieve relevant transcript chunks
    retrieved_chunks = retrieve_chunks(
        query=message,
        video_id=video_id,
        k=5,
    )

    # Stop if no relevant information was retrieved
    if not retrieved_chunks:
        return (
            "I could not find relevant information "
            "in the video transcript to answer your question."
        )

    # Step 2: Build the context
    context_parts = []

    for chunk in retrieved_chunks:
        start_time = format_timestamp(chunk["start_time"])
        end_time = format_timestamp(chunk["end_time"])

        context_parts.append(
            f"""
            [Timestamp: {start_time} - {end_time}]
            [Chunk: {chunk['chunk_index']}]

            {chunk['text']}
            """
        )

    context = "\n\n".join(context_parts)

    # Step 3: Define instructions for the AI
    instructions = """
    You are the AI Video Knowledge Assistant.

    Your task is to answer questions using ONLY the
    information provided in the video transcript context.

    Rules:

    1. Base your answers exclusively on the supplied context.
    2. Do not invent facts or introduce external information.
    3. If the context does not contain enough information,
        clearly explain that the video transcript does not
        provide a sufficient answer.
    4. Write clear, natural and informative answers.
    5. Organize longer answers into paragraphs or bullet points.

    6. TIMESTAMP CITATIONS ARE MANDATORY:
        - Every factual paragraph must include at least one timestamp.
        - Use the exact MM:SS timestamps provided in the context.
        - Place the timestamp at the end of the relevant paragraph.
        - Format: [MM:SS - MM:SS]
        - Never invent or estimate timestamps.
        - If a statement cannot be linked to a specific timestamp,
        do not present it as a fact.

    7. Do not claim that the video shows something visually:
        you only have access to its transcript.
    """

    # Step 4: Generate the answer
    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=instructions,
        input=f"""
        VIDEO TRANSCRIPT CONTEXT:

        {context}

        USER QUESTION:

        {message}

        ANSWER:
        """,
        max_output_tokens=700,
    )

    # Step 5: Build timestamp references directly from retrieved chunks
    references = []

    for chunk in retrieved_chunks:
        start_time = format_timestamp(chunk["start_time"])
        end_time = format_timestamp(chunk["end_time"])

        reference = (
            f"- [{start_time} - {end_time}] "
            f"Transcript segment {chunk['chunk_index']}"
        )

        references.append(reference)

    answer = response.output_text

    return (
        f"{answer}\n\n"
        "VIDEO REFERENCES:\n"
        + "\n".join(references)
    )