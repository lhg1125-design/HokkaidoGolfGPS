# VWID AC Collector

Standalone, read-only APK collector for the user's Ownice Android head unit. It is a separate application (`com.vwid.accollector`) and does not replace or modify the HVAC Bridge, Total Launcher, or their widget providers.

## On the head unit
1. Install `VWID_AC_COLLECTOR_1_0.apk` using the existing file manager. No PC, ADB, root or network connection is required to run it.
2. Open **VWID AC Collector**. It automatically checks `com.tw.ac` and `com.zht.car.accontroller` and lists additional package-name candidates.
3. Tap **ZIP 생성 · 다운로드 저장**. On Android 10 the archive is written to `Downloads/VWID_HVAC/` through MediaStore. The alternative save button uses the system document picker, including a USB drive if available.
4. Tap **저장한 ZIP 공유**, or use the file manager to share the ZIP. Upload it to the conversation for static analysis.

The archive contains only the two named target packages' installed APK files (including splits), component metadata, candidate package names, and a JSON report. If a package is absent or its APK cannot be read, the report records that fact. It never substitutes an unrelated APK. A missing package may require further investigation of the actual installed firmware.

The app has no MCU/CAN commands, TWUtil calls, boot receiver, widget provider, root/shell commands, internet permission, broad storage permission, or background service. It does not read application-private data or automatically upload anything. No vehicle control capability is claimed or tested. The existing HVAC control UI remains unchanged.

## Build
`gradle :app:assembleDebug` from this directory, using JDK 17, Gradle 8.9 and Android SDK 35. The dedicated GitHub Actions workflow produces a debug-signed APK. Build success does not establish that an OEM-protected APK can be read on the actual head unit.
