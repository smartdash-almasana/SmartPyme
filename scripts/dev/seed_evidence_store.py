# This is a standalone script to seed the evidence store for validation.

import json
import os
from pathlib import Path

from models.document_models import DocumentChunk

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ROOT = REPO_ROOT / "evidence_store"
CHUNKS_DIR = EVIDENCE_ROOT / "document_chunks"
CHUNKS_FILE = CHUNKS_DIR / "chunks.jsonl"

def seed():
    print("Initializing evidence store...")
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    if CHUNKS_FILE.exists():
        os.remove(CHUNKS_FILE)

    print("Seeding with test evidence chunk 'test-evidence-001'...")

    # Create a sample DocumentChunk
    seed_chunk = DocumentChunk(
        chunk_id="test-evidence-001",
        source_id="src-test-001",
        filename="test_document.pdf",
        page=1,
        text="This is the content of the test evidence chunk.",
        metadata={"author": "test_suite"}
    )

    # Pydantic models have a .model_dump() method to get a dict
    chunk_dict = seed_chunk.model_dump(mode="json")

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        f.write(f'{json.dumps(chunk_dict, ensure_ascii=False)}\n')

    print("Seeding complete.")

if __name__ == "__main__":
    seed()
