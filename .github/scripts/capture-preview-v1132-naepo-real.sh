#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.13.2-naepo-real-yardage-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1132-naepo-real"
mkdir -p "$OUT"; rm -f "$OUT"/*.png
adb logcat -c || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
clear_system_dialogs(){ adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true; sleep .3; }
shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true; clear_system_dialogs
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep .85; clear_system_dialogs
  adb exec-out screencap -p > "$OUT/$file"; test -s "$OUT/$file"
}

adb shell pm clear "$PKG" >/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
shot 3 0 1 0 "00-naepo-real-home.png"
shot 3 0 1 1 "01-naepo-real-h1-red.png"
shot 3 0 2 1 "02-naepo-real-h2-red.png"
shot 3 0 4 1 "03-naepo-real-h4-red.png"
shot 3 0 6 1 "04-naepo-real-h6-red.png"
shot 3 0 9 1 "05-naepo-real-h9-red.png"
# Physical H1 reused on second loop with published Yellow-flag meter/par pack.
shot 3 0 10 1 "06-naepo-real-h10-yellow.png"
# Reverse-order variant starts with Yellow flag.
shot 3 1 3 1 "07-naepo-yellow-first-h3.png"
# Direct-map SIM movement: orange pulse stays on the real map and remaining m changes.
shot 3 0 6 1 "08-naepo-h6-before-progress.png"
adb shell input tap 540 900; sleep .5
adb exec-out screencap -p > "$OUT/09-naepo-h6-progress.png"; test -s "$OUT/09-naepo-h6-progress.png"
shot 3 0 1 3 "10-naepo-real-scorecard.png"
adb shell wm size 720x1600; adb shell wm density 320; sleep .4
shot 3 0 2 1 "11-compact-naepo-h2-real.png"
adb shell wm size reset; adb shell wm density reset
if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.13.2 Naepo real-yardage preview run"; adb logcat -d | tail -500; exit 1
fi
printf 'V1.13.2 Naepo real-yardage screenshots:\n'; ls -lh "$OUT"/*.png
