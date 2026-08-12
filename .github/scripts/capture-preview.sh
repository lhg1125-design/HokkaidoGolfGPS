#!/usr/bin/env bash
set -euo pipefail

APK="HokkaidoGolfGPS-v1.6.3-debug.apk"
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
adb exec-out screencap -p > "$OUT/01-home.png"

# First round opens player-count setup. Preview defaults to 3 players, so only 3 name slots are visible.
adb shell input tap 540 1840
sleep 2
adb exec-out screencap -p > "$OUT/02-player-count-slots.png"

# Seed a 3-player setup to verify that every later screen creates only 3 linked player slots.
adb shell am force-stop "$PKG" || true
adb shell run-as "$PKG" sh -c 'mkdir -p shared_prefs; cat > shared_prefs/state_v09.xml <<"EOF"
<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<map>
  <int name="player_count" value="3" />
  <string name="player_name_0">&#xAC00;&#xB78C;</string>
  <string name="player_name_1">&#xB098;&#xB798;</string>
  <string name="player_name_2">&#xB2E4;&#xC628;</string>
  <boolean name="player_names_set" value="true" />
</map>
EOF'
adb shell am start -n "$ACTIVITY" --ez preview true
sleep 4
adb shell input tap 540 1840
sleep 3
adb exec-out screencap -p > "$OUT/03-course-3players.png"

# Score input should render exactly 3 player cards.
adb shell input tap 415 2290
sleep 2
adb exec-out screencap -p > "$OUT/04-score-input-3players.png"

# Scorecard should render 3 named columns and 3 summary cards, no unused P4 slot.
adb shell input tap 670 2290
sleep 2
adb exec-out screencap -p > "$OUT/05-scorecard-3players.png"

printf 'V1.6.3 dynamic-player screenshots captured:\n'
ls -lh "$OUT"/*.png
