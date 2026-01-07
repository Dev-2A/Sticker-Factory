from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageFilter


@dataclass(frozen=True)
class StickerOptions:
    # Size
    preset: str     # "S"/"M"/"L"/"CUSTOM"
    target_px: int  # used when preset != CUSTOM (longest side)
    custom_px: int | None = None     # used when preset == CUSTOM
    
    # Border
    border_px: int = 24
    
    # Background removal (simple)
    simple_bg_remove: bool = False
    bg_threshold: int = 30  # color distance threshold, 0-255-ish


def _to_rgba(img: Image.Image) -> Image.Image:
    if img.mode != "RGBA":
        return img.convert("RGBA")
    return img


def is_fully_opaque(img: Image.Image) -> bool:
    """
    Returns True if image has no transparency (alpha is 255 everywhere.)
    JPG and most non-cutout PNGs will be fully opaque.
    """
    rgba = _to_rgba(img)
    alpha = rgba.getchannel("A")
    a_min, a_max = alpha.getextrema()
    return a_min == 255 and a_max == 255


def _resize_longest_side(img: Image.Image, longest: int) -> Image.Image:
    w, h = img.size
    if max(w, h) == longest:
        return img
    if w >= h:
        new_w = longest
        new_h = int(round(h * (longest / w)))
    else:
        new_h = longest
        new_w = int(round(w * (longest / h)))
    return img.resize((max(1, new_w), max(1, new_h)), resample=Image.LANCZOS)


def _simple_background_remove_rgba(img_rgba: Image.Image, threshold: int) -> Image.Image:
    """
    Very simple background removal:
    - Takes average of 4 corners (RGB) as background color
    - Pixels close to that color -> alpha 0
    Works best for solid backgrounds.
    """
    arr = np.array(img_rgba).astype(np.int16)   # (H,W,4)
    rgb = arr[:, :, :3]
    a = arr[:, :, 3]
    
    h, w = rgb.shape[:2]
    corners = np.array([
        rgb[0, 0], rgb[0, w - 1], rgb[h - 1, 0], rgb[h - 1, w - 1]
    ], dtype=np.int16)
    bg = corners.mean(axis=0)   # (3,)
    
    dist = np.sqrt(((rgb - bg) ** 2).sum(axis=2))   # (H,W)
    mask_bg = dist <= threshold
    
    # Only affect pixels that are currently opaque-ish
    new_a = a.copy()
    new_a[mask_bg] = 0
    
    out = arr.copy()
    out[:, :, 3] = new_a
    return Image.fromarray(out.astype(np.uint8), mode="RGBA")


def _add_white_border(img_rgba: Image.Image, border_px: int) -> Image.Image:
    """
    Sticker-style white outline based on alpha dilation.
    """
    if border_px <= 0:
        return img_rgba
    
    alpha = img_rgba.split()[-1]
    
    # Dilate alpha using MaxFilter. Size must be odd.
    k = max(3, border_px * 2 + 1)
    dilated = alpha.filter(ImageFilter.MaxFilter(size=k))
    
    # Border mask = dilated - original alpha (clamped)
    a0 = np.array(alpha).astype(np.int16)
    a1 = np.array(dilated).astype(np.int16)
    border = np.clip(a1 - a0, 0, 255).astype(np.uint8)
    
    border_img = Image.new("RGBA", img_rgba.size, (255, 255, 255, 0))
    border_img.putalpha(Image.fromarray(border, mode="L"))
    
    # Composite: border under original
    out = Image.alpha_composite(border_img, img_rgba)
    return out


def make_sticker(img: Image.Image, opts: StickerOptions) -> Image.Image:
    img_rgba = _to_rgba(img)
    
    # optional simple bg remove if no alpha or if user wants anyway
    if opts.simple_bg_remove:
        img_rgba = _simple_background_remove_rgba(img_rgba, threshold=int(opts.bg_threshold))
    
    # resize
    if opts.preset.upper() == "CUSTOM":
        longest = int(opts.custom_px or opts.target_px)
    else:
        longest = int(opts.target_px)
    
    img_rgba = _resize_longest_side(img_rgba, longest=longest)
    
    # border
    img_rgba = _add_white_border(img_rgba, border_px=int(opts.border_px))
    
    # trim transparent margins (nice for sheet packing)
    bbox = img_rgba.getbbox()
    if bbox:
        img_rgba = img_rgba.crop(bbox)
    
    return img_rgba


def preset_to_px(preset: str) -> int:
    p = preset.upper().strip()
    if p == "S":
        return 512
    if p == "M":
        return 768
    if p == "L":
        return 1024
    return 768