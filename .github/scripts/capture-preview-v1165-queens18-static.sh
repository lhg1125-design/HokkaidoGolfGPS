#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.16.5-static-course-qc-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1165-queens18"
mkdir -p "$OUT"; rm -f "$OUT"/*.png
adb shell wm size 941x1672
adb shell wm density 420
sleep 3

adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put secure immersive_mode_confirmations confirmed || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true

start_preview(){
  local hole="$1"
  adb shell am force-stop "$PKG" || true
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse 4 --ei previewVariant 0 --ei previewHole "$hole" --ei previewScreen 1 >/dev/null
  sleep 1.2
}

for h in $(seq 1 18); do
  hh=$(printf '%02d' "$h")
  start_preview "$h"
  adb exec-out screencap -p > "$OUT/queens-h${hh}.png"
  test -s "$OUT/queens-h${hh}.png"
done

python3 - <<'PY'
from pathlib import Path
from PIL import Image
import hashlib
out=Path('preview-v1165-queens18')
fs=sorted(out.glob('queens-h*.png'))
assert len(fs)==18,fs
hashes=[]
for i,f in enumerate(fs,1):
    im=Image.open(f).convert('RGB')
    assert im.size==(941,1672),(f,im.size)
    # Bottom navigation begins near y=1458. The course viewport ends at 1428,
    # so no approved hole artwork may be clipped by navigation.
    hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
assert len(set(hashes))>=16,('screenshots unexpectedly duplicated',len(set(hashes)))
print('QUEENS 18 SCREENSHOT SET READY',len(fs),'unique',len(set(hashes)))
PY

adb shell wm size reset || true
adb shell wm density reset || true
ls -lh "$OUT"/*.png
