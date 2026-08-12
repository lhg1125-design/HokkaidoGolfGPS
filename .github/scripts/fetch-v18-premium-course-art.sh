#!/usr/bin/env bash
set -u
RAW=.github/tmp/v18
RES=app/src/main/res/drawable-nodpi
mkdir -p "$RAW" "$RES"
UA='Mozilla/5.0 (Linux; Android 15; HokkaidoGolfGPS/1.10.2) AppleWebKit/537.36'

fetch_img(){
  local url="$1"
  local out="$2"
  local minw="${3:-180}"
  local minh="${4:-180}"
  local tmp="${out}.tmp"
  rm -f "$tmp" "$out"
  if curl -L --fail --silent --show-error --connect-timeout 8 --max-time 25 --retry 2 -A "$UA" "$url" -o "$tmp"; then
    if python3 - "$tmp" "$minw" "$minh" <<'PY'
from PIL import Image
import sys
p=sys.argv[1]; mw=int(sys.argv[2]); mh=int(sys.argv[3])
try:
    im=Image.open(p); im.verify(); ok=im.width>=mw and im.height>=mh
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

# Scenic layers used by the landing/course cards.
fetch_img 'https://www.princehotels.co.jp/golf/kamishihoro/images/kamishihoro_main_pc_2000x910_01.jpg' "$RAW/raw_kamishihoro.jpg" 480 300
fetch_img 'https://www.princehotels.co.jp/image/2024_4_top200_golf_1.jpg' "$RAW/raw_furano.jpg" 480 300
fetch_img 'https://golf-pass.brightspotcdn.com/dims4/default/f86d5af/2147483647/strip/true/crop/1440x929%2B0%2B15/resize/930x600%21/format/webp/quality/90/?url=https%3A%2F%2Fgolf-pass-brightspot.s3.amazonaws.com%2Ffc%2F1b%2Ffd7f35b176dd12aa987c27f2efd2%2F119818.jpg' "$RAW/raw_sahoro.jpg" 480 300
fetch_img 'https://image.fnnews.com/resource/media/image/2025/07/03/202507031109109114_l.jpg' "$RAW/raw_naepo.jpg" 480 300
fetch_img 'https://royallinks.co.kr/mobile/images/main/event02.jpg' "$RAW/raw_royal.jpg" 480 300

# ---------------------------------------------------------------------------
# Full-hole maps. These are the Prince official per-hole course-guide images.
# They are stored as drawable-nodpi so Android never crops or density-rescales
# them before the FIT_CENTER renderer displays tee -> green in full.
# ---------------------------------------------------------------------------
for h in $(seq -w 1 18); do
  fetch_img "https://www.princehotels.co.jp/golf/kamishihoro/course/images_static/pct-course-c${h}.jpg" "$RES/yardage_kamishihoro_c${h}.jpg" 180 180
  fetch_img "https://www.princehotels.co.jp/golf/kamishihoro/course/images_static/pct-course-m${h}.jpg" "$RES/yardage_kamishihoro_m${h}.jpg" 180 180
  fetch_img "https://www.princehotels.co.jp/golf/furano/course/images_static/pct-course-palmer${h}.jpg" "$RES/yardage_furano_palmer${h}.jpg" 180 180
  fetch_img "https://www.princehotels.co.jp/golf/furano/course/images_static/pct-course-king${h}.jpg" "$RES/yardage_furano_king${h}.jpg" 180 180
done

# GDO publishes a layout image for every Sahoro hole. Its asset URLs can move,
# so discover image candidates from the live course-layout HTML. We only log
# candidates here; V1.10.2 falls back to an explicit SCHEMATIC full-hole view
# unless stable per-hole assets are discovered and verified.
GDO_HTML="$RAW/sahoro-gdo.html"
if curl -L --fail --silent --show-error --connect-timeout 8 --max-time 25 --retry 2 -A "$UA" \
  'https://reserve.golfdigest.co.jp/golf-course/course-layout/111101/' -o "$GDO_HTML"; then
  python3 - "$GDO_HTML" <<'PY'
from html.parser import HTMLParser
from urllib.parse import urljoin
import sys
class P(HTMLParser):
    def __init__(self): super().__init__(); self.src=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()!='img': return
        d=dict(attrs); s=d.get('data-src') or d.get('src') or d.get('data-original')
        if s: self.src.append(urljoin('https://reserve.golfdigest.co.jp/',s))
p=P(); p.feed(open(sys.argv[1],encoding='utf-8',errors='ignore').read())
seen=[]
for u in p.src:
    lu=u.lower()
    if u not in seen and ('111101' in u or 'layout' in lu or 'hole' in lu or 'course' in lu):
        seen.append(u)
for i,u in enumerate(seen[:120],1): print(f'GDO_IMG_CAND {i:03d} {u}')
PY
fi

printf 'Full-hole Prince assets present: '
find "$RES" -maxdepth 1 -type f \( -name 'yardage_kamishihoro_*.jpg' -o -name 'yardage_furano_*.jpg' \) | wc -l
ls -lh "$RAW" || true
