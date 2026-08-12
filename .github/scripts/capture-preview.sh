#!/usr/bin/env bash
set -euo pipefail

APK="HokkaidoGolfGPS-v1.4.2-debug.apk"
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

adb shell input tap 540 1840
sleep 3
adb shell input tap 610 1160
sleep 2
adb exec-out screencap -p > "$OUT/02-course-gps-target.png"

adb shell input tap 415 2290
sleep 2
adb exec-out screencap -p > "$OUT/03-score-input.png"

adb shell input tap 670 2290
sleep 2
adb exec-out screencap -p > "$OUT/04-scorecard-xl.png"

adb shell input tap 910 2290
sleep 2
adb exec-out screencap -p > "$OUT/05-round-summary.png"

printf 'V1.4.2 calibrated GPS target + five-screen screenshots captured:\n'
ls -lh "$OUT"/*.png
