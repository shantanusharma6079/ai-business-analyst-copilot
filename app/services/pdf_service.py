import os
import re
from collections import Counter

import fitz
import pytesseract
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

if os.getenv("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")

CAPTION_PATTERN = re.compile(r"^(table|tab\.)\s*\d+", re.IGNORECASE)

# A page with less native text than this is treated as a scanned image
OCR_MIN_CHARS = 50
# Tesseract works best when text is ~20-30px tall: 300 DPI gets 11pt text there
OCR_DPI = 300

# Problems with the environment, not the page: these fail the whole document
SYSTEM_ERRORS = (pytesseract.TesseractNotFoundError, MemoryError)

def extract_pdf_pages(file_path: str):
    document = fitz.open(file_path, filetype="pdf")

    body_size = get_body_font_size(document)
    last_heading = None

    pages = []

    for page_number, page in enumerate(document, start=1):
        # One broken page is skipped instead of failing the whole document
        try:
            extracted, last_heading = extract_page(page, page_number, body_size, last_heading)
        except SYSTEM_ERRORS:
            raise
        except Exception as e:
            extracted = {
                "page": page_number,
                "text": "",
                "tables": [],
                "ocr_confidence": None,
                "error": f"{type(e).__name__}: {e}"[:200]
            }

        pages.append(extracted)

    document.close()

    return pages

def extract_page(page, page_number, body_size, last_heading):
    if is_scanned(page):
        text, confidence = ocr_page(page)
        return {
            "page": page_number,
            "text": text,
            "tables": [],
            "ocr_confidence": confidence
        }, last_heading

    table_rects = []
    tables = []
    lines = get_lines(page)

    for table in page.find_tables().tables:
        rect = fitz.Rect(table.bbox)
        table_rects.append(rect)
        tables.append({"rect": rect, "markdown": clean_markdown(table.to_markdown())})

    headings = [
        line for line in lines
        if is_heading(line, body_size) and not overlaps_any(line["rect"], table_rects)
    ]

    for table in tables:
        heading = find_heading_above(headings, table["rect"]) or last_heading
        caption = find_caption_below(lines, table["rect"])
        table["heading"] = heading
        table["caption"] = caption
        del table["rect"]

    if headings:
        last_heading = headings[-1]["text"]

    return {
        "page": page_number,
        "text": get_text_outside_tables(page, table_rects),
        "tables": tables,
        "ocr_confidence": None
    }, last_heading

def is_scanned(page):
    return len(page.get_text().strip()) < OCR_MIN_CHARS

def ocr_page(page):
    pixmap = page.get_pixmap(dpi=OCR_DPI)
    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    # Rebuild text line by line; Tesseract numbers blocks, paragraphs and lines
    lines = {}
    total_weight = 0
    weighted_confidence = 0

    for i, word in enumerate(data["text"]):
        word = word.strip()
        confidence = float(data["conf"][i])

        # -1 marks layout boxes, not words
        if not word or confidence < 0:
            continue

        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines.setdefault(key, []).append(word)

        # Weight by length so a misread long word counts more than a stray "a"
        total_weight += len(word)
        weighted_confidence += confidence * len(word)

    text = ""
    previous = None

    for key in sorted(lines):
        if previous is not None:
            text += "\n\n" if key[:2] != previous[:2] else "\n"
        text += " ".join(lines[key])
        previous = key

    confidence = round(weighted_confidence / total_weight, 1) if total_weight else None

    return text, confidence

def get_body_font_size(document):
    # Most common font size, weighted by characters = body text size
    sizes = Counter()

    for page in document:
        try:
            blocks = page.get_text("dict")["blocks"]
        except Exception:
            # Broken pages are reported by extract_page; skip them here
            continue
        for block in blocks:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    sizes[round(span["size"], 1)] += len(span["text"].strip())

    return sizes.most_common(1)[0][0] if sizes else 0

def get_lines(page):
    lines = []

    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans = line["spans"]
            text = "".join(span["text"] for span in spans).strip()
            if not text:
                continue
            lines.append({
                "text": text,
                "rect": fitz.Rect(line["bbox"]),
                "size": max(span["size"] for span in spans),
                "bold": any(span["flags"] & 16 for span in spans)
            })

    lines.sort(key=lambda line: line["rect"].y0)

    return lines

def is_heading(line, body_size):
    if len(line["text"]) > 100:
        return False
    return line["bold"] or line["size"] > body_size * 1.15

def overlaps_any(rect, rects):
    return any(rect.intersects(other) for other in rects)

def find_heading_above(headings, table_rect):
    above = [h for h in headings if h["rect"].y1 <= table_rect.y0]
    return above[-1]["text"] if above else None

def find_caption_below(lines, table_rect, max_gap=30):
    for line in lines:
        if table_rect.y1 <= line["rect"].y0 <= table_rect.y1 + max_gap:
            if CAPTION_PATTERN.match(line["text"]):
                return line["text"]
    return None

def get_text_outside_tables(page, table_rects):
    # Drop text blocks inside tables so table content is not indexed twice
    blocks = page.get_text("blocks", sort=True)

    return "".join(
        block[4] for block in blocks
        if not overlaps_any(fitz.Rect(block[:4]), table_rects)
    )

def clean_markdown(markdown):
    return markdown.replace("<br>", " ").strip()
