import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector

from app.config import NEON_DATABASE_URL
from app.vector_store.chroma_store import get_embeddings


def get_connection():
    """Open a connection to the Neon PostgreSQL database."""
    if not NEON_DATABASE_URL:
        raise RuntimeError("NEON_DATABASE_URL non configurata.")

    conn = psycopg.connect(NEON_DATABASE_URL)
    register_vector(conn)
    return conn


def retrieve_chunks(
    query: str,
    video_id: str | None = None,
    k: int = 5,
) -> list[dict]:
    """Retrieve the most relevant transcript chunks from Neon."""

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if k <= 0:
        raise ValueError("k must be greater than zero.")

    query_embedding = get_embeddings().embed_query(query)

    sql = """
        SELECT
            content,
            video_id,
            chunk_index,
            start_time,
            end_time,
            segment_count
        FROM video_chunks
        WHERE (%s::text IS NULL OR video_id = %s)
        ORDER BY embedding <-> %s
        LIMIT %s
    """

    with get_connection() as conn:
        rows = conn.execute(
            sql,
            (video_id, video_id, Vector(query_embedding), k),
        ).fetchall()

    return [
        {
            "text": row[0],
            "video_id": row[1],
            "chunk_index": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "segment_count": row[5],
        }
        for row in rows
    ]


def retrieve_all_chunks(video_id: str) -> list[dict]:
    """Retrieve all transcript chunks for a specific video."""

    if not video_id:
        raise ValueError("Video ID cannot be empty.")

    sql = """
        SELECT
            content,
            video_id,
            chunk_index,
            start_time,
            end_time,
            segment_count
        FROM video_chunks
        WHERE video_id = %s
        ORDER BY start_time
    """

    with get_connection() as conn:
        rows = conn.execute(sql, (video_id,)).fetchall()

    return [
        {
            "text": row[0],
            "video_id": row[1],
            "chunk_index": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "segment_count": row[5],
        }
        for row in rows
    ]


def get_cached_video_chunks(video_id: str) -> list[dict]:
    """Retrieve cached transcript chunks, including segment indices."""

    if not video_id:
        raise ValueError("video_id cannot be empty.")

    sql = """
        SELECT
            content,
            video_id,
            chunk_index,
            start_time,
            end_time,
            segment_count,
            segment_indices
        FROM video_chunks
        WHERE video_id = %s
        ORDER BY chunk_index
    """

    with get_connection() as conn:
        rows = conn.execute(sql, (video_id,)).fetchall()

    return [
        {
            "text": row[0],
            "video_id": row[1],
            "chunk_index": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "segment_count": row[5],
            "segment_indices": row[6],
        }
        for row in rows
    ]