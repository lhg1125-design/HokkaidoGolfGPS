#!/usr/bin/env bash
set -u
RAW=.github/tmp/v18
mkdir -p "$RAW"
UA='Mozilla/5.0 (Linux; Android 15; HokkaidoGolfGPS/1.8) AppleWebKit/537.36'

fetch_img(){
  local url="$1"
  local out="$2"
  local tmp="${out}.tmp"
  rm -f "$tmp" "$out"
  if curl -L --fail --silent --show-error --connect-timeout 8 --max-time 25 --retry 1 -A "$UA" "$url" -o "$tmp"; then
    if python3 - "$tmp" <<'PY'
from PIL import Image
import sys
p=sys.argv[1]
try:
    im=Image.open(p); im.verify()
    ok=im.width>=320 and im.height>=180
except Exception:
    ok=False
raise SystemExit(0 if ok else 1)
PY
    then
      mv "$tmp" "$out"
      echo "ART OK  $(basename "$out")"
      return 0
    fi
  fi
  rm -f "$tmp"
  echo "ART FALLBACK  $(basename "$out")"
  return 0
}

# Japan: official Prince hero photography for Kamishihoro/Furano; Sahoro uses a
# high-resolution course reference from GDO. These are visual layers only —
# hole PAR/yardage remains the structured app data.
fetch_img 'https://www.princehotels.co.jp/golf/kamishihoro/images/kamishihoro_main_pc_2000x910_01.jpg' "$RAW/raw_kamishihoro.jpg"
fetch_img 'https://www.princehotels.co.jp/image/2024_4_top200_golf_1.jpg' "$RAW/raw_furano.jpg"
fetch_img 'https://i.gimg.jp/resource/reserve/courseimage/01103_13.jpg' "$RAW/raw_sahoro.jpg"

# Korea test pack: Naepo aerial overview reference + Royal Links official course image.
fetch_img 'https://image.fnnews.com/resource/media/image/2025/07/03/202507031109109114_l.jpg' "$RAW/raw_naepo.jpg"
fetch_img 'https://www.royallinks.co.kr/images/course/courseImg.jpg' "$RAW/raw_royal.jpg"

ls -lh "$RAW" || true
