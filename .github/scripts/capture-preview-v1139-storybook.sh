#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.13.9-storybook-ui-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1139-storybook-ui"
mkdir -p "$OUT"; rm -f "$OUT"/*.png
adb logcat -c || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
wake(){ adb shell input keyevent 224 >/dev/null 2>&1 || true; adb shell wm dismiss-keyguard >/dev/null 2>&1 || true; adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true; sleep .35; }
shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true
  wake
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 1.35
  wake
  adb exec-out screencap -p > "$OUT/$file"
  test -s "$OUT/$file"
}
adb shell pm clear "$PKG" >/dev/null || true
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true

# Storybook visual language across the full app journey.
shot 2 0 7 0 "00-storybook-home.png"
shot 2 0 7 1 "01-sahoro-h07-storybook-yardage.png"
shot 4 0 7 1 "02-royallinks-queens-h07-storybook-yardage.png"
shot 1 0 15 1 "03-furano-palmer-h15-storybook-yardage.png"
shot 2 0 7 2 "04-storybook-score-one-tap.png"

# Compact phone: home and score must retain all controls without clipping.
adb shell wm size 720x1600; adb shell wm density 320; sleep .5
shot 2 0 7 0 "05-compact-storybook-home.png"
shot 2 0 7 2 "06-compact-storybook-score.png"
adb shell wm size reset; adb shell wm density reset; sleep .45

# Flip cover: live HUD remains glanceable after wooden storybook styling.
adb shell wm size 948x1048; adb shell wm density 320; sleep .55
shot 3 0 6 1 "07-flip-cover-storybook-live.png"
adb shell wm size reset; adb shell wm density reset

if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.13.9 STORYBOOK preview run"; adb logcat -d | tail -500; exit 1
fi
printf 'V1.13.9 STORYBOOK screenshots:\n'; ls -lh "$OUT"/*.png
