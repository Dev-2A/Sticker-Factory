from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from math import ceil
from pathlib import Path

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
    fill_mode: str = "repeat"
    show_labels: bool = False
    label_mode: str = "index"   # "index" / "filename"
    label_font_size: float = 6.0


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


def _shorten_label(text: str, max_len: int = 20) -> str:
    text = " ".join((text or "").split())
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 1)] + "..."


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


def _validate_opts(opts: SheetOptions) -> None:
    if int(opts.cols) <= 0 or int(opts.rows) <= 0:
        raise ValueError("cols/rows must be > 0")
    
    if opts.fill_mode not in ("repeat", "blank"):
        raise ValueError('fill_mode must be "repeat" or "blank"')
    
    if float(opts.label_font_size) <= 0:
        raise ValueError("label_font_size must be > 0")


def make_a4_sheet_pdf(
    stickers: list[Image.Image],
    out_pdf_path: str,
    opts: SheetOptions,
    sticker_names: list[str] | None = None,
) -> None:
    """
    Create an A4 sticker sheet PDF.

    Pagination:
    - If stickers > cells/page: multi-page, sequential placement, blanks on last page remainder.
    - If stickers <= cells/page:
        - fill_mode="repeat": repeat to fill all cells (existing behavior)
        - fill_mode="blank" : place sequential then leave remaining cells empty
    Labels:
    - If show_labels=True, draw a small label inside each placed sticker cell.
      label_mode="index" uses #1, #2, ...
      label_mode="filename" uses provided sticker_names (fallback to #n).
    """
    _validate_opts(opts)
    
    page_w, page_h = A4
    margin = float(opts.margin_mm) * mm
    gap = float(opts.gap_mm) * mm
    cols, rows = int(opts.cols), int(opts.rows)
    
    cell_w = (page_w - 2 * margin - (cols - 1) * gap) / cols
    cell_h = (page_h - 2 * margin - (rows - 1) * gap) / rows
    if cell_w <= 0 or cell_h <= 0:
        raise ValueError("Invalid layout: Cell size <= 0 (check margin/gap/cols/rows).")
    
    # normalize names
    names: list[str] = []
    if sticker_names and len(sticker_names) == len(stickers):
        for n in sticker_names:
            base = Path(n).name
            names.append(base)
    else:
        names = [f"#{i+1}" for i in range(len(stickers))]
    
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
    
    multi_page = len(stickers) > total_cells
    num_pages = ceil(len(stickers) / total_cells) if multi_page else 1
    
    # label config
    if opts.show_labels:
        c.setFont("Helvetica", float(opts.label_font_size))
    
    placed_global_idx = 0 # sequential index for multi-page and blank mode
    
    for _page in range(num_pages):
        if opts.show_cut_guides:
            _draw_cut_guides(c, page_w, page_h, cols, rows, margin, gap, cell_w, cell_h)
        
        for cell_i in range(total_cells):
            r = cell_i // cols
            col = cell_i % cols
            
            x0 = margin + col * (cell_w + gap)
            y0 = page_h - margin - (r + 1) * cell_h - r * gap
            
            # Decide which sticker (if any) to place in this cell
            img: Image.Image | None = None
            sticker_idx: int | None = None
            
            if multi_page:
                if placed_global_idx >= len(stickers):
                    img = None
                else:
                    sticker_idx = placed_global_idx
                    img = stickers[sticker_idx]
                    placed_global_idx += 1
            else:
                # single page behavior depends on fill_mode
                if opts.fill_mode == "repeat":
                    sticker_idx = cell_i % len(stickers)
                    img = stickers[sticker_idx]
                else:   # blank
                    if cell_i < len(stickers):
                        sticker_idx = cell_i
                        img = stickers[sticker_idx]
                    else:
                        img = None
            
            if img is None or sticker_idx is None:
                continue
            
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
            
            # Optional label
            if opts.show_labels:
                if opts.label_mode == "index":
                    label = f"#{sticker_idx + 1}"
                else:
                    label = _shorten_label(names[sticker_idx], max_len=22)
                
                # bottom-left inside cell (small padding)
                pad = 2.0
                c.drawString(x0 + pad, y0 + pad, label)
    
        c.showPage()
    
    c.save()