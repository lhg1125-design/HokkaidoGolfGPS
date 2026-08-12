#!/usr/bin/env bash
set -euo pipefail

APK="HokkaidoGolfGPS-v1.7.0-korea-test-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview"

mkdir -p "$OUT"
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global hide_error_dialogs 1 || true
adb shell settings put global show_first_crash_dialog 0 || true
adb shell am force-stop com.google.android.apps.nexuslauncher || true
adb shell am force-stop com.android.launcher3 || true

adb shell am force-stop "$PKG" || true
adb shell pm clear "$PKG" >/dev/null 2>&1 || true
adb install -r "$APK" >/dev/null
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell am start -n "$ACTIVITY" --ez preview true
sleep 5
adb exec-out screencap -p > "$OUT/01-home-korea-test.png"

# Naepo test card is the first Korea card.
adb shell input tap 540 1340
sleep 2
adb exec-out screencap -p > "$OUT/02-naepo-selected.png"

# First round opens dynamic player-count/name setup.
adb shell input tap 540 1980
sleep 2
adb exec-out screencap -p > "$OUT/03-player-setup.png"

# Seed 3 active players so all later screenshots verify linked slots/records.
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
adb shell am start -n "$ACTIVITY" --ez preview true
sleep 4
adb shell input tap 540 1340
sleep 1
adb shell input tap 540 1980
sleep 3
adb exec-out screencap -p > "$OUT/04-naepo-field-cal.png"

# Score input: exactly 3 player cards.
adb shell input tap 415 2290
sleep 2
adb exec-out screencap -p > "$OUT/05-naepo-score-input.png"

# Scorecard: names and three-player totals only.
adb shell input tap 670 2290
sleep 2
adb exec-out screencap -p > "$OUT/06-naepo-scorecard.png"

# Summary: per-player cards + persistent ROUND SAVED record.
adb shell input tap 900 2290
sleep 2
adb exec-out screencap -p > "$OUT/07-round-summary-saved.png"

# Relaunch home and validate Royal Links official-white vector yardage.
adb shell am force-stop "$PKG" || true
adb shell am start -n "$ACTIVITY" --ez preview true
sleep 3
adb shell input tap 540 1540
sleep 1
adb shell input tap 540 1980
sleep 3
adb exec-out screencap -p > "$OUT/08-royallinks-queens-yardage.png"

printf 'V1.7.0 Korea field-test screenshots captured:\n'
ls -lh "$OUT"/*.png
