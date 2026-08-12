# 北海道ゴルフ GPSキャディ

Hokkaido golf trip GPS caddie prototype for 2026-08-24~26.

## V0.4 Field Prototype

- Distance unit: **m only**
- Android Studio not required
- APK builds automatically with GitHub Actions
- Rounded Korean UI + playful animated golf-ball mascot / GPS pulse
- Live Android GPS accuracy and nearest-course detection
- External map-app linkage for the selected golf course
- Official REGULAR-tee hole distances converted from yards to meters
- 4-player stroke / putt score input and 18-hole scorecard

### Target courses

- 上士幌ゴルフ場 — CHAMPIONS / MASTERS
- 富良野ゴルフコース — PALMER / KING
- サホロカントリークラブ — OUT / IN

### Important field-data status

The three **course-center coordinates are verified**, but individual green Front / Center / Back GPS coordinates are still pending. V0.4 therefore must not be treated as a laser/GPS rangefinder replacement for shot decisions yet. The next field sprint adds hole-level target coordinates and target-distance logic.
