import re
from collections import Counter

import fitz

CAPTION_PATTERN = re.compile(r"^(table|tab\.)\s*\d+", re.IGNORECASE)

def extract_pdf_pages(file_path: str):
    document = fitz.open(file_path)

    body_size = get_body_font_size(document)
    last_heading = None

    pages = []

    for page_number, page in enumerate(document, start=1):
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

        pages.append({
            "page": page_number,
            "text": get_text_outside_tables(page, table_rects),
            "tables": tables
        })

    document.close()

    return pages

def get_body_font_size(document):
    # Most common font size, weighted by characters = body text size
    sizes = Counter()

    for page in document:
        for block in page.get_text("dict")["blocks"]:
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
