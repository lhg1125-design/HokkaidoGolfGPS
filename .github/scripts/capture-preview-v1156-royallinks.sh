#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.15.6-master-renderer-royallinks-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1156-royallinks"
mkdir -p "$OUT"; rm -f "$OUT"/*.png
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put secure immersive_mode_confirmations confirmed || true
adb shell wm size 941x1672
adb shell wm density 420
shot(){
  local variant="$1" hole="$2" name="$3"
  adb shell am force-stop "$PKG" || true
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse 4 --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen 1 >/dev/null
  sleep 1.5
  adb exec-out screencap -p > "$OUT/$name"
  test -s "$OUT/$name"
}
shot 0 1 "00-royallinks-queens-h1-master.png"
shot 1 1 "01-royallinks-kings-h1-master.png"
shot 1 10 "02-royallinks-kings-h10-master.png"
python3 - <<'PY'
from pathlib import Path
from PIL import Image, ImageChops
fs=sorted(Path('preview-v1156-royallinks').glob('*.png'))
assert len(fs)==3,fs
ims=[Image.open(f).convert('RGB') for f in fs]
for f,im in zip(fs,ims): assert im.size==(941,1672),(f,im.size)
for a,b in zip(ims,ims[1:]): assert ImageChops.difference(a,b).getbbox() is not None
print('V1.15.6 Royal Links master renderer screenshots OK',[(f.name,im.size) for f,im in zip(fs,ims)])
PY
adb shell wm size reset || true
adb shell wm density reset || true
