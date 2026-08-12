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
    ok=im.width>=480 and im.height>=300
except Exception:
    ok=False
raise SystemExit(0 if ok else 1)
PY
    then
      mv "$tmp" "$out"
      python3 - "$out" <<'PY'
from PIL import Image
import sys,os
im=Image.open(sys.argv[1])
print('ART OK ',os.path.basename(sys.argv[1]),im.size,os.path.getsize(sys.argv[1]))
PY
      return 0
    fi
  fi
  rm -f "$tmp"
  echo "ART FALLBACK  $(basename "$out")"
  return 0
}

# Japan visual layers. Hole PAR/yardage/GPS remain structured data in the app.
fetch_img 'https://www.princehotels.co.jp/golf/kamishihoro/images/kamishihoro_main_pc_2000x910_01.jpg' "$RAW/raw_kamishihoro.jpg"
fetch_img 'https://www.princehotels.co.jp/image/2024_4_top200_golf_1.jpg' "$RAW/raw_furano.jpg"
fetch_img 'https://golf-pass.brightspotcdn.com/dims4/default/f86d5af/2147483647/strip/true/crop/1440x929%2B0%2B15/resize/930x600%21/format/webp/quality/90/?url=https%3A%2F%2Fgolf-pass-brightspot.s3.amazonaws.com%2Ffc%2F1b%2Ffd7f35b176dd12aa987c27f2efd2%2F119818.jpg' "$RAW/raw_sahoro.jpg"

# Korea test pack: Naepo aerial overview reference + Royal Links official scenic image.
fetch_img 'https://image.fnnews.com/resource/media/image/2025/07/03/202507031109109114_l.jpg' "$RAW/raw_naepo.jpg"
fetch_img 'https://royallinks.co.kr/mobile/images/main/event02.jpg' "$RAW/raw_royal.jpg"

ls -lh "$RAW" || true
