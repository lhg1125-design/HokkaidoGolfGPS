#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.10.0-field-beta-debug.apk"
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
adb shell settings put secure immersive_mode_confirmations confirmed || true

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
  adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true
  sleep 0.8
}

shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 2.2
  clear_system_dialogs
  adb exec-out screencap -p > "$OUT/$file"
  test -s "$OUT/$file"
}

# Baseline + high-value official-guide holes for tomorrow's field beta.
shot 0 0 1 0 "01-home-v110.png"
shot 0 0 4 1 "02-kamishihoro-champions-h4.png"
shot 0 1 12 1 "03-kamishihoro-masters-h12.png"
shot 0 1 13 1 "04-kamishihoro-masters-h13-dogleg.png"
shot 0 1 15 1 "05-kamishihoro-masters-h15.png"
shot 1 0 15 1 "06-furano-palmer-h15.png"
shot 1 1 17 1 "07-furano-king-h17.png"
shot 2 0 3 1 "08-sahoro-h3.png"
shot 4 0 1 2 "09-score-input.png"
shot 4 0 1 3 "10-scorecard.png"

# Compact-device containment test: render the same complex hole at 720x1600.
adb shell wm size 720x1600
adb shell wm density 320
sleep 1
shot 0 1 13 1 "11-compact-720x1600-yardage.png"
shot 4 0 1 3 "12-compact-720x1600-scorecard.png"
adb shell wm size reset
adb shell wm density reset

# Hard crash gate. The build fails if our package produced a Java fatal exception.
if adb logcat -d | grep -E "FATAL EXCEPTION|Process: ${PKG}" | grep -q "${PKG}\|FATAL EXCEPTION"; then
  echo "App crash detected during V1.10 preview run"
  adb logcat -d | tail -500
  exit 1
fi

printf 'V1.10 field beta screenshots:\n'
ls -lh "$OUT"/*.png
