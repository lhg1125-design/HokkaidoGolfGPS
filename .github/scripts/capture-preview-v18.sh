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

shot(){
  local course="$1" variant="$2" hole="$3" screen="$4" file="$5"
  adb shell am force-stop "$PKG" || true
  adb shell am start -n "$ACTIVITY" --ez preview true --ei previewCourse "$course" --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen "$screen" >/dev/null
  sleep 4
  adb exec-out screencap -p > "$OUT/$file"
}

shot 3 0 1 0 "01-home-premium.png"
shot 0 0 11 1 "02-kamishihoro-premium.png"
shot 1 0 4  1 "03-furano-premium.png"
shot 2 0 1  1 "04-sahoro-premium.png"
shot 3 0 1  1 "05-naepo-premium.png"
shot 4 0 1  1 "06-royallinks-queens-premium.png"
shot 4 1 12 1 "07-royallinks-kings-premium.png"

printf 'V1.8 premium screenshots:\n'
ls -lh "$OUT"/*.png
