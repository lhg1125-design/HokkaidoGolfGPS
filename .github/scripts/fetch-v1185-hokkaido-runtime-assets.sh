#!/usr/bin/env bash
set -euo pipefail
RES=app/src/main/res/drawable-nodpi
TMP=.github/tmp/v1185-hokkaido
mkdir -p "$RES" "$TMP"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/143.0.0.0 Safari/537.36'

fetch_img(){
  local url="$1" out="$2" minw="${3:-120}" minh="${4:-180}" tmp="${2}.tmp"
  rm -f "$tmp" "$out"
  curl -L --fail --silent --show-error --connect-timeout 10 --max-time 35 --retry 4 --retry-all-errors \
    -A "$UA" -H 'Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8' \
    "$url" -o "$tmp"
  python3 - "$tmp" "$minw" "$minh" <<'PY'
from PIL import Image
import sys
p=sys.argv[1]; mw=int(sys.argv[2]); mh=int(sys.argv[3])
with Image.open(p) as im:
    im.verify()
with Image.open(p) as im:
    assert im.width >= mw and im.height >= mh, (p, im.size)
PY
  mv "$tmp" "$out"
  echo "ASSET OK $(basename "$out")"
}

fetch_gora(){
  local url="$1" out="$2" tmp="${2}.tmp"
  rm -f "$tmp" "$out"
  curl -L --fail --silent --show-error --connect-timeout 10 --max-time 35 --retry 5 --retry-all-errors \
    -A "$UA" \
    -e 'https://booking.gora.golf.rakuten.co.jp/guide/course_info/drone/disp/c_id/10068' \
    -H 'Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8' \
    -H 'Accept-Language: ja,en-US;q=0.8,en;q=0.6' \
    "$url" -o "$tmp"
  python3 - "$tmp" <<'PY'
from PIL import Image, ImageStat
import sys
p=sys.argv[1]
with Image.open(p) as im:
    im.verify()
with Image.open(p) as im:
    assert im.width >= 60 and im.height >= 300, (p, im.size)
    stat=ImageStat.Stat(im.convert('RGB').resize((32,32)))
    assert sum(stat.stddev) > 8, (p, stat.stddev)
PY
  mv "$tmp" "$out"
  echo "SAHORO OK $(basename "$out")"
}

# Remove stale runtime yardage assets so this build is Hokkaido-only.
rm -f "$RES"/yardage_kamishihoro_* "$RES"/yardage_furano_* "$RES"/yardage_sahoro_* "$RES"/yardage_royallinks_* "$RES"/yardage_naepo_*

for h in $(seq -w 1 18); do
  fetch_img "https://www.princehotels.co.jp/golf/kamishihoro/course/images_static/pct-course-c${h}.jpg" "$RES/yardage_kamishihoro_c${h}.jpg" 180 180
  fetch_img "https://www.princehotels.co.jp/golf/kamishihoro/course/images_static/pct-course-m${h}.jpg" "$RES/yardage_kamishihoro_m${h}.jpg" 180 180
  fetch_img "https://www.princehotels.co.jp/golf/furano/course/images_static/pct-course-palmer${h}.jpg" "$RES/yardage_furano_palmer${h}.jpg" 180 180
  fetch_img "https://www.princehotels.co.jp/golf/furano/course/images_static/pct-course-king${h}.jpg" "$RES/yardage_furano_king${h}.jpg" 180 180
  n=$((10#$h))
  if [ "$n" -le 9 ]; then
    fetch_gora "https://image.gora.golf.rakuten.co.jp/img/golf/10068/new_hole_info/166_${n}.png" "$RES/yardage_sahoro_${h}.png"
  else
    k=$((n-9))
    fetch_gora "https://image.gora.golf.rakuten.co.jp/img/golf/10068/new_hole_info/167_${k}.png" "$RES/yardage_sahoro_${h}.png"
  fi
done

PRINCE=$(find "$RES" -maxdepth 1 -type f \( -name 'yardage_kamishihoro_*.jpg' -o -name 'yardage_furano_*.jpg' \) | wc -l)
SAHORO=$(find "$RES" -maxdepth 1 -type f -name 'yardage_sahoro_*.png' | wc -l)
TOTAL=$((PRINCE+SAHORO))
echo "Hokkaido runtime yardage assets: Prince=$PRINCE Sahoro=$SAHORO Total=$TOTAL"
test "$PRINCE" -eq 72
test "$SAHORO" -eq 18
test "$TOTAL" -eq 90
