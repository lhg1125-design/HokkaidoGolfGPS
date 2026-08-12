#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.9.0-actual-yardage-pack-debug.apk"
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
  <string name="player_name_0">누나</string>
  <string name="player_name_1">매형</string>
  <string name="player_name_2">희권</string>
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

shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  launch_screen "$course" "$variant" "$hole" "$screen"
  adb exec-out screencap -p > "$OUT/$file"
}

# Home and exact-distance yardage verification. H1/H2 prove that hole graphics change.
shot 0 0 1 0 "01-home-v190.png"
shot 0 0 1 1 "02-kamishihoro-h1-yardage.png"
shot 0 0 2 1 "03-kamishihoro-h2-yardage.png"
shot 1 0 5 1 "04-furano-palmer-h5-yardage.png"
shot 1 1 12 1 "05-furano-king-h12-yardage.png"
shot 2 0 3 1 "06-sahoro-h3-yardage.png"
shot 3 0 1 1 "07-naepo-field-yardage.png"
shot 4 0 1 1 "08-royallinks-queens-h1-yardage.png"
shot 4 1 12 1 "09-royallinks-kings-h12-yardage.png"

# Score/card safe-bounds validation.
shot 4 0 1 2 "10-score-input-safe.png"
shot 4 0 1 3 "11-scorecard-safe.png"

printf 'V1.9.0 actual yardage screenshots:\n'
ls -lh "$OUT"/*.png
