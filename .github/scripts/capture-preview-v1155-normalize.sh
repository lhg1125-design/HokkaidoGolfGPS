#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.15.5-normalized-approved-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1155-furano123"
mkdir -p "$OUT"; rm -f "$OUT"/*.png
adb logcat -c || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
adb shell settings put secure immersive_mode_confirmations confirmed || true
adb shell wm size 941x1672
adb shell wm density 420
sleep .5
wake(){ adb shell input keyevent 224 >/dev/null 2>&1 || true; adb shell wm dismiss-keyguard >/dev/null 2>&1 || true; adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true; sleep .35; }
shot(){
  local hole="$1" file="$2"
  adb shell am force-stop "$PKG" || true
  wake
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse 1 --ei previewVariant 1 --ei previewHole "$hole" --ei previewScreen 1 >/dev/null
  sleep 1.5
  wake
  adb exec-out screencap -p > "$OUT/$file"
  test -s "$OUT/$file"
}
adb shell pm clear "$PKG" >/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
shot 1 "00-furano-king-h1-normalized.png"
shot 2 "01-furano-king-h2-normalized.png"
shot 3 "02-furano-king-h3-normalized.png"
python3 - <<'PY'
from PIL import Image,ImageChops
from pathlib import Path
import numpy as np
p=Path('preview-v1155-furano123'); fs=sorted(p.glob('*.png'))
assert len(fs)==3,fs
ims=[Image.open(x).convert('RGB') for x in fs]
for f,im in zip(fs,ims):
    assert im.size==(941,1672),(f,'uncropped viewport required',im.size)
    assert im.getbbox(),f
for a,b in zip(ims,ims[1:]): assert ImageChops.difference(a,b).getbbox() is not None
# App must truly fill top and bottom system areas.
for f,im in zip(fs,ims):
    top=np.asarray(im.crop((260,8,680,42)),dtype=np.float32).mean(axis=(0,1))
    bot=np.asarray(im.crop((300,1590,640,1645)),dtype=np.float32).mean(axis=(0,1))
    assert top[2]>105 and top[2]>top[0]*1.45 and top[2]>top[1]*1.15,(f,'top is not approved blue header',top.tolist())
    assert bot[1]>bot[0]*1.35 and bot[1]>bot[2]*1.05,(f,'bottom is not app nav',bot.tolist())
# Header can no longer regress to the blank V1.15.4 top: require enough bright
# title/weather pixels in the upper 95 px.
for f,im in zip(fs,ims):
    a=np.asarray(im.crop((20,15,925,92)),dtype=np.uint8)
    white=((a[:,:,0]>220)&(a[:,:,1]>220)&(a[:,:,2]>220)).mean()
    assert white>0.025,(f,'title/weather chrome missing',float(white))
# Geometry provenance is gated separately by exact 408 hashes. Here reject only
# visible undersize/blur regressions; final approval is from the captured PNGs.
def detail(im,box):
    a=np.asarray(im.convert('L').crop(box),dtype=np.float32)
    return float(np.abs(np.diff(a,axis=1)).mean()+np.abs(np.diff(a,axis=0)).mean())
boxes=[(240,350,720,1470),(250,320,700,1470),(300,320,680,1470)]
scores=[detail(im,b) for im,b in zip(ims,boxes)]
assert scores[0]>11.0,('H1 detail regression',scores)
assert scores[1]>8.5,('H2 detail regression',scores)
assert scores[2]>6.0,('H3 detail regression',scores)
print('V1.15.5 normalized visual QA',[(f.name,im.size) for f,im in zip(fs,ims)],'detail',scores)
PY
if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.15.5 Furano KING H1-H3 preview"; adb logcat -d | tail -500; exit 1
fi
adb shell wm size reset || true
adb shell wm density reset || true
printf 'V1.15.5 normalized Furano KING H1-H3 screenshots:\n'; ls -lh "$OUT"/*.png
