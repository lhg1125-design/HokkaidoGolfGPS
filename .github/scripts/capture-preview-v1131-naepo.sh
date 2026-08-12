#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.13.1-naepo-field-test-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1131-naepo"
mkdir -p "$OUT"; rm -f "$OUT"/*.png

adb logcat -c || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true

clear_system_dialogs(){
  adb shell am force-stop com.google.android.apps.nexuslauncher >/dev/null 2>&1 || true
  adb shell am force-stop com.android.launcher3 >/dev/null 2>&1 || true
  adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true
  sleep .35
}

shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true; clear_system_dialogs
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 1.0; clear_system_dialogs
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep .55
  adb exec-out screencap -p > "$OUT/$file"
  test -s "$OUT/$file"
}

# Real app entrance keeps the approved concept-art skin.
adb shell pm clear "$PKG" >/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
clear_system_dialogs
adb shell am start -W -n "$ACTIVITY" >/dev/null; sleep 1.0; clear_system_dialogs
adb exec-out screencap -p > "$OUT/00-app-home-concept.png"
test -s "$OUT/00-app-home-concept.png"

# Naepo selected on the same wood-sign home UI.
shot 3 0 1 0 "01-naepo-home-selected.png"

# Complete field-cal flow in explicit SIM mode: RED first loop, H1.
shot 3 0 1 1 "02-naepo-h1-field-ready.png"
# Direct map tap moves the orange player position and updates remaining distance.
adb shell input tap 540 920
sleep .65
adb exec-out screencap -p > "$OUT/03-naepo-h1-progress.png"
test -s "$OUT/03-naepo-h1-progress.png"

# Second nine uses the other green while keeping the 9-hole physical-hole label.
shot 3 0 10 1 "04-naepo-h10-second-green.png"
# Reverse order variant: YELLOW first.
shot 3 1 1 1 "05-naepo-yellow-first.png"

# Circular top hole-step button must still work on the Naepo field canvas.
shot 3 0 1 1 "06-naepo-h1-before-next.png"
adb shell input tap 1005 285
sleep .65
adb exec-out screencap -p > "$OUT/07-naepo-next-h2.png"
test -s "$OUT/07-naepo-next-h2.png"

# Scorecard uses the same rounded concept typography.
shot 3 0 1 3 "08-naepo-scorecard.png"

# Compact-device check.
adb shell wm size 720x1600; adb shell wm density 320; sleep .6
shot 3 0 1 1 "09-compact-naepo-field-ready.png"
adb shell wm size reset; adb shell wm density reset

if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.13.1 Naepo field-test preview run"
  adb logcat -d | tail -500
  exit 1
fi
printf 'V1.13.1 Naepo field-test screenshots:\n'; ls -lh "$OUT"/*.png
