#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.13.0-concept-art-skin-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
SIM_ACTIVITY="com.hokkaidogolf.trip/.BetaSimActivity"
OUT="preview-v1130"
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
  sleep .5
  adb exec-out screencap -p > "$OUT/$file"
  test -s "$OUT/$file"
}

# Concept-art home / simulator launcher.
adb shell am force-stop "$PKG" || true; clear_system_dialogs
adb shell am start -W -n "$SIM_ACTIVITY" >/dev/null; sleep .8
adb exec-out screencap -p > "$OUT/00-concept-beta-launcher.png"

# Four representative animated-style full-hole maps.
shot 2 0 13 1 "01-sahoro-h13-concept-yardage.png"
shot 0 0 1 1 "02-kamishihoro-c-h1-concept-yardage.png"
shot 1 0 15 1 "03-furano-palmer-h15-concept-yardage.png"
shot 4 0 1 1 "04-royallinks-q-h1-concept-yardage.png"

# Verify circular hole movement remains functional after the visual re-skin.
shot 2 0 13 1 "05-sahoro-h13-hole-buttons.png"
adb shell input tap 1017 522
sleep .6
adb exec-out screencap -p > "$OUT/06-sahoro-next-h14.png"

# Dedicated score UI and compact-screen rendering.
shot 2 0 13 3 "07-scorecard-concept-font.png"
adb shell wm size 720x1600; adb shell wm density 320; sleep .6
shot 2 0 13 1 "08-compact-sahoro-concept-yardage.png"
shot 0 0 1 1 "09-compact-kamishihoro-concept-yardage.png"
adb shell wm size reset; adb shell wm density reset

if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.13.0 concept-art preview run"
  adb logcat -d | tail -500
  exit 1
fi
printf 'V1.13.0 concept-art screenshots:\n'; ls -lh "$OUT"/*.png
