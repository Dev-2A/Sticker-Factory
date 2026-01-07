from __future__ import annotations

from pathlib import Path

from PIL import Image

from sticker_factory.pdfgen import SheetOptions, make_a4_sheet_pdf


def _count_pdf_pages_rough(pdf_bytes: bytes) -> int:
    """
    Rough page count without extra deps.
    ReportLab usually contains multiple '/Type /Page' occurrences:
    - one per page
    - one for the '/Pages' node
    We'll subtract 1 as an approximation.
    """
    n = pdf_bytes.count(b"/Type /Page")
    return max(1, n - 1)


def test_make_a4_sheet_pdf_creates_file(tmp_path: Path):
    stickers = [Image.new("RGBA", (300, 300), (255, 0, 0, 128))]
    out_pdf = tmp_path / "sheet.pdf"
    opts = SheetOptions(cols=3, rows=5, margin_mm=10.0, gap_mm=4.0, show_cut_guides=False)

    make_a4_sheet_pdf(stickers=stickers, out_pdf_path=str(out_pdf), opts=opts)
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0


def test_make_a4_sheet_pdf_with_cut_guides(tmp_path: Path):
    stickers = [Image.new("RGBA", (300, 300), (0, 255, 0, 128))]
    out_pdf = tmp_path / "sheet_guides.pdf"
    opts = SheetOptions(cols=4, rows=6, margin_mm=10.0, gap_mm=4.0, show_cut_guides=True)

    make_a4_sheet_pdf(stickers=stickers, out_pdf_path=str(out_pdf), opts=opts)
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0


def test_make_a4_sheet_pdf_pagination_multiple_pages(tmp_path: Path):
    # 3x5 => 15 cells per page
    # Create 40 stickers => ceil(40/15)=3 pages expected
    stickers = [Image.new("RGBA", (200, 200), (i % 256, 0, 0, 255)) for i in range(40)]
    out_pdf = tmp_path / "sheet_multi.pdf"
    opts = SheetOptions(cols=3, rows=5, margin_mm=10.0, gap_mm=4.0, show_cut_guides=False)

    make_a4_sheet_pdf(stickers=stickers, out_pdf_path=str(out_pdf), opts=opts)
    data = out_pdf.read_bytes()
    pages = _count_pdf_pages_rough(data)

    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0
    assert pages >= 3


def test_make_a4_sheet_pdf_fill_mode_blank(tmp_path: Path):
    # When stickers <= cells/page, fill_mode="blank" should leave remaining cells empty (no error).
    stickers = [Image.new("RGBA", (200, 200), (0, 0, 255, 255)) for _ in range(2)]
    out_pdf = tmp_path / "sheet_blank.pdf"
    opts = SheetOptions(cols=3, rows=5, margin_mm=10.0, gap_mm=4.0, fill_mode="blank")

    make_a4_sheet_pdf(stickers=stickers, out_pdf_path=str(out_pdf), opts=opts)
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0


def test_make_a4_sheet_pdf_with_labels(tmp_path: Path):
    stickers = [Image.new("RGBA", (200, 200), (10, 10, 10, 255)) for _ in range(3)]
    names = ["cat.png", "dog.png", "fox.png"]
    out_pdf = tmp_path / "sheet_labels.pdf"
    opts = SheetOptions(
        cols=3,
        rows=5,
        margin_mm=10.0,
        gap_mm=4.0,
        show_labels=True,
        label_mode="filename",
        label_font_size=6.0,
    )

    make_a4_sheet_pdf(stickers=stickers, sticker_names=names, out_pdf_path=str(out_pdf), opts=opts)
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0
