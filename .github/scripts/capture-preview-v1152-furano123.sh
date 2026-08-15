#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.15.4-user-golden-visual-lock-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1154-furano123"
mkdir -p "$OUT"; rm -f "$OUT"/*.png
adb logcat -c || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
# The Android first-use immersive tutorial is not app UI. Confirm it before any
# screenshot so the QA frame contains only the APK output.
adb shell settings put secure immersive_mode_confirmations confirmed || true
# Render at the exact reviewed 941x1672 master ratio. The app itself must hide
# Android status/navigation bars and occupy the display cutout; screenshots are
# never cropped to fake a pass.
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
shot 1 "00-furano-king-h1-user-golden.png"
shot 2 "01-furano-king-h2-user-golden.png"
shot 3 "02-furano-king-h3-user-golden.png"
python3 - <<'PY'
from PIL import Image,ImageChops
from pathlib import Path
import numpy as np
p=Path('preview-v1154-furano123'); fs=sorted(p.glob('*.png'))
assert len(fs)==3,fs
ims=[Image.open(x).convert('RGB') for x in fs]
for f,im in zip(fs,ims):
    assert im.size==(941,1672),(f,'must be uncropped reviewed viewport',im.size)
    assert im.getbbox(),f
# All holes must remain distinct.
for a,b in zip(ims,ims[1:]): assert ImageChops.difference(a,b).getbbox() is not None
# Real immersive-fullscreen gate. A system/cutout black bar would make the
# top-center non-blue; a system nav bar would replace the app dark-green nav.
for f,im in zip(fs,ims):
    top=np.asarray(im.crop((260,8,680,42)),dtype=np.float32).mean(axis=(0,1))
    bot=np.asarray(im.crop((300,1590,640,1645)),dtype=np.float32).mean(axis=(0,1))
    assert top[2]>105 and top[2]>top[0]*1.45 and top[2]>top[1]*1.15,(f,'system/status/cutout bar visible',top.tolist())
    assert bot[1]>bot[0]*1.35 and bot[1]>bot[2]*1.05,(f,'system/navigation bar visible',bot.tolist())
# Reject the Android immersive tutorial sheet if it ever reappears: its large
# light panel dominates the upper half of the frame.
for f,im in zip(fs,ims):
    a=np.asarray(im.crop((80,100,860,650)),dtype=np.float32)
    near_white=((a[:,:,0]>205)&(a[:,:,1]>205)&(a[:,:,2]>205)).mean()
    assert near_white<0.55,(f,'Android immersive tutorial overlay visible',float(near_white))
# Course-art detail gate. The previous broken 127x400 / 99x400 upscales scored
# about 9.6 / 6.8 here; reviewed art is ~19 / 17.5. Keep a conservative floor
# that still rejects visibly degraded regressions.
def detail(im,box):
    a=np.asarray(im.convert('L').crop(box),dtype=np.float32)
    return float(np.abs(np.diff(a,axis=1)).mean()+np.abs(np.diff(a,axis=0)).mean())
boxes=[(240,350,720,1470),(250,320,700,1470),(300,320,680,1470)]
scores=[detail(im,b) for im,b in zip(ims,boxes)]
assert scores[0]>11.0,('H1 detail regression',scores)
assert scores[1]>11.0,('H2 low-resolution/undersize regression',scores)
assert scores[2]>10.0,('H3 low-resolution/undersize regression',scores)
print('V1.15.4 visual QA',[(f.name,im.size) for f,im in zip(fs,ims)],'detail',scores)
PY
if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.15.4 Furano KING H1-H3 preview"; adb logcat -d | tail -500; exit 1
fi
adb shell wm size reset || true
adb shell wm density reset || true
printf 'V1.15.4 Furano KING H1-H3 reviewed screenshots:\n'; ls -lh "$OUT"/*.png
