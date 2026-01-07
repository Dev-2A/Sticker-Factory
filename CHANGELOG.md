# Changelog  

## [Unreleased]  
- Add output ZIP export (download all generated files at once)
- Add cut guides (grid lines) option for A4 sticker sheet PDF
- Add multi-page PDF generation when stickers exceed one page
- Detect fully-opaque inputs and show a UI hint when transparency is missing
- Auto-enable simple background removal for fully-opaque inputs (optional)
- (planned) Better background removal (rembg optional)
- (planned) More sheet templates (A5, Letter)
- (plaaned) Border styles (colored stroke, drop shadow)

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