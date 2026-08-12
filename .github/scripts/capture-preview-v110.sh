#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.12.2-map-pin-focus-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
SIM_ACTIVITY="com.hokkaidogolf.trip/.BetaSimActivity"
PREFLIGHT_ACTIVITY="com.hokkaidogolf.trip/.FieldPreflightActivity"
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
  sleep 0.4
}

adb shell am force-stop "$PKG" || true; clear_system_dialogs
adb shell am start -W -n "$SIM_ACTIVITY" >/dev/null; sleep .8; clear_system_dialogs
adb shell am start -n "$SIM_ACTIVITY" >/dev/null; sleep .4
adb exec-out screencap -p > "$OUT/00-beta-sim-launcher.png"

adb shell am force-stop "$PKG" || true; clear_system_dialogs
adb shell am start -W -n "$PREFLIGHT_ACTIVITY" --ez preview true >/dev/null; sleep .8
adb exec-out screencap -p > "$OUT/01-field-preflight-ready.png"
test -s "$OUT/01-field-preflight-ready.png"

shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true; clear_system_dialogs
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 1.05; clear_system_dialogs
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep .45; adb exec-out screencap -p > "$OUT/$file"; test -s "$OUT/$file"
}

# Meter-only yardage + direct orange map pin. No separate YOU legend/axis.
shot 2 0 13 1 "02-sahoro-h13-meter-pin-42.png"
# Tap directly on the hole image to move SIM position toward the green.
adb shell input tap 540 900
sleep .7
adb exec-out screencap -p > "$OUT/03-sahoro-h13-meter-pin-moved.png"
test -s "$OUT/03-sahoro-h13-meter-pin-moved.png"
shot 2 0 1 1 "04-sahoro-h1-meter-pin.png"
shot 0 1 13 1 "05-kamishihoro-m-h13-meter-pin.png"
shot 4 0 1 1 "06-royallinks-queens-h1-meter-pin.png"
shot 3 0 1 1 "07-naepo-cal-required.png"
shot 4 0 1 3 "08-scorecard.png"

# Compact containment: full TEE->GREEN art + direct orange pin + meter-only row.
adb shell wm size 720x1600; adb shell wm density 320; sleep .6
shot 2 0 13 1 "09-compact-sahoro-h13-meter-pin.png"
shot 4 0 1 1 "10-compact-royallinks-h1-meter-pin.png"
adb shell wm size reset; adb shell wm density reset

if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.12.2 preview run"; adb logcat -d | tail -500; exit 1
fi
printf 'V1.12.2 meter-only direct-pin screenshots:\n'; ls -lh "$OUT"/*.png
