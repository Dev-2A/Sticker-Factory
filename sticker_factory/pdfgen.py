from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import List, Tuple

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader


@dataclass(frozen=True)
class SheetOptions:
    cols: int
    rows: int
    margin_mm: float
    gap_mm: float


GRID_PRESETS = {
    "3x5": (3, 5),
    "4x6": (4, 6),
    "5x7": (5, 7),
}


def _img_to_reader(img: Image.Image) -> ImageReader:
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return ImageReader(bio)


def make_a4_sheet_pdf(
    stickers: List[Image.Image],
    out_pdf_path: str,
    opts: SheetOptions,
) -> None:
    page_w, page_h = A4
    margin = opts.margin_mm * mm
    gap = opts.gap_mm * mm
    
    cols, rows = int(opts.cols), int(opts.rows)
    if cols <= 0 or rows <= 0:
        raise ValueError("cols/rows must be > 0")
    
    cell_w = (page_w - 2 * margin - (cols - 1) * gap) / cols
    cell_h = (page_h - 2 * margin - (rows - 1) * gap) / rows
    
    c = Canvas(out_pdf_path, pagesize=A4)
    
    # Place stickerse row-major, repeating if stickers < cells, truncating if more
    total_cells = cols * rows
    if not stickers:
        # still create an empty sheet
        c.showPage()
        c.save()
        return
    
    for i in range(total_cells):
        r = i // cols
        col = i % cols
        
        x0 = margin + col * (cell_w + gap)
        y0 = page_h - margin - (r + 1) * cell_h - r * gap   # from top
        
        img = stickers[i % len(stickers)]
        iw, ih = img.size
        
        # Fit image inside cell maintaining aspect ratio
        scale = min(cell_w / iw, cell_h / ih)
        draw_w = iw * scale
        draw_h = ih * scale
        
        x = x0 + (cell_w - draw_w) / 2
        y = y0 + (cell_h - draw_h) / 2
        
        c.drawImage(_img_to_reader(img), x, y, width=draw_w, height=draw_h, mask="auto")
    
    c.showPage()
    c.save()