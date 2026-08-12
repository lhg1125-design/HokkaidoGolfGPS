#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.10.4-hokkaido-full-hole-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
SIM_ACTIVITY="com.hokkaidogolf.trip/.BetaSimActivity"
OUT="preview"
mkdir -p "$OUT"; rm -f "$OUT"/*.png

adb logcat -c || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global hide_error_dialogs 1 || true
adb shell settings put global show_first_crash_dialog 0 || true
adb shell settings put secure anr_show_background 0 || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true

clear_system_dialogs(){
  adb shell am force-stop com.google.android.apps.nexuslauncher >/dev/null 2>&1 || true
  adb shell am force-stop com.android.launcher3 >/dev/null 2>&1 || true
  adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true
  sleep 0.5
}

adb shell am force-stop "$PKG" || true; clear_system_dialogs
adb shell am start -W -n "$SIM_ACTIVITY" >/dev/null; sleep 1.0; clear_system_dialogs
adb shell am start -n "$SIM_ACTIVITY" >/dev/null; sleep 0.5
adb exec-out screencap -p > "$OUT/00-beta-sim-launcher.png"

shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true; clear_system_dialogs
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 1.4; clear_system_dialogs
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 0.6; adb exec-out screencap -p > "$OUT/$file"; test -s "$OUT/$file"
}

# Hokkaido full-hole map gate: tee and green must both remain visible.
shot 0 0 1 1 "01-kamishihoro-c-h1-full.png"
shot 0 1 13 1 "02-kamishihoro-m-h13-full.png"
shot 1 0 15 1 "03-furano-palmer-h15-full.png"
shot 1 1 17 1 "04-furano-king-h17-full.png"
shot 2 0 1 1 "05-sahoro-h1-full.png"
shot 2 0 13 1 "06-sahoro-h13-full.png"

# Korea: Naepo truth guard + Royal Links official Queens/Kings maps.
shot 3 0 1 1 "07-naepo-cal-required.png"
shot 4 0 1 1 "08-royallinks-queens-h1-full.png"
shot 4 1 14 1 "09-royallinks-kings-h14-full.png"
shot 4 0 1 3 "10-scorecard.png"

# Compact containment gate, including Sahoro.
adb shell wm size 720x1600; adb shell wm density 320; sleep 0.7
shot 0 0 1 1 "11-compact-kamishihoro-h1-full.png"
shot 2 0 13 1 "12-compact-sahoro-h13-full.png"
shot 4 0 1 1 "13-compact-royallinks-h1-full.png"
adb shell wm size reset; adb shell wm density reset

if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.10.4 preview run"; adb logcat -d | tail -500; exit 1
fi
printf 'V1.10.4 Hokkaido full-hole yardage screenshots:\n'; ls -lh "$OUT"/*.png
