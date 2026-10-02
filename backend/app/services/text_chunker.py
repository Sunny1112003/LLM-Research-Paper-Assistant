from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.pdf_reader import PDFPage


@dataclass(frozen=True)
class DocumentChunk:
    text: str
    page: int
    chunk_index: int


def chunk_pages(pages: list[PDFPage]) -> list[DocumentChunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks: list[DocumentChunk] = []

    for page in pages:
        text = page.text.strip()
        if not text:
            continue
        for index, chunk in enumerate(splitter.split_text(text)):
            if chunk.strip():
                chunks.append(DocumentChunk(chunk.strip(), page.page, index))

    return chunks
