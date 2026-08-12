#!/usr/bin/env bash
set -euo pipefail

APK="HokkaidoGolfGPS-v0.6-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.MainActivity"
OUT="preview"

mkdir -p "$OUT"

adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true

# Launch at Kamishihoro course center. adb emu geo fix expects longitude latitude.
adb emu geo fix 143.2283621 43.2570513 || true
adb shell am force-stop "$PKG" || true
adb shell am start -n "$ACTIVITY"
sleep 4
adb emu geo fix 143.2283621 43.2570513 || true
sleep 2

adb exec-out screencap -p > "$OUT/01-home.png"

# Pixel 6 emulator is 1080 x 2400. Select first course and start round.
adb shell input tap 540 820
sleep 1
adb shell input tap 300 1715
sleep 1
adb shell input tap 540 2020
sleep 3
adb exec-out screencap -p > "$OUT/02-round.png"

# Open score tab.
adb shell input tap 690 2240
sleep 2
adb exec-out screencap -p > "$OUT/03-score.png"

printf 'Preview screenshots captured:\n'
ls -lh "$OUT"/*.png
