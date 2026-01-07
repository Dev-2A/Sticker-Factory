from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass(frozen=True)
class RunPaths:
    run_id: str
    root: Path
    out_dir: Path
    stickers_dir: Path
    sheets_dir: Path
    log_path: Path


def make_run_paths(project_root: Path) -> RunPaths:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = project_root / "out" / run_id
    stickers_dir = out_dir / "stickers"
    sheets_dir = out_dir / "sheets"
    log_path = out_dir / "run.log"
    
    stickers_dir.mkdir(parents=True, exist_ok=True)
    sheets_dir.mkdir(parents=True, exist_ok=True)
    
    return RunPaths(
        run_id=run_id,
        root=project_root,
        out_dir=out_dir,
        stickers_dir=stickers_dir,
        sheets_dir=sheets_dir,
        log_path=log_path,
    )