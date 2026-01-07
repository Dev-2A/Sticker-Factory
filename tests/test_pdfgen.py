from __future__ import annotations

from pathlib import Path

from PIL import Image

from sticker_factory.pdfgen import SheetOptions, make_a4_sheet_pdf


def test_make_a4_sheet_pdf_creates_file(tmp_path: Path):
    stickers = [Image.new("RGBA", (300, 300), (255, 0, 0, 128))]
    out_pdf = tmp_path / "sheet.pdf"
    opts = SheetOptions(cols=3, rows=5, margin_mm=10.0, gap_mm=4.0)
    
    make_a4_sheet_pdf(stickers=stickers, out_pdf_path=str(out_pdf), opts=opts)
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0