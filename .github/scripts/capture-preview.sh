#!/usr/bin/env bash
set -euo pipefail

APK="HokkaidoGolfGPS-v1.1-debug.apk"
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

# Preview location remains halfway between synthetic H11 TEE and GREEN.
adb emu geo fix 143.2283600 43.2585100 || true
adb shell am force-stop "$PKG" || true
adb shell am start -n "$ACTIVITY" --ez preview true
sleep 4
adb emu geo fix 143.2283600 43.2585100 || true
sleep 2
adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true
adb exec-out screencap -p > "$OUT/01-home-concept.png"

# Start round from the large orange start button.
adb shell input tap 540 2200
sleep 4
adb exec-out screencap -p > "$OUT/02-course-concept.png"

# Touch the live course to show target bubble.
adb shell input tap 600 1080
sleep 1
adb exec-out screencap -p > "$OUT/03-target-concept.png"

# Open score tab in the rounded bottom navigation.
adb shell input tap 690 2260
sleep 2
adb exec-out screencap -p > "$OUT/04-score-concept.png"

printf 'V1.1 concept UI screenshots captured:\n'
ls -lh "$OUT"/*.png
