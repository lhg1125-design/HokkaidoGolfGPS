#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.16.0-master-renderer-field-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1160-royallinks"
mkdir -p "$OUT"; rm -f "$OUT"/*.png "$OUT"/*.log
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put secure immersive_mode_confirmations confirmed || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
adb shell wm size 941x1672
adb shell wm density 420
shot(){
  local variant="$1" hole="$2" file="$3"
  adb shell am force-stop "$PKG" || true
  adb logcat -c || true
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse 4 --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen 1 || true
  sleep .25
  local pid
  pid="$(adb shell pidof "$PKG" 2>/dev/null | tr -d '\r' | awk '{print $1}')"
  echo "ROYAL APP PID after launch: ${pid:-NONE} variant=$variant hole=$hole"
  sleep 2.0
  adb exec-out screencap -p > "$OUT/$file"
  adb logcat -d -v threadtime > "$OUT/${file%.png}.log" || true
  test -s "$OUT/$file"
  if ! adb shell pidof "$PKG" >/dev/null 2>&1; then
    echo "APP PROCESS EXITED: pid=${pid:-NONE} variant=$variant hole=$hole" >&2
    echo '===== APPLICATION EXIT INFO =====' >&2
    adb shell dumpsys activity exit-info "$PKG" 2>&1 | head -160 >&2 || true
    echo '===== PID/PACKAGE LOGCAT =====' >&2
    if [ -n "${pid:-}" ]; then
      grep -E "[[:space:]]${pid}[[:space:]]|${PKG}|am_crash|am_anr|am_kill|am_proc_died|lmkd|lowmemory|DEBUG.*pid" "$OUT/${file%.png}.log" | tail -260 >&2 || true
    else
      grep -E "${PKG}|am_crash|am_anr|am_kill|am_proc_died|lmkd|lowmemory" "$OUT/${file%.png}.log" | tail -260 >&2 || true
    fi
    echo '===== DROPBOX APP CRASH / NATIVE CRASH =====' >&2
    adb shell dumpsys dropbox --print data_app_crash 2>/dev/null | tail -160 >&2 || true
    adb shell dumpsys dropbox --print data_app_native_crash 2>/dev/null | tail -160 >&2 || true
    return 77
  fi
}
rc=0
shot 0 1 "00-royallinks-queens-h1-master.png" || rc=$?
if [ "$rc" -eq 0 ]; then shot 1 1 "01-royallinks-kings-h1-master.png" || rc=$?; fi
if [ "$rc" -eq 0 ]; then shot 0 18 "02-royallinks-queens-h18-master.png" || rc=$?; fi
if [ "$rc" -ne 0 ]; then
  echo "Royal Links runtime launch failed before visual QA (rc=$rc)" >&2
  exit "$rc"
fi
python3 - <<'PY'
from PIL import Image, ImageChops
from pathlib import Path
import numpy as np
p=Path("preview-v1160-royallinks")
fs=sorted(p.glob("*.png"))
assert len(fs)==3,fs
ims=[Image.open(f).convert("RGB") for f in fs]
for f,im in zip(fs,ims):
    assert im.size==(941,1672),(f,im.size)
    top=np.asarray(im.crop((250,20,700,135)),dtype=np.float32).mean(axis=(0,1))
    assert top[2]>top[0]*1.2,(f,"master blue header missing",top.tolist())
    board=np.asarray(im.crop((60,175,880,330)),dtype=np.float32).mean(axis=(0,1))
    assert board[0]>board[1]*1.25,(f,"master wood board missing",board.tolist())
    a=np.asarray(im.convert("L").crop((248,360,650,1450)),dtype=np.float32)
    assert float(a.std())>18,(f,"course source missing/flat",float(a.std()))
    nav=np.asarray(im.crop((80,1500,860,1635)),dtype=np.float32).mean(axis=(0,1))
    assert nav[1]>nav[0]*1.15,(f,"master nav missing",nav.tolist())
assert ImageChops.difference(ims[0],ims[1]).getbbox() is not None
print("V1.16.1 Royal Links master-renderer visual QA PASS", [f.name for f in fs])
PY
adb shell wm size reset || true
adb shell wm density reset || true
ls -lh "$OUT"/*.png
