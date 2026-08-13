#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.13.3-naepo-2d-geo-pin-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1133-naepo-polish"
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
  sleep .9; clear_system_dialogs
  adb exec-out screencap -p > "$OUT/$file"; test -s "$OUT/$file"
}

adb shell pm clear "$PKG" >/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
shot 3 0 1 0 "00-naepo-polished-home.png"
shot 3 0 1 1 "01-h1-centerline-default.png"
# Same H1: move forward and golfer-right. Pin should follow the real course corridor.
adb shell input tap 690 1120; sleep .65
adb exec-out screencap -p > "$OUT/02-h1-right-cross-track.png"; test -s "$OUT/02-h1-right-cross-track.png"
# Same H1: golfer-left comparison.
adb shell input tap 380 1050; sleep .65
adb exec-out screencap -p > "$OUT/03-h1-left-cross-track.png"; test -s "$OUT/03-h1-left-cross-track.png"
# Curved longer holes verify centerline following rather than a fixed vertical pin.
shot 3 0 4 1 "04-h4-curved-centerline.png"
adb shell input tap 660 1260; sleep .65
adb exec-out screencap -p > "$OUT/05-h4-right-progress.png"; test -s "$OUT/05-h4-right-progress.png"
shot 3 0 6 1 "06-h6-long-hole.png"
adb shell input tap 420 980; sleep .65
adb exec-out screencap -p > "$OUT/07-h6-left-progress.png"; test -s "$OUT/07-h6-left-progress.png"
shot 3 0 9 1 "08-h9-real-map.png"
# Physical H1 is reused on loop two; active green chip changes to YELLOW.
shot 3 0 10 1 "09-h10-yellow-green.png"
shot 3 1 3 1 "10-yellow-first-h3.png"
shot 3 0 1 3 "11-naepo-scorecard.png"
adb shell wm size 720x1600; adb shell wm density 320; sleep .5
shot 3 0 2 1 "12-compact-h2-2d-pin.png"
adb shell wm size reset; adb shell wm density reset
if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.13.3 Naepo polish preview run"; adb logcat -d | tail -500; exit 1
fi
printf 'V1.13.3 Naepo 2D geo-pin screenshots:\n'; ls -lh "$OUT"/*.png
