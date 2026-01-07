from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from math import ceil

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas


@dataclass(frozen=True)
class SheetOptions:
    cols: int
    rows: int
    margin_mm: float
    gap_mm: float
    show_cut_guides: bool = False


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


def _draw_cut_guides(
    c: Canvas,
    page_w: float,
    page_h: float,
    cols: int,
    rows: int,
    margin: float,
    gap: float,
    cell_w: float,
    cell_h: float,
) -> None:
    """
    Draw thin grid lines around each cell (cut guides).
    """
    # Use thin default stroke. (No explicit color t o keep it simple.)
    c.setLineWidth(0.3)
    
    for r in range(rows):
        for col in range(cols):
            x0 = margin + col * (cell_w + gap)
            y0 = page_h - margin - (r + 1) * cell_h - r * gap
            c.rect(x0, y0, cell_w, cell_h, stroke=1, fill=0)


def make_a4_sheet_pdf(
    stickers: list[Image.Image],
    out_pdf_path: str,
    opts: SheetOptions,
) -> None:
    page_w, page_h = A4
    margin = float(opts.margin_mm) * mm
    gap = float(opts.gap_mm) * mm
    
    cols, rows = int(opts.cols), int(opts.rows)
    if cols <= 0 or rows <= 0:
        raise ValueError("cols/rows must be > 0")
    
    cell_w = (page_w - 2 * margin - (cols - 1) * gap) / cols
    cell_h = (page_h - 2 * margin - (rows - 1) * gap) / rows
    if cell_w <= 0 or cell_h <= 0:
        raise ValueError("Invalid layout: Cell size <= 0 (check margin/gap/cols/rows).")
    
    c = Canvas(out_pdf_path, pagesize=A4)
    
    # Place stickerse row-major, repeating if stickers < cells, truncating if more
    total_cells = cols * rows
    
    if not stickers:
        # still create an empty sheet
        if opts.show_cut_guides:
            _draw_cut_guides(c, page_w, page_h, cols, rows, margin, gap, cell_w, cell_h)
        c.showPage()
        c.save()
        return
    
    if len(stickers) <= total_cells:
        num_pages = 1
    else:
        num_pages = ceil(len(stickers) / total_cells)
    
    idx = 0
    for _page in range(num_pages):
        if opts.show_cut_guides:
            _draw_cut_guides(c, page_w, page_h ,cols, rows, margin, gap, cell_w, cell_h)
        
        for cell_i in range(total_cells):    
            r = cell_i // cols
            col = cell_i % cols
            
            x0 = margin + col * (cell_w + gap)
            y0 = page_h - margin - (r + 1) * cell_h - r * gap   # from top
        
            if len(stickers) <= total_cells:
                # repeat to fill page
                img = stickers[cell_i % len(stickers)]
            else:
                # sequential placement across pages, blank remainder on last page
                if idx >= len(stickers):
                    break
                img = stickers[idx]
                idx += 1
                
            iw, ih = img.size
            if iw <= 0 or ih <= 0:
                continue
        
            # Fit image inside cell maintaining aspect ratio
            scale = min(cell_w / iw, cell_h / ih)
            draw_w = iw * scale
            draw_h = ih * scale
        
            x = x0 + (cell_w - draw_w) / 2
            y = y0 + (cell_h - draw_h) / 2
        
            c.drawImage(_img_to_reader(img), x, y, width=draw_w, height=draw_h, mask="auto")
    
        c.showPage()
    
    c.save()