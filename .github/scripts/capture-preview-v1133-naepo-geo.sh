#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.13.3-naepo-2d-geo-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1133-naepo-geo"
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
  sleep .85; clear_system_dialogs
  adb exec-out screencap -p > "$OUT/$file"; test -s "$OUT/$file"
}

adb shell pm clear "$PKG" >/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
shot 3 0 1 1 "00-naepo-h1-centerline.png"
# left/right taps at similar vertical progress: orange pin should follow the actual drawn corridor and lateral offset.
adb shell input tap 365 930; sleep .45
adb exec-out screencap -p > "$OUT/01-naepo-h1-left-offset.png"; test -s "$OUT/01-naepo-h1-left-offset.png"
adb shell input tap 710 930; sleep .45
adb exec-out screencap -p > "$OUT/02-naepo-h1-right-offset.png"; test -s "$OUT/02-naepo-h1-right-offset.png"
shot 3 0 4 1 "03-naepo-h4-real-curve.png"
adb shell input tap 455 760; sleep .45
adb exec-out screencap -p > "$OUT/04-naepo-h4-progress-curve.png"; test -s "$OUT/04-naepo-h4-progress-curve.png"
shot 3 0 6 1 "05-naepo-h6-red.png"
shot 3 0 9 1 "06-naepo-h9-red.png"
shot 3 0 10 1 "07-naepo-h10-yellow.png"
shot 3 1 3 1 "08-naepo-yellow-first-h3.png"
shot 3 0 1 3 "09-naepo-scorecard.png"
adb shell wm size 720x1600; adb shell wm density 320; sleep .4
shot 3 0 2 1 "10-compact-naepo-h2-geo.png"
adb shell wm size reset; adb shell wm density reset
if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.13.3 Naepo 2D geo preview run"; adb logcat -d | tail -500; exit 1
fi
printf 'V1.13.3 Naepo 2D geo screenshots:\n'; ls -lh "$OUT"/*.png
