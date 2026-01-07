from __future__ import annotations

import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path


@dataclass(frozen=True)
class ZipResult:
    zip_bytes: bytes
    file_count: int


def make_zip_bytes_from_dir(dir_path: Path, arc_prefix: str | None = None) -> ZipResult:
    """
    Create a zip archive (in-memory bytes) from all files under dir_path.
    Stores relative paths in the zip. Optionally prefix inside-zip paths with arc_prefeix.
    """
    dir_path = Path(dir_path)
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"dir_path must be an existing directory: {dir_path}")
    
    files = [p for p in dir_path.rglob("*") if p.is_file()]
    
    bio = BytesIO()
    with zipfile.ZipFile(bio, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            rel = p.relative_to(dir_path).as_posix()
            arcname = f"{arc_prefix.rstrip('/')}/{rel}" if arc_prefix else rel
            zf.write(p, arcname)
    
    data = bio.getvalue()
    return ZipResult(zip_bytes=data, file_count=len(files))