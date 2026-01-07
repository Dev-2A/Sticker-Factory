# Changelog

All notable changes to this project will be documented in this file.

Format: Keep a Changelog  
Versioning: Semantic Versioning (SemVer)

## [Unreleased]

### Planned
- Better background removal (optional `rembg` integration)
- More sheet templates (e.g., A5, Letter)
- More border styles (colored stroke, drop shadow)
- Additional print helpers (e.g., PDF footer: run_id/date, optional crop marks)

---

## [0.3.0]

### Added
- Sheet fill mode for single-page cases:
  - `repeat` (repeat stickers to fill all cells)
  - `blank` (leave remaining cells empty)
- Optional labels on sheet PDF:
  - `index` mode (`#1, #2, ...`)
  - `filename` mode (shortened file names)
- UI controls for fill mode and labels (mode + font size)

### Changed
- `make_a4_sheet_pdf(...)` now supports passing `sticker_names` for filename labels.

---

## [0.2.1]

### Added
- Output ZIP export:
  - One-click download of all generated outputs (stickers, PDFs, logs)
  - ZIP also saved under `out/<run_id>/`

---

## [0.2.0]

### Added
- Cut guides (grid lines) option for A4 sticker sheet PDF
- Multi-page PDF generation when stickers exceed one page
- UI option to toggle cut guides

---

## [0.1.1]

### Added
- Checkerboard preview in UI to clearly verify transparency & white border
- Detect fully-opaque inputs (e.g., JPG) and show UI hint
- Optional auto-enable for simple background removal on fully-opaque inputs

### Fixed
- CI/pytest import stability for `sticker_factory` (ensure tests can import package reliably)

---

## [0.1.0] - 2026-01-06

### Added
- Streamlit UI for uploading images and generating:
  - Sticker PNGs with adjustable white border
  - A4 sticker sheet PDF with configurable grid/margins/gap
- Simple background removal option (corner-color based)
- Output folder structure `out/<timestamp>/...`
- Console + file logging
- Failure isolation per image
- GitHub Action CI (ruff + pytest)

### Known issues
- Simple background removal struggles with complex backgrounds/gradients.
- Very large images may be slower (consider resizing input).
