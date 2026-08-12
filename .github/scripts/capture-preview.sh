#!/usr/bin/env bash
set -euo pipefail

APK="HokkaidoGolfGPS-v1.6.2-debug.apk"
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
adb shell am start -n "$ACTIVITY" --ez preview true
sleep 5
adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true
adb exec-out screencap -p > "$OUT/01-home.png"

# First round start opens the one-time P1~P4 two-character name dialog.
adb shell input tap 540 1840
sleep 2
adb exec-out screencap -p > "$OUT/02-player-name-dialog.png"

# Seed the same two-character preview names after the dialog capture, then restart.
adb shell am force-stop "$PKG" || true
adb shell run-as "$PKG" sh -c 'mkdir -p shared_prefs; cat > shared_prefs/state_v09.xml <<"EOF"
<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<map>
  <string name="player_name_0">&#xAC00;&#xB78C;</string>
  <string name="player_name_1">&#xB098;&#xB798;</string>
  <string name="player_name_2">&#xB2E4;&#xC628;</string>
  <string name="player_name_3">&#xB77C;&#xC628;</string>
  <boolean name="player_names_set" value="true" />
</map>
EOF'
adb shell am start -n "$ACTIVITY" --ez preview true
sleep 4
adb shell input tap 540 1840
sleep 3

# Live course keeps the saved names in the player strip.
adb exec-out screencap -p > "$OUT/03-course-named-players.png"

# Score Input: names replace P1~P4; edit button remains available.
adb shell input tap 415 2290
sleep 2
adb exec-out screencap -p > "$OUT/04-score-input-names.png"

# Scorecard: two-character names are used in both table headers and round-summary cards.
adb shell input tap 670 2290
sleep 2
adb exec-out screencap -p > "$OUT/05-scorecard-names.png"

printf 'V1.6.2 player-name screenshots captured:\n'
ls -lh "$OUT"/*.png
