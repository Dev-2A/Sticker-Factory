from __future__ import annotations

import zipfile
from pathlib import Path

from sticker_factory.zip_utils import make_zip_bytes_from_dir


def test_make_zip_bytes_from_dir(tmp_path: Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "one.txt").write_text("1", encoding="utf-8")
    (tmp_path / "two.txt").write_text("2", encoding="utf-8")

    res = make_zip_bytes_from_dir(tmp_path, arc_prefix="out")
    assert res.file_count == 2
    assert len(res.zip_bytes) > 0

    with zipfile.ZipFile(__import__("io").BytesIO(res.zip_bytes)) as zf:
        names = set(zf.namelist())
        assert "out/a/one.txt" in names
        assert "out/two.txt" in names
