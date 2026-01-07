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

## Background removal & white border notes
- **흰 테두리는 투명도(알파, alpha) 경계**를 기준으로 생성됩니다.
  - 입력 이미지가 **완전 불투명**(대부분의 JPG, 배경이 꽉 찬 PNG)인 경우,  
    투명 경계가 없어서 **흰 테두리가 거의/전혀 보이지 않을 수 있습니다.**
- 배경이 **단색(흰 배경 상품컷 등)** 이라면 **"Simple background remove (solid bg)"** 옵션을 켜세요.
- **"Auto-enable simple bg remove when no transparency"** 옵션을 켜두면,  
  완전 불투명 이미지에 대해 자동으로 간단 배경 제거를 적용해서 **흰 테두리 생성이 가능**해집니다.
- 참고: "간단 배경 제거"는 **단색 배경에서 가장 잘 동작**하며,  
  복잡한 배경(그라데이션/배경무늬/사람/풍경 등)에서는 결과가 부정확할 수 있습니다.