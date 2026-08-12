#!/usr/bin/env bash
set -euo pipefail

APK="HokkaidoGolfGPS-v1.3-debug.apk"
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

adb emu geo fix 143.2283600 43.2585100 || true
adb shell am force-stop "$PKG" || true
adb shell am start -n "$ACTIVITY" --ez preview true
sleep 4
adb emu geo fix 143.2283600 43.2585100 || true
sleep 2
adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true
adb exec-out screencap -p > "$OUT/01-home-artwork.png"

adb shell input tap 540 1840
sleep 4
adb exec-out screencap -p > "$OUT/02-course-artwork.png"

adb shell input tap 610 1160
sleep 2
adb exec-out screencap -p > "$OUT/03-target-artwork.png"

adb shell input tap 670 2290
sleep 2
adb exec-out screencap -p > "$OUT/04-scorecard-xl.png"

printf 'V1.3 scorecard XL + round summary screenshots captured:\n'
ls -lh "$OUT"/*.png
