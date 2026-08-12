#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.8.1-premium-art-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview"
mkdir -p "$OUT"
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global hide_error_dialogs 1 || true
adb shell settings put global show_first_crash_dialog 0 || true
adb shell settings put secure anr_show_background 0 || true
# Pixel Launcher can ANR on the headless software-rendered emulator and cover the
# app despite the app itself being healthy. Stop launchers before every capture.
adb shell am force-stop com.google.android.apps.nexuslauncher || true
adb shell am force-stop com.android.launcher3 || true
sleep 1

cat > /tmp/state_v09.xml <<'EOF'
<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<map>
  <int name="player_count" value="3" />
  <string name="player_name_0">가람</string>
  <string name="player_name_1">나래</string>
  <string name="player_name_2">다온</string>
  <boolean name="player_names_set" value="true" />
</map>
EOF
adb shell am force-stop "$PKG" || true
adb shell run-as "$PKG" mkdir -p shared_prefs
adb shell run-as "$PKG" tee shared_prefs/state_v09.xml < /tmp/state_v09.xml >/dev/null

kill_launcher_overlay(){
  adb shell am force-stop com.google.android.apps.nexuslauncher || true
  adb shell am force-stop com.android.launcher3 || true
  sleep 1
}

launch_home(){
  local course="$1" variant="$2" hole="$3"
  adb shell am force-stop "$PKG" || true
  kill_launcher_overlay
  adb logcat -c || true
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen 0 >/dev/null
  sleep 4
  kill_launcher_overlay
  # Bring our Activity back to the foreground after stopping Launcher.
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen 0 >/dev/null
  sleep 2
}

shot_round(){
  local course="$1" variant="$2" hole="$3" file="$4"
  echo "===== PREMIUM ROUND course=$course variant=$variant hole=$hole file=$file ====="
  launch_home "$course" "$variant" "$hole"
  adb shell input tap 540 1940
  sleep 5
  kill_launcher_overlay
  echo "FOCUS: $(adb shell dumpsys window | grep -m1 'mCurrentFocus' || true)"
  echo "APP PID: $(adb shell pidof "$PKG" || true)"
  adb exec-out screencap -p > "$OUT/$file"
}

launch_home 3 0 1
adb exec-out screencap -p > "$OUT/01-home-premium.png"
shot_round 0 0 11 "02-kamishihoro-premium.png"
shot_round 1 0 4  "03-furano-premium.png"
shot_round 2 0 1  "04-sahoro-premium.png"
shot_round 3 0 1  "05-naepo-premium.png"
shot_round 4 0 1  "06-royallinks-queens-premium.png"
shot_round 4 1 12 "07-royallinks-kings-premium.png"

printf 'V1.8.1 premium screenshots:\n'
ls -lh "$OUT"/*.png
