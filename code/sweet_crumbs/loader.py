"""Read TXT/Markdown/PDF documents, clean them, and keep source/page metadata."""
import logging
import re
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from .config import CHUNK_SIZE, CHUNK_OVERLAP, KNOWLEDGE_DIR

logging.getLogger("pypdf").setLevel(logging.ERROR)

def is_noise(line: str) -> bool:
    """Recognise page footers without removing ordinary references to pages."""
    return re.fullmatch(r"\s*page\s+\d+(?:\s+of\s+\d+)?\s*",line,re.I) is not None

def clean_text(text: str) -> str:
    """Remove page footers and redundant whitespace while keeping paragraphs."""
    lines = [line for line in text.splitlines() if not is_noise(line)]
    paragraphs = re.split(r"\n\s*\n","\n".join(lines))
    return "\n\n".join(cleaned for paragraph in paragraphs if (cleaned := " ".join(paragraph.split())))

def load_folder(folder: Path = KNOWLEDGE_DIR) -> tuple[list[Document], list[str]]:
    """Load supported files and report each unreadable file or textless PDF page."""
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Knowledge folder not found: {folder}")
    documents, skipped = [], []
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        source = path.relative_to(folder).as_posix()
        try:
            if path.suffix.lower() in (".txt",".md"):
                pages = [(1,path.read_text(encoding="utf-8-sig"))]
            elif path.suffix.lower() == ".pdf":
                reader = PdfReader(path)
                if reader.is_encrypted:
                    raise ValueError("password-protected PDF")
                pages = [(number,page.extract_text() or "") for number,page in enumerate(reader.pages,1)]
            else:
                skipped.append(f"{source}: unsupported file type {path.suffix}")
                continue
            for number,text in pages:
                cleaned = clean_text(text)
                if cleaned:
                    documents.append(Document(page_content=cleaned,metadata={"source":source,"page":number}))
                else:
                    skipped.append(f"{source}, page {number}: no text found; scanned pages need OCR")
        except (OSError, ValueError, PdfReadError) as error:
            skipped.append(f"{source}: {error}")
    return documents, skipped

def split_documents(documents: list[Document], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[Document]:
    """Produce overlapping chunks with source, page and a stable sequence number."""
    if not 0 <= overlap < chunk_size:
        raise ValueError("Require 0 <= overlap < chunk_size")
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=overlap)
    chunks = splitter.split_documents(documents)
    for number,chunk in enumerate(chunks,1):
        chunk.metadata["chunk"] = number
    return chunks

if __name__ == "__main__":
    from tempfile import TemporaryDirectory
    from pypdf import PdfWriter
    assert is_noise("Page 2 of 3") and is_noise("page 7")
    assert not is_noise("Page through the menu")
    assert clean_text("a   b\n\n\n\nPage 1 of 2\nc") == "a b\n\nc"
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root/"facts.txt").write_text("Price is 30,000 PKR. "*30,encoding="utf-8")
        (root/"notes.docx").write_bytes(b"unsupported")
        (root/"broken.pdf").write_bytes(b"broken")
        writer = PdfWriter()
        writer.add_blank_page(width=100,height=100)
        writer.write(root/"scanned.pdf")
        documents, skipped = load_folder(root)
        chunks = split_documents(documents,100,20)
        assert len(skipped) == 3 and len(chunks) > 1
        assert all(c.metadata["source"] == "facts.txt" and c.metadata["page"] == 1 for c in chunks)
    print("Loader: cleanup, metadata, damaged/scanned/unsupported file checks passed.")
