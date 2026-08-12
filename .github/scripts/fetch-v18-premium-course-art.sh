#!/usr/bin/env bash
set -euo pipefail
RAW=.github/tmp/v18
RES=app/src/main/res/drawable-nodpi
mkdir -p "$RAW" "$RES"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/143.0.0.0 Safari/537.36'
GORA_PAGE='https://booking.gora.golf.rakuten.co.jp/guide/course_info/drone/disp/c_id/10068'
GORA_HTML="$RAW/sahoro-gora.html"
GORA_COOKIE="$RAW/gora-cookies.txt"
CAND="$RAW/sahoro-candidates.txt"

fetch_img(){
  local url="$1" out="$2" minw="${3:-180}" minh="${4:-180}" tmp="${2}.tmp"
  rm -f "$tmp" "$out"
  if curl -L --fail --silent --show-error --connect-timeout 8 --max-time 25 --retry 2 -A "$UA" "$url" -o "$tmp"; then
    if python3 - "$tmp" "$minw" "$minh" <<'PY'
from PIL import Image
import sys
p=sys.argv[1]; mw=int(sys.argv[2]); mh=int(sys.argv[3])
try:
    im=Image.open(p); im.verify(); ok=im.width>=mw and im.height>=mh
except Exception: ok=False
raise SystemExit(0 if ok else 1)
PY
    then mv "$tmp" "$out"; echo "ART OK  $(basename "$out")"; return 0; fi
  fi
  rm -f "$tmp"; echo "ART FALLBACK  $(basename "$out")"; return 0
}

# Establish Rakuten session and persist exact Sahoro source URLs for auditing.
: > "$CAND"
if curl -L --fail --silent --show-error --connect-timeout 8 --max-time 30 --retry 2 \
  -A "$UA" -c "$GORA_COOKIE" -b "$GORA_COOKIE" -e 'https://booking.gora.golf.rakuten.co.jp/' \
  "$GORA_PAGE" -o "$GORA_HTML"; then
  python3 - "$GORA_HTML" <<'PY' | tee "$CAND"
from html.parser import HTMLParser
from urllib.parse import urljoin
import re,sys,html
base='https://booking.gora.golf.rakuten.co.jp/'; raw=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
class P(HTMLParser):
    def __init__(self): super().__init__(); self.urls=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        for k in ('src','data-src','data-original','href','poster','srcset'):
            v=d.get(k)
            if v:
                for part in v.split(','):
                    u=part.strip().split(' ')[0]
                    if u:self.urls.append(urljoin(base,u))
p=P();p.feed(raw)
for m in re.finditer(r'https?://[^\"\'<>\\ ]+|/[A-Za-z0-9_./?=&%:+~-]+\.(?:jpg|jpeg|png|webp)(?:\?[^\"\'<>\\ ]*)?',raw,re.I): p.urls.append(urljoin(base,html.unescape(m.group(0))))
seen=[]
for u in p.urls:
    lu=u.lower()
    if u not in seen and any(k in lu for k in ('10068','hole','layout','course','drone','gora')) and any(e in lu for e in ('.jpg','.jpeg','.png','.webp')):seen.append(u)
for i,u in enumerate(seen[:300],1):print(f'GORA_IMG_CAND {i:03d} {u}')
print('GORA_HTML_BYTES',len(raw),'GORA_IMG_COUNT',len(seen))
PY
else
  echo 'GORA_HTML_FETCH_FAILED' | tee "$CAND"
fi

fetch_gora_img(){
  local url="$1" out="$2" tmp="${2}.tmp"
  rm -f "$tmp" "$out"
  if curl -L --fail --silent --show-error --connect-timeout 8 --max-time 20 --retry 1 \
      -A "$UA" -b "$GORA_COOKIE" -c "$GORA_COOKIE" -e "$GORA_PAGE" \
      -H 'Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8' \
      -H 'Sec-Fetch-Site: same-site' -H 'Sec-Fetch-Mode: no-cors' -H 'Sec-Fetch-Dest: image' \
      "$url" -o "$tmp"; then
    if python3 - "$tmp" <<'PY'
from PIL import Image
import sys
try:
    im=Image.open(sys.argv[1]); im.verify(); ok=im.width>=180 and im.height>=180
except Exception: ok=False
raise SystemExit(0 if ok else 1)
PY
    then mv "$tmp" "$out"; echo "GORA ART OK $(basename "$out")"; return 0; fi
  fi
  rm -f "$tmp"; echo "GORA CURL BLOCKED $(basename "$out")"; return 0
}

# Scenic layers.
fetch_img 'https://www.princehotels.co.jp/golf/kamishihoro/images/kamishihoro_main_pc_2000x910_01.jpg' "$RAW/raw_kamishihoro.jpg" 480 300
fetch_img 'https://www.princehotels.co.jp/image/2024_4_top200_golf_1.jpg' "$RAW/raw_furano.jpg" 480 300
fetch_img 'https://golf-pass.brightspotcdn.com/dims4/default/f86d5af/2147483647/strip/true/crop/1440x929%2B0%2B15/resize/930x600%21/format/webp/quality/90/?url=https%3A%2F%2Fgolf-pass-brightspot.s3.amazonaws.com%2Ffc%2F1b%2Ffd7f35b176dd12aa987c27f2efd2%2F119818.jpg' "$RAW/raw_sahoro.jpg" 480 300
fetch_img 'https://image.fnnews.com/resource/media/image/2025/07/03/202507031109109114_l.jpg' "$RAW/raw_naepo.jpg" 480 300
fetch_img 'https://royallinks.co.kr/mobile/images/main/event02.jpg' "$RAW/raw_royal.jpg" 480 300

