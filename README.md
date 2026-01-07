# Sticker Factory (Sticker Sheet Generator)

이미지 → **스티커 PNG(흰 테두리)** + **A4 스티커 시트 PDF**를 자동으로 생성하는 Windows-friendly MVP.

## Features (MVP)
- PNG/JPG 업로드 (여러 장 가능)
- 스티커 단품 PNG 생성
  - 투명 배경 유지(가능 시)
  - (옵션) **간단 배경 제거**: 단색 배경(코너 색) 기반
  - 흰 테두리(두께 조절)
  - 크기 프리셋(S/M/L) 또는 px 지정
- A4 PDF 스티커 시트 생성
  - 그리드 프리셋 (3x5, 4x6, 5x7)
  - 여백/간격(mm) 조절
 - 산출물: `out/YYYYMMDD_HHMMSS/` 아래 저장
- 로그: 콘솔 + `run.log`
- 실패 격리: 한 장 실패해도 나머지는 계속

## Requirements
- Windows 10/11
- Python 3.10+ (권장 3.11도 OK)

## Run (Windows CMD)
```bat
run.cmd
```
접속: http://127.0.0.1:8501

## Output
- `out/<run_id>/stickers/*.png`
- `out/<run_id>/sheets/*.pdf`
- `out/<run_id>/run.log`

## Notes
- "간단 배경 제거"는 단색 배경(예: 흰 배경 상품컷)에서 잘 동작합니다.
- 아주 정교한 배경 제거가 필요하면 추후 v0.2에서 `rembg`(onnx) 같은 옵션을 추가하는 걸 추천.