"""Lesson 3.4: load and chunk a knowledge folder. An optional folder argument overrides the demo."""
import argparse
from collections import Counter
from pathlib import Path
from sweet_crumbs.config import BASE, KNOWLEDGE_DIR
from sweet_crumbs.data import write_json
from sweet_crumbs.loader import load_folder, split_documents

def main() -> None:
    """Print an owner-readable loading report and save the sourced chunks for RAG."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder",nargs="?",type=Path,default=KNOWLEDGE_DIR)
    args = parser.parse_args()
    try:
        documents, skipped = load_folder(args.folder)
        chunks = split_documents(documents)
        for source,count in Counter(c.metadata["source"] for c in chunks).items():
            print(f"Loaded {source}: {count} chunks")
        for reason in skipped:
            print(f"Skipped {reason}")
        print(f"{len(documents)} document pages -> {len(chunks)} chunks; ~{round(sum(len(c.page_content) for c in chunks)/4)} tokens")
        if chunks:
            print(f"First chunk: {chunks[0].metadata}\n{chunks[0].page_content[:200]}")
        write_json(BASE / "chunks.json",[{"text":c.page_content,**c.metadata} for c in chunks])
        print("Saved chunks.json for the next RAG lesson.")
    except (OSError, ValueError) as error:
        print(f"Loader could not finish: {error}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
