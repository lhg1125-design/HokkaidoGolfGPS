#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.10.1-field-yardage-safe-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
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

shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true
  clear_system_dialogs
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 2.4
  clear_system_dialogs
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 1.0
  adb exec-out screencap -p > "$OUT/$file"
  test -s "$OUT/$file"
}

# Japan actual published yardages; consecutive holes prove map/card changes.
shot 0 0 1 1 "01-kamishihoro-champions-h1.png"
shot 0 0 2 1 "02-kamishihoro-champions-h2.png"
shot 0 1 13 1 "03-kamishihoro-masters-h13.png"
shot 1 0 5 1 "04-furano-palmer-h5.png"
shot 1 1 12 1 "05-furano-king-h12.png"
shot 2 0 3 1 "06-sahoro-h3.png"

# Korea: Naepo must stay CAL REQUIRED until real tee+green are captured;
# Royal Links uses official WHITE meters.
shot 3 0 1 1 "07-naepo-cal-required.png"
shot 4 0 1 1 "08-royallinks-queens-h1.png"
shot 4 1 12 1 "09-royallinks-kings-h12.png"

# Player/score containment.
shot 4 0 1 2 "10-score-input.png"
shot 4 0 1 3 "11-scorecard.png"

# Compact-device containment gate: no pager / card / footer clipping.
adb shell wm size 720x1600
adb shell wm density 320
sleep 1
shot 0 0 2 1 "12-compact-kamishihoro-h2.png"
shot 4 0 1 3 "13-compact-scorecard.png"
adb shell wm size reset
adb shell wm density reset

if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.10.1 preview run"
  adb logcat -d | tail -500
  exit 1
fi

printf 'V1.10.1 field yardage safe screenshots:\n'
ls -lh "$OUT"/*.png
