import os
import sys

import psycopg
from dotenv import load_dotenv
from pgvector import Vector
from pgvector.psycopg import register_vector

from app.vector_store.chroma_store import get_vector_store


EXPECTED_DIMENSION = 1536
EXPECTED_RECORDS = 284


def main():
    load_dotenv("../.env")

    database_url = os.getenv("NEON_DATABASE_URL")
    if not database_url:
        raise RuntimeError("NEON_DATABASE_URL non configurata.")

    collection = get_vector_store()._collection

    data = collection.get(
        include=["documents", "metadatas", "embeddings"]
    )

    ids = data["ids"]
    documents = data["documents"]
    metadatas = data["metadatas"]
    embeddings = data["embeddings"]

    total = len(ids)

    if total != EXPECTED_RECORDS:
        raise RuntimeError(
            f"Attesi {EXPECTED_RECORDS} record, trovati {total}. Migrazione interrotta."
        )

    if not all(len(embedding) == EXPECTED_DIMENSION for embedding in embeddings):
        raise RuntimeError("Trovato un embedding con dimensione diversa da 1536.")

    rows = []

    for chunk_id, content, metadata, embedding in zip(
        ids, documents, metadatas, embeddings
    ):
        required = [
            "video_id",
            "chunk_index",
            "start_time",
            "end_time",
            "segment_count",
            "segment_indices",
        ]

        missing = [key for key in required if key not in metadata]
        if missing:
            raise RuntimeError(
                f"Metadati mancanti per il chunk {chunk_id}: {missing}"
            )

        segment_indices = [
            int(value)
            for value in str(metadata["segment_indices"]).split(",")
            if value.strip()
        ]

        rows.append((
            chunk_id,
            metadata["video_id"],
            int(metadata["chunk_index"]),
            content,
            float(metadata["start_time"]),
            float(metadata["end_time"]),
            int(metadata["segment_count"]),
            segment_indices,
            Vector(embedding.tolist()),
        ))

    with psycopg.connect(database_url) as conn:
        register_vector(conn)

        existing = conn.execute(
            "SELECT COUNT(*) FROM video_chunks"
        ).fetchone()[0]

        if existing != 0:
            raise RuntimeError(
                f"Neon contiene giÃ  {existing} record. Nessun dato inserito."
            )

        conn.cursor().executemany(
            """
            INSERT INTO video_chunks (
                id,
                video_id,
                chunk_index,
                content,
                start_time,
                end_time,
                segment_count,
                segment_indices,
                embedding
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            rows,
        )

        migrated = conn.execute(
            "SELECT COUNT(*) FROM video_chunks"
        ).fetchone()[0]

        if migrated != EXPECTED_RECORDS:
            raise RuntimeError(
                f"Verifica fallita: Neon contiene {migrated} record."
            )

        print(f"Migrazione completata: {migrated} record.")
        print("Dimensione embedding: 1536")
        print("ChromaDB: origine non modificata.")


if __name__ == "__main__":
    main()