# Prince + Royal full-hole maps and first-pass Rakuten downloads.
for h in $(seq -w 1 18); do
  n=$((10#$h))
  fetch_img "https://www.princehotels.co.jp/golf/kamishihoro/course/images_static/pct-course-c${h}.jpg" "$RES/yardage_kamishihoro_c${h}.jpg" 180 180
  fetch_img "https://www.princehotels.co.jp/golf/kamishihoro/course/images_static/pct-course-m${h}.jpg" "$RES/yardage_kamishihoro_m${h}.jpg" 180 180
  fetch_img "https://www.princehotels.co.jp/golf/furano/course/images_static/pct-course-palmer${h}.jpg" "$RES/yardage_furano_palmer${h}.jpg" 180 180
  fetch_img "https://www.princehotels.co.jp/golf/furano/course/images_static/pct-course-king${h}.jpg" "$RES/yardage_furano_king${h}.jpg" 180 180
  fetch_img "https://www.royallinks.co.kr/images/course/a/${h}.jpg" "$RES/yardage_royallinks_queens${h}.jpg" 180 180
  fetch_img "https://www.royallinks.co.kr/images/course/b/${h}.jpg" "$RES/yardage_royallinks_kings${h}.jpg" 180 180
  if [ "$n" -le 9 ]; then
    fetch_gora_img "https://image.gora.golf.rakuten.co.jp/img/golf/10068/new_hole_info/166_${n}.png" "$RES/yardage_sahoro_${h}.png"
  else
    k=$((n-9)); fetch_gora_img "https://image.gora.golf.rakuten.co.jp/img/golf/10068/new_hole_info/167_${k}.png" "$RES/yardage_sahoro_${h}.png"
  fi
done

# Rakuten blocks raw image fetches from some CI IPs. If needed, keep the live
# GORA page open and inject each known hole URL as an IMG request initiated by
# that page. Screenshot the loaded element, preserving the entire tee->green map.
SAHORO=$(find "$RES" -maxdepth 1 -type f -name 'yardage_sahoro_*.png' | wc -l)
if [ "$SAHORO" -ne 18 ]; then
  echo "GORA direct fetch yielded $SAHORO/18; starting in-page browser injection"
  rm -f "$RES"/yardage_sahoro_*.png
  python3 - "$GORA_PAGE" "$RES" <<'PY'
import sys,time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image,ImageStat

page=sys.argv[1]; root=Path(sys.argv[2])
opt=Options()
for a in ('--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--window-size=1600,1200'):
    opt.add_argument(a)
opt.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/143.0.0.0 Safari/537.36')
d=webdriver.Chrome(options=opt)
d.set_script_timeout(18)
try:
    d.get(page); time.sleep(2.5)
    ok_count=0
    for hole in range(1,19):
        grp='166' if hole<=9 else '167'; num=hole if hole<=9 else hole-9
        src=f'https://image.gora.golf.rakuten.co.jp/img/golf/10068/new_hole_info/{grp}_{num}.png'
        result=d.execute_async_script(r'''
            const url=arguments[0], done=arguments[arguments.length-1];
            const old=document.getElementById('oaiHoleImage'); if(old) old.remove();
            const img=document.createElement('img'); img.id='oaiHoleImage';
            img.style.cssText='position:absolute;left:0;top:0;z-index:2147483647;background:#fff;max-width:none!important;max-height:none!important;object-fit:contain;';
            img.onload=()=>{img.style.width=img.naturalWidth+'px';img.style.height=img.naturalHeight+'px';done([true,img.naturalWidth,img.naturalHeight]);};
            img.onerror=()=>done([false,0,0]);
            document.body.appendChild(img); img.src=url;
        ''',src)
        loaded=bool(result and result[0]); nw=int(result[1]) if loaded else 0; nh=int(result[2]) if loaded else 0
        print('INJECT LOAD',hole,loaded,nw,nh,src)
        if not loaded or nw<180 or nh<180: continue
        el=d.find_element(By.ID,'oaiHoleImage')
        d.execute_script("window.scrollTo(0,0);arguments[0].style.left='0px';arguments[0].style.top='0px';",el)
        time.sleep(.12)
        out=root/f'yardage_sahoro_{hole:02d}.png'
        if not el.screenshot(str(out)): continue
        try:
            with Image.open(out) as im:
                if im.width<180 or im.height<180:
                    out.unlink(missing_ok=True); continue
                st=ImageStat.Stat(im.convert('RGB').resize((32,32)))
                if sum(st.stddev)<8:
                    print('INJECT LOW VARIANCE',hole,st.stddev); out.unlink(missing_ok=True); continue
                print('SELENIUM GORA OK',out.name,im.size,'std',round(sum(st.stddev),2))
                ok_count+=1
        except Exception as e:
            print('INJECT VERIFY FAIL',hole,e); out.unlink(missing_ok=True)
    print('SELENIUM_GORA_COUNT',ok_count)
finally:
    d.quit()
PY
fi

PRINCE=$(find "$RES" -maxdepth 1 -type f \( -name 'yardage_kamishihoro_*.jpg' -o -name 'yardage_furano_*.jpg' \) | wc -l)
SAHORO=$(find "$RES" -maxdepth 1 -type f -name 'yardage_sahoro_*.png' | wc -l)
ROYAL=$(find "$RES" -maxdepth 1 -type f -name 'yardage_royallinks_*.jpg' | wc -l)
echo "Prince full-hole assets present: $PRINCE"
echo "Sahoro GORA full-hole assets present: $SAHORO"
echo "Royal Links full-hole assets present: $ROYAL"
if [ "$PRINCE" -ne 72 ] || [ "$SAHORO" -ne 18 ] || [ "$ROYAL" -ne 36 ]; then
  echo 'FULL-HOLE ASSET GATE FAILED' >&2
  exit 1
fi
