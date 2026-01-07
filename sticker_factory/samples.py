from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw


def _make_sample_1(path: Path) -> None:
    # transparent background + simple shapes
    img = Image.new("RGBA", (768, 768), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # cute sticker-ish blob
    d.ellipse((80, 120, 688, 700), fill=(255, 200, 50, 255))
    d.ellipse((210, 240, 310, 340), fill=(0, 0, 0, 255))
    d.ellipse((458, 240, 558, 340), fill=(0, 0, 0, 255))
    d.arc((260, 360, 560, 620), start=200, end=340, fill=(0, 0, 0, 255), width=18)
    
    img.save(path)


def _make_sample_2(path: Path) -> None:
    # non-transparent background (for simple bg remove demo)
    img = Image.new("RGB", (900, 600), (245, 245, 245))
    d = ImageDraw.Draw(img)
    
    d.rounded_rectangle((120, 80, 780, 520), radius=60, fill=(80, 160, 255))
    d.polygon([(450, 130), (540, 290), (720, 300), (580, 410), (640, 560),
               (450, 470), (260, 560), (320, 410), (180, 300), (360, 290)],
              fill=(255, 255, 255))
    
    img.save(path)


def ensure_samples(project_root: Path) -> Path:
    samples_dir = project_root / "assets" / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    
    s1 = samples_dir / "sample_transparent.png"
    s2 = samples_dir / "sample_solid_bg.jpg"
    
    if not s1.exists():
        _make_sample_1(s1)
    if not s2.exists():
        _make_sample_2(s2)
    
    return samples_dir


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    samples_dir = ensure_samples(project_root)
    print(f"[samples] ready: {samples_dir}")


if __name__ == "__main__":
    main()