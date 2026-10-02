from dataclasses import dataclass

from pypdf import PdfReader


@dataclass(frozen=True)
class PDFPage:
    page: int
    text: str


def read_pdf(pdf_path: str) -> list[PDFPage]:
    reader = PdfReader(pdf_path)
    return [
        PDFPage(page_number, page.extract_text() or "")
        for page_number, page in enumerate(reader.pages, start=1)
    ]
