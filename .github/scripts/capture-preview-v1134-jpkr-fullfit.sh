#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.13.4-jpkr-2d-fullfit-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1134-jpkr-fullfit"
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
  sleep 1.15; clear_system_dialogs
  adb exec-out screencap -p > "$OUT/$file"; test -s "$OUT/$file"
}

adb shell pm clear "$PKG" >/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true

# Japan: representative long / dogleg / par-3 holes from every source pack.
shot 0 0 11 1 "00-kamishihoro-champions-h11.png"
shot 0 1 13 1 "01-kamishihoro-masters-h13.png"
shot 1 0 15 1 "02-furano-palmer-h15.png"
shot 1 1 4 1 "03-furano-king-h04.png"
shot 2 0 7 1 "04-sahoro-h07.png"

# Korea: Naepo two-green physical mapping + Royal Links both courses.
shot 3 0 4 1 "05-naepo-red-h04.png"
shot 3 0 13 1 "06-naepo-yellow-logical-h13.png"
shot 4 0 7 1 "07-royallinks-queens-h07.png"
shot 4 1 10 1 "08-royallinks-kings-h10.png"

# Compact-screen safe-fit check. Entire map + footer + bottom nav must remain visible.
adb shell wm size 720x1600; adb shell wm density 320; sleep .45
shot 0 0 18 1 "09-compact-kamishihoro-h18.png"
shot 4 1 18 1 "10-compact-royallinks-h18.png"
adb shell wm size reset; adb shell wm density reset

# Score screen regression guard.
shot 3 0 1 3 "11-naepo-scorecard.png"

if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.13.4 JP/KR full-fit preview run"; adb logcat -d | tail -500; exit 1
fi
printf 'V1.13.4 JP/KR full-fit screenshots:\n'; ls -lh "$OUT"/*.png
