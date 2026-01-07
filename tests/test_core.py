from __future__ import annotations

from PIL import Image, ImageDraw

from sticker_factory.core import StickerOptions, make_sticker


def test_make_sticker_returns_rgba_and_nonempty():
    img = Image.new("RGB", (400, 300), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.ellipse((50, 40, 340, 260), fill=(10, 200, 50))
    
    opts = StickerOptions(
        preset="S",
        target_px=512,
        border_px=20,
        simple_bg_remove=True,
        bg_threshold=35,
    )
    
    out = make_sticker(img, opts)
    assert out.mode == "RGBA"
    w, h = out.size
    assert w > 0 and h > 0