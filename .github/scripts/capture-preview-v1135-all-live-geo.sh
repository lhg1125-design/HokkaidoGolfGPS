#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.13.5-all-live-geo-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1135-all-live-geo"
mkdir -p "$OUT"; rm -f "$OUT"/*.png
adb logcat -c || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
clear_system_dialogs(){ adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true; sleep .25; }
shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true; clear_system_dialogs
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 1.0; clear_system_dialogs
  adb exec-out screencap -p > "$OUT/$file"; test -s "$OUT/$file"
}

adb shell pm clear "$PKG" >/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true

# Japan: both course variants and representative dogleg/long-hole shapes.
shot 0 0 11 1 "00-kamishihoro-champions-h11-live2d.png"
shot 0 1 13 1 "01-kamishihoro-masters-h13-live2d.png"
shot 1 0 15 1 "02-furano-palmer-h15-live2d.png"
shot 1 1 17 1 "03-furano-king-h17-live2d.png"
shot 2 0 7 1 "04-sahoro-h07-live2d.png"

# Korea: Naepo two-green mapping and Royal Links both course variants.
shot 3 0 4 1 "05-naepo-red-h04-live2d.png"
shot 3 0 13 1 "06-naepo-yellow-h13-live2d.png"
shot 4 0 7 1 "07-royallinks-queens-h07-live2d.png"
shot 4 1 10 1 "08-royallinks-kings-h10-live2d.png"

# Compact display guard: map must stay full-fit, chips/buttons visible.
adb shell wm size 720x1600; adb shell wm density 320; sleep .4
shot 0 0 18 1 "09-compact-japan-h18.png"
shot 3 0 9 1 "10-compact-naepo-h09.png"
shot 4 1 18 1 "11-compact-royallinks-h18.png"
adb shell wm size reset; adb shell wm density reset

# Score regression.
shot 4 0 1 3 "12-royallinks-scorecard.png"

if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.13.5 preview run"; adb logcat -d | tail -500; exit 1
fi
printf 'V1.13.5 all-course LIVE GEO screenshots:\n'; ls -lh "$OUT"/*.png
