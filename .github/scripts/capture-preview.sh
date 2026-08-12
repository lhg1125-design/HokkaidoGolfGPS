#!/usr/bin/env bash
set -euo pipefail

APK="HokkaidoGolfGPS-v0.8-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV08Activity"
OUT="preview"

mkdir -p "$OUT"
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put global hide_error_dialogs 1 || true
adb shell settings put global show_first_crash_dialog 0 || true
adb shell am force-stop com.google.android.apps.nexuslauncher || true
adb shell am force-stop com.android.launcher3 || true

# Emulator location near Kamishihoro. preview=true provides clearly labeled demo TEE/GREEN refs only for screenshot validation.
adb emu geo fix 143.2283621 43.2570513 || true
adb shell am force-stop "$PKG" || true
adb shell am start -n "$ACTIVITY" --ez preview true
sleep 4
adb emu geo fix 143.2283621 43.2570513 || true
sleep 2
adb shell am broadcast -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true
adb exec-out screencap -p > "$OUT/01-home.png"

# Start round from preselected Kamishihoro / Champions.
adb shell input tap 300 1715
sleep 1
adb shell input tap 540 2020
sleep 4
adb exec-out screencap -p > "$OUT/02-round.png"

# Tap the schematic once so the attack-distance bubble is visible in the second round state.
adb shell input tap 600 1100
sleep 1
adb exec-out screencap -p > "$OUT/03-target.png"

# Open score tab.
adb shell input tap 690 2240
sleep 2
adb exec-out screencap -p > "$OUT/04-score.png"

printf 'V0.8 preview screenshots captured:\n'
ls -lh "$OUT"/*.png
