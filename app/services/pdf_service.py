import fitz

def extract_pdf_pages(file_path: str):
    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        pages.append({
            "page": page_number,
            "text": page.get_text()
        })

    document.close()

    return pages
