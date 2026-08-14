#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.15.1-reference-polish-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1138-cover-hud"
mkdir -p "$OUT"; rm -f "$OUT"/*.png
adb logcat -c || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
wake(){ adb shell input keyevent 224 >/dev/null 2>&1 || true; adb shell wm dismiss-keyguard >/dev/null 2>&1 || true; adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true; sleep .4; }
shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true
  wake
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 1.4
  wake
  adb exec-out screencap -p > "$OUT/$file"
  test -s "$OUT/$file"
}
adb shell pm clear "$PKG" >/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true

# V1.15.1 reference checks: 3-column yardage, dark nav, clean landscape, relative PAR score.
shot 2 0 7 0 "00-storybook-home.png"
shot 2 0 7 1 "01-sahoro-h07-storybook-yardage.png"
shot 2 0 7 2 "02-storybook-score-relative-par.png"
shot 4 0 7 1 "03-royallinks-queens-h07-storybook.png"
shot 1 0 15 1 "04-furano-palmer-h15-storybook.png"
shot 3 0 6 1 "05-naepo-h6-cover-hud.png"
shot 3 0 5 1 "06-naepo-h5-cover-hud.png"
shot 2 0 13 1 "07-sahoro-h13-cover-hud.png"
shot 3 0 1 4 "08-round-summary-log-button.png"
adb shell wm size 948x1048; adb shell wm density 320; sleep .6
shot 3 0 6 1 "09-flip-cover-naepo-h6.png"
shot 3 0 5 1 "10-flip-cover-naepo-h5.png"
adb shell wm size 720x1600; adb shell wm density 320; sleep .5
shot 2 0 7 0 "11-compact-storybook-home.png"
shot 2 0 7 2 "12-compact-storybook-score-relative-par.png"
shot 3 0 6 1 "13-compact-naepo-h6.png"
adb shell wm size reset; adb shell wm density reset; sleep .5
adb shell am force-stop "$PKG" || true
wake
adb shell am start -W -a android.settings.APPLICATION_DETAILS_SETTINGS -d "package:${PKG}" >/dev/null
sleep 1.4
wake
adb exec-out screencap -p > "$OUT/14-app-icon-app-info.png"
test -s "$OUT/14-app-icon-app-info.png"
if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.15.1 REFERENCE POLISH preview run"; adb logcat -d | tail -500; exit 1
fi
printf 'V1.15.1 REFERENCE POLISH screenshots:\n'; ls -lh "$OUT"/*.png
