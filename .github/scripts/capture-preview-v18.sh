#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.8.0-premium-art-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview"
mkdir -p "$OUT"
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global hide_error_dialogs 1 || true
adb shell settings put global show_first_crash_dialog 0 || true

# Preconfigure 3 named players so the normal production start flow can enter the
# round immediately. This tests the same route a golfer uses instead of forcing
# the drawing screen through a preview-only shortcut.
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

launch_home(){
  local course="$1" variant="$2" hole="$3"
  adb shell am force-stop "$PKG" || true
  adb logcat -c || true
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen 0 >/dev/null
  sleep 5
}

shot_round(){
  local course="$1" variant="$2" hole="$3" file="$4"
  echo "===== NORMAL ROUND course=$course variant=$variant hole=$hole file=$file ====="
  launch_home "$course" "$variant" "$hole"
  # Home start button, Pixel 6 / 1080x2400 capture profile.
  adb shell input tap 540 1940
  sleep 7
  echo "FOCUS: $(adb shell dumpsys window | grep -m1 'mCurrentFocus' || true)"
  if adb shell pidof "$PKG" >/dev/null 2>&1; then echo "APP ALIVE: $(adb shell pidof "$PKG")"; else echo "APP NOT RUNNING"; fi
  adb logcat -d -v brief | grep -E 'FATAL EXCEPTION|AndroidRuntime|ArrayIndexOutOfBounds|IndexOutOfBounds|NullPointerException|IllegalArgumentException' | tail -n 30 || true
  adb exec-out screencap -p > "$OUT/$file"
}

# Home: Korea selector + Taegeukgi + V1.8 badge.
launch_home 3 0 1
adb exec-out screencap -p > "$OUT/01-home-premium.png"

# Japan premium-art screens.
shot_round 0 0 11 "02-kamishihoro-premium.png"
shot_round 1 0 4  "03-furano-premium.png"
shot_round 2 0 1  "04-sahoro-premium.png"

# Korea premium-art screens.
shot_round 3 0 1  "05-naepo-premium.png"
shot_round 4 0 1  "06-royallinks-queens-premium.png"
shot_round 4 1 12 "07-royallinks-kings-premium.png"

printf 'V1.8 premium screenshots:\n'
ls -lh "$OUT"/*.png
