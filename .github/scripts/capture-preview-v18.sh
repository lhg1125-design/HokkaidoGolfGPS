#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.8.2-yardage-ux-debug.apk"
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
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true

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

launch_screen(){
  local course="$1" variant="$2" hole="$3" screen="$4"
  adb shell am force-stop "$PKG" || true
  kill_launcher_overlay
  adb logcat -c || true
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 4
  kill_launcher_overlay
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 2
}

shot_round(){
  local course="$1" variant="$2" hole="$3" file="$4"
  echo "===== YARDAGE ROUND course=$course variant=$variant hole=$hole file=$file ====="
  launch_screen "$course" "$variant" "$hole" 1
  echo "FOCUS: $(adb shell dumpsys window | grep -m1 'mCurrentFocus' || true)"
  echo "APP PID: $(adb shell pidof "$PKG" || true)"
  adb exec-out screencap -p > "$OUT/$file"
}

launch_screen 0 0 2 0
adb exec-out screencap -p > "$OUT/01-home.png"
shot_round 0 0 2 "02-kamishihoro-h2-yardage.png"
shot_round 0 0 3 "03-kamishihoro-h3-yardage.png"
shot_round 1 0 4 "04-furano-h4-yardage.png"
shot_round 2 0 1 "05-sahoro-h1-yardage.png"
shot_round 3 0 1 "06-naepo-h1-yardage.png"
shot_round 4 0 1 "07-royallinks-h1-yardage.png"

# Open the player setup dialog from the score-input screen to verify the 3/4
# segmented control and keyboard-safe name fields.
launch_screen 0 0 2 2
adb shell input tap 890 225
sleep 2
adb exec-out screencap -p > "$OUT/08-player-setup-3-4-toggle.png"

printf 'V1.8.2 yardage/UX screenshots:\n'
ls -lh "$OUT"/*.png
