import os

import fitz
from dotenv import load_dotenv

load_dotenv()

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "25")) * 1024 * 1024
MAX_PDF_PAGES = int(os.getenv("MAX_PDF_PAGES", "500"))

# The PDF spec allows junk before the header, readers look in the first 1 KB
PDF_SIGNATURE = b"%PDF-"
SIGNATURE_WINDOW = 1024

class InvalidPDFError(Exception):
    def __init__(self, message, status_code=422):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def validate_pdf(data: bytes):
    # Cheapest checks first: size, then signature, then parsing
    if len(data) == 0:
        raise InvalidPDFError("File is empty")

    if len(data) > MAX_UPLOAD_BYTES:
        raise InvalidPDFError(
            f"File is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB",
            status_code=413
        )

    if PDF_SIGNATURE not in data[:SIGNATURE_WINDOW]:
        raise InvalidPDFError("Not a PDF file (missing %PDF- signature)", status_code=415)

    try:
        document = fitz.open(stream=data, filetype="pdf")
    except Exception as e:
        raise InvalidPDFError(f"Corrupt PDF: {e}") from e

    try:
        # needs_pass: a user password is required to read it.
        # is_encrypted alone is too strict: owner-password PDFs open fine.
        if document.needs_pass:
            raise InvalidPDFError("PDF is password protected")

        if document.page_count == 0:
            raise InvalidPDFError("PDF has no pages")

        if document.page_count > MAX_PDF_PAGES:
            raise InvalidPDFError(
                f"PDF has {document.page_count} pages, limit is {MAX_PDF_PAGES}"
            )
    finally:
        document.close()
