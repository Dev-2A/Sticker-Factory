from __future__ import annotations

from PIL import Image, ImageDraw

from sticker_factory.core import StickerOptions, make_sticker, is_fully_opaque


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


def test_is_fully_opaque():
    rgb = Image.new("RGB", (10, 10), (255, 0, 0))
    assert is_fully_opaque(rgb) is True
    
    rgba = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
    assert is_fully_opaque(rgba) is True
    
    rgba2 = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
    rgba2.putpixel((0, 0), (255, 0, 0, 0))
    assert is_fully_opaque(rgba2) is False