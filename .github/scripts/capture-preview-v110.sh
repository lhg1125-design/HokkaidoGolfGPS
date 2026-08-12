#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.10.2-full-hole-yardage-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
SIM_ACTIVITY="com.hokkaidogolf.trip/.BetaSimActivity"
OUT="preview"
mkdir -p "$OUT"
rm -f "$OUT"/*.png

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

cat > /tmp/state_v09.xml <<'EOF'
<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<map>
  <int name="player_count" value="3" />
  <string name="player_name_0">누나</string>
  <string name="player_name_1">매형</string>
  <string name="player_name_2">희권</string>
  <boolean name="player_names_set" value="true" />
</map>
EOF
adb shell am force-stop "$PKG" || true
adb shell run-as "$PKG" mkdir -p shared_prefs
adb shell run-as "$PKG" tee shared_prefs/state_v09.xml < /tmp/state_v09.xml >/dev/null

clear_system_dialogs(){
  adb shell am force-stop com.google.android.apps.nexuslauncher >/dev/null 2>&1 || true
  adb shell am force-stop com.android.launcher3 >/dev/null 2>&1 || true
  adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true
  sleep 0.8
}

adb shell am force-stop "$PKG" || true
clear_system_dialogs
adb shell am start -W -n "$SIM_ACTIVITY" >/dev/null
sleep 1.3
clear_system_dialogs
adb shell am start -n "$SIM_ACTIVITY" >/dev/null
sleep 0.7
adb exec-out screencap -p > "$OUT/00-beta-sim-launcher.png"

a_shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true
  clear_system_dialogs
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 2.1
  clear_system_dialogs
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 0.9
  adb exec-out screencap -p > "$OUT/$file"
  test -s "$OUT/$file"
}

# Full tee -> green coverage gate. Long Par 5 + Par 3 + dogleg/strategy holes.
a_shot 0 0 1 1 "01-kamishihoro-champions-h1-full.png"
a_shot 0 0 11 1 "02-kamishihoro-champions-h11-full.png"
a_shot 0 1 13 1 "03-kamishihoro-masters-h13-full.png"
a_shot 0 1 18 1 "04-kamishihoro-masters-h18-full.png"
a_shot 1 0 5 1 "05-furano-palmer-h5-full.png"
a_shot 1 0 15 1 "06-furano-palmer-h15-full.png"
a_shot 1 1 12 1 "07-furano-king-h12-full.png"
a_shot 1 1 17 1 "08-furano-king-h17-full.png"

# Sahoro currently uses full-hole schematic until stable per-hole GDO asset URLs are verified.
a_shot 2 0 3 1 "09-sahoro-h3-full-schematic.png"
a_shot 2 0 13 1 "10-sahoro-h13-full-schematic.png"

# Korea guard rails.
a_shot 3 0 1 1 "11-naepo-cal-required.png"
a_shot 4 0 1 1 "12-royallinks-queens-h1.png"
a_shot 4 0 1 2 "13-score-input.png"
a_shot 4 0 1 3 "14-scorecard.png"

# Compact display: full image must remain center-inside with TEE and GREEN visible.
adb shell wm size 720x1600
adb shell wm density 320
sleep 1
a_shot 0 0 1 1 "15-compact-kamishihoro-h1-full.png"
a_shot 1 0 15 1 "16-compact-furano-h15-full.png"
a_shot 4 0 1 3 "17-compact-scorecard.png"
adb shell wm size reset
adb shell wm density reset

if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.10.2 preview run"
  adb logcat -d | tail -500
  exit 1
fi

printf 'V1.10.2 full-hole yardage screenshots:\n'
ls -lh "$OUT"/*.png
