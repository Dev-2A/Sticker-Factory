from __future__ import annotations

from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw

from sticker_factory.core import StickerOptions, is_fully_opaque, make_sticker, preset_to_px
from sticker_factory.logging_utils import setup_logging
from sticker_factory.paths import make_run_paths
from sticker_factory.pdfgen import GRID_PRESETS, SheetOptions, make_a4_sheet_pdf
from sticker_factory.samples import ensure_samples

st.set_page_config(page_title="Sticker Factory", layout="wide")


def _load_image_from_upload(upload) -> Image.Image:
    # Streamlit UploadedFile -> PIL Image
    data = upload.read()
    bio = BytesIO(data)
    img = Image.open(bio)
    img.load()
    return img


def _save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")


def _png_bytes(img: Image.Image) -> bytes:
    bio = BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()


def _checkerboard_bg(w: int, h: int, tile: int= 24) -> Image.Image:
    img = Image.new("RGB", (w, h), (230, 230, 230))
    d = ImageDraw.Draw(img)
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            if ((x // tile) + (y // tile)) % 2 == 0:
                d.rectangle([x, y, x+ tile - 1, y + tile - 1], fill=(200, 200, 200))
    return img


def _preview_on_checker(sticker_rgba: Image.Image, pad: int = 40) -> Image.Image:
    w, h = sticker_rgba.size
    bg = _checkerboard_bg(w + pad * 2, h + pad * 2)
    bg_rgba = bg.convert("RGBA")
    bg_rgba.alpha_composite(sticker_rgba, (pad, pad))
    return bg_rgba.convert("RGB")

def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    samples_dir = ensure_samples(project_root)
    
    st.title("Sticker Factory 🏭 (Sticker Sheet Generator)")
    st.caption("이미지를 넣으면 스티커가 나온다. 공장장님(당신)은 오늘도 생산량을 뽑는다.")
    
    # Sidebar: options
    with st.sidebar:
        st.header("Sticker Options")
        
        preset = st.selectbox("Size preset", ["S", "M", "L", "CUSTOM"], index=1)
        target_px = preset_to_px(preset)
        
        custom_px = None
        if preset == "CUSTOM":
            custom_px = st.number_input("Custom longest side (px)", min_value=64, max_value=4096, value=768, step=32)
        
        border_px = st.slider("White border thickness (px)", min_value=0, max_value=80, value=24, step=2)
        
        st.divider()
        st.subheader("Background")
        simple_bg_remove = st.checkbox("Simple background remove (solid bg)", value=False)
        auto_bg_remove_when_opaque = st.checkbox(
            "Auto-enable simple bg remove when no transparency (recommended)",
            value=True,
        )
        bg_threshold = st.slider(
            "BG threshold",
            min_value=0,
            max_value=120,
            value=30,
            step=1,
            disabled=not (simple_bg_remove or auto_bg_remove_when_opaque),
        )
        
        st.divider()
        st.header("Sheet Options (A4 PDF)")
        grid_preset = st.selectbox("Grid preset", list(GRID_PRESETS.keys()), index=1)
        cols, rows = GRID_PRESETS[grid_preset]
        margin_mm = st.number_input("Margin (mm)", min_value=0.0, max_value=30.0, value=10.0, step=1.0)
        gap_mm = st.number_input("Gap (mm)", min_value=0.0, max_value=20.0, value=4.0, step=1.0)
    
    # Inputs
    c1, c2 = st.columns([2, 1], gap="large")
    
    with c1:
        st.subheader("1) Upload images")
        uploads = st.file_uploader(
            "PNG/JPG (multiple allowed)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )
        
        st.markdown("**Or use samples:**")
        sample_paths = sorted(samples_dir.glob("*.*"))
        sample_choice = st.selectbox(
            "Sample image",
            ["(none)"] + [p.name for p in sample_paths],
            index=0,
        )
        
        images: list[tuple[str, Image.Image]] = []
        
        # Load uploads
        if uploads:
            for up in uploads:
                try:
                    img = _load_image_from_upload(up)
                    images.append((up.name, img))
                except Exception as e:
                    st.error(f"Failed to read upload {up.name}: {e}")
        
        # Load sample
        if sample_choice != "(none)":
            p = samples_dir / sample_choice
            try:
                img = Image.open(p)
                img.load()
                images.append((p.name, img))
            except Exception as e:
                st.error(f"Failed to load sample {p.name}: {e}")
        
        if images:
            opaque_inputs = [name for (name, im) in images if is_fully_opaque(im)]
            
            if opaque_inputs and (not simple_bg_remove) and (not auto_bg_remove_when_opaque):
                st.warning(
                    "Some inputs have no transparency. White border may NOT appear unless you enable "
                    "'Simple background remove' (or turn on auto-enable option).\n\n"
                    f"Opaque: {', '.join(opaque_inputs[:8])}"
                    + (" ..." if len(opaque_inputs) > 8 else "")
                )
            elif opaque_inputs and auto_bg_remove_when_opaque and (not simple_bg_remove):
                st.info(
                    "Some inputs are fully opaque. Auto simple background removal will be applied "
                    "to create transparency for the white border."
                )
            
            st.write(f"Loaded: **{len(images)}** image(s)")
            thumbs = st.columns(min(4, len(images)))
            for i, (name, img) in enumerate(images[:4]):
                with thumbs[i]:
                    st.image(img, caption=name, use_column_width=True)
        else:
            st.info("Upload images or pick a sample to begin.")
    
    with c2:
        st.subheader("2) Generate")
        run_button = st.button("Generate stickers + A4 PDF", type="primary", use_container_width=True)
        
        st.markdown("**Output:** `out/<timestamp>/...`")
        st.markdown("**Logging:** `run.log` inside that folder")
    
    if not run_button:
        return
    
    if not images:
        st.warning("No images to process.")
        return
    
    # Prepare run dirs + logging
    rp = make_run_paths(project_root)
    logger = setup_logging(rp.log_path)
    logger.info("Run started: %s", rp.run_id)
    
    opts = StickerOptions(
        preset=preset,
        target_px=int(target_px),
        custom_px=int(custom_px) if custom_px is not None else None,
        border_px=int(border_px),
        simple_bg_remove=bool(simple_bg_remove),
        bg_threshold=int(bg_threshold),
    )
    
    sheet_opts = SheetOptions(
        cols=int(cols),
        rows=int(rows),
        margin_mm=float(margin_mm),
        gap_mm=float(gap_mm),
    )
    
    st.success(f"Run: {rp.run_id}")
    st.code(str(rp.out_dir), language="text")
    
    stickers: list[Image.Image] = []
    results_rows = []
    
    # Process each image with failure isolation
    for idx, (name, img) in enumerate(images, start=1):
        try:
            logger.info("Processing [%d/%d] %s", idx, len(images), name)
            
            effective_simple = bool(simple_bg_remove)
            if auto_bg_remove_when_opaque and is_fully_opaque(img):
                effective_simple = True
            per_img_opts = StickerOptions(
                preset=opts.preset,
                target_px=opts.target_px,
                custom_px=opts.custom_px,
                border_px=opts.border_px,
                simple_bg_remove=effective_simple,
                bg_threshold=opts.bg_threshold,
            )
            
            sticker = make_sticker(img, per_img_opts)
            
            stickers.append(sticker)
            
            base = Path(name).stem
            out_png = rp.stickers_dir / f"{base}__sticker.png"
            _save_png(sticker, out_png)
            
            results_rows.append((name, "OK", str(out_png)))
        except Exception as e:
            logger.exception("Failed processing %s: %s", name, e)
            results_rows.append((name, "FAIL", str(e)))
    
    # PDF (even if some failed)
    pdf_path = rp.sheets_dir / f"sticker_sheet_{rp.run_id}.pdf"
    try:
        make_a4_sheet_pdf(stickers=stickers, out_pdf_path=str(pdf_path), opts=sheet_opts)
        logger.info("PDF created: %s", str(pdf_path))
    except Exception as e:
        logger.exception("PDF generation failed: %s", e)
        st.error(f"PDF generation failed: {e}")
        pdf_path = None
    
    # UI results
    st.divider()
    st.subheader("3) Results")
    
    colA, colB = st.columns([1, 1], gap="large")
    
    with colA:
        st.markdown("### Files")
        st.write("Stickers saved:", str(rp.stickers_dir))
        if pdf_path:
            st.write("PDF saved:", str(pdf_path))
        st.write("Log:", str(rp.log_path))
        
        # Downloads (in-browser)
        st.markdown("### Download")
        if stickers:
            st.download_button(
                label="Download first sticker PNG",
                data=_png_bytes(stickers[0]),
                file_name="sticker.png",
                mime="image/png",
                use_container_width=True,
            )
        if pdf_path and pdf_path.exists():
            st.download_button(
                label="Download A4 sheet PDF",
                data=pdf_path.read_bytes(),
                file_name=pdf_path.name,
                mime="application/pdf",
                use_container_width=True,
            )
    
    with colB:
        previews = [_preview_on_checker(s) for s in stickers[:6]]
        st.markdown("### Preview")
        if stickers:
            st.image(previews, caption=[f"Sticker {i+1}" for i in range(len(previews))], width=160)
        else:
            st.info("No sticker generated (all failed).")
    
    st.markdown("### Per-image status")
    st.table([{"input": a, "status": b, "output_or_error": c} for a, b, c in results_rows])
    
    logger.info("Run finished. OK=%d FAIL=%d", sum(r[1] == "OK" for r in results_rows), sum(r[1] == "FAIL" for r in results_rows))


if __name__ == "__main__":
    main()