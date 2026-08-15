#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.15.2-furano-king123-golden-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1152-furano123"
mkdir -p "$OUT"; rm -f "$OUT"/*.png
adb logcat -c || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
adb shell wm size 1080x1920
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
shot 1 "00-furano-king-h1-golden.png"
shot 2 "01-furano-king-h2-approved-408_2.png"
shot 3 "02-furano-king-h3-approved-408_3.png"
# Basic screenshot sanity: portrait, nonempty, three distinct captures.
python3 - <<'PY'
from PIL import Image,ImageChops
from pathlib import Path
p=Path('preview-v1152-furano123'); fs=sorted(p.glob('*.png'))
assert len(fs)==3,fs
ims=[Image.open(x).convert('RGB') for x in fs]
for f,im in zip(fs,ims):
    assert im.width<im.height,(f,im.size)
    assert im.getbbox(),f
for a,b in zip(ims,ims[1:]): assert ImageChops.difference(a,b).getbbox() is not None
print([(f.name,im.size) for f,im in zip(fs,ims)])
PY
if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.15.2 Furano KING H1-H3 preview"; adb logcat -d | tail -500; exit 1
fi
adb shell wm size reset || true
adb shell wm density reset || true
printf 'V1.15.2 Furano KING H1-H3 screenshots:\n'; ls -lh "$OUT"/*.png
