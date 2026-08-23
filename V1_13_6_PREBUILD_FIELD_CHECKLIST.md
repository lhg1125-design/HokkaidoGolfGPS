# V1.13.6 PREBUILD FIELD CHECKLIST

Status: **CODE REVIEW COMPLETE / BUILD NOT YET USED AS PASS EVIDENCE**  
Branch: `release/v1.13.6-approved-ui-hotfix`

## Legend

- **CODE PASS**: required implementation is present in the patch/build chain.
- **PREBUILD GATE**: automatically checked against the fully generated Java source immediately before Gradle compilation.
- **APK GATE**: checked after APK compilation/package creation.
- **FIELD CHECK**: must be confirmed outdoors with real GPS.

| Item | Code status | Build gate | Field verification |
|---|---|---|---|
| Android native GPS_PROVIDER | CODE PASS | PREBUILD GATE | FIELD CHECK |
| Stable multi-fix TEE CAL | CODE PASS | PREBUILD GATE | FIELD CHECK |
| Two-tap CAL confirmation | CODE PASS | PREBUILD GATE | FIELD CHECK |
| TEE-only DIST start | CODE PASS | PREBUILD GATE | FIELD CHECK |
| Circular player marker after TEE CAL | CODE PASS | PREBUILD GATE | FIELD CHECK |
| Accuracy halo / marker smoothing | CODE PASS | PREBUILD GATE | FIELD CHECK |
| GREEN CENTER optional save | CODE PASS | PREBUILD GATE | FIELD CHECK |
| GREEN true remaining-distance upgrade | CODE PASS | PREBUILD GATE | FIELD CHECK |
| GREEN-assisted finish-zone / next-hole detection confidence | CODE PASS | PREBUILD GATE | FIELD CHECK |
| GREEN does not replace next-hole TEE CAL | CODE PASS | PREBUILD GATE | FIELD CHECK |
| GPS bars from Location.getAccuracy() | CODE PASS | PREBUILD GATE | FIELD CHECK |
| GPS GOOD/WAIT quality/stale gate | CODE PASS | PREBUILD GATE | FIELD CHECK |
| Realtime weather from current GPS coordinate | CODE PASS | PREBUILD GATE + APK GATE | FIELD CHECK |
| Realtime wind speed/direction | CODE PASS | PREBUILD GATE + APK GATE | FIELD CHECK |
| Auto hole detects candidate only | CODE PASS | PREBUILD GATE | FIELD CHECK |
| No silent automatic hole commit | CODE PASS | PREBUILD GATE | FIELD CHECK |
| Storybook confirmation popup | CODE PASS | PREBUILD GATE | FIELD CHECK |
| Candidate real packaged yardage mini-map | CODE PASS | PREBUILD GATE + APK ASSET GATE | FIELD CHECK |
| Candidate left/right correction | CODE PASS | PREBUILD GATE | FIELD CHECK |
| User confirmation commits hole | CODE PASS | PREBUILD GATE | FIELD CHECK |
| Cute character wallpaper | CODE PASS | PREBUILD GATE | VISUAL CHECK |
| Large bold PAR / distance / strategy | CODE PASS | PREBUILD GATE | VISUAL CHECK |
| TTS speaker readout | CODE PASS | PREBUILD GATE | DEVICE TTS CHECK |
| Single TTS implementation / no duplicate declarations | FIXED | PREBUILD GATE | COMPILE CHECK |
| 135 packaged yardage assets | existing build chain | APK GATE | VISUAL SAMPLE CHECK |

## CAL operation to verify on course

### TEE

1. Wait for GPS to settle.
2. Tap `TEE 저장` once.
3. Keep the device at the tee and tap again when prompted.
4. Verify save confirmation.
5. Verify circular marker appears.
6. Verify DIST starts from the TEE-only remaining-distance mode.

### GREEN CENTER — optional

1. Save only when convenient.
2. Two-tap stable CAL is used.
3. Verify DIST switches to actual current GPS -> GREEN CENTER distance.
4. Verify the final-hole zone / next-hole candidate timing is more directly referenced to the saved green.
5. Do not require GREEN CAL to finish the round.

## Player marker display

Expected visual:

- orange center dot,
- white ring,
- accuracy halo,
- halo quality follows GPS accuracy,
- smooth movement,
- starts with TEE only,
- upgrades to TEE->GREEN geographic projection when GREEN exists.

The previous hole's GREEN is **not** used as a fake player coordinate on the next-hole yardage. The next-hole marker starts from that hole's TEE CAL.

## DIST

- Before TEE CAL / usable GPS: `--`
- TEE only: `TOTAL - straight-line displacement from saved TEE`
- GREEN saved: `current GPS -> GREEN CENTER actual straight-line distance`

## Weather / GPS card

- Weather coordinate = current device GPS coordinate.
- Weather = current Open-Meteo temperature/weather code.
- Wind = current 10 m direction + speed in m/s.
- Refresh approximately 10 minutes or 1 km movement.
- Weather failure keeps last valid value or `--`; no hardcoded demonstration values.
- GPS bars use `Location.getAccuracy()`.
- GPS GOOD/WAIT remains independent of weather network availability.

## Auto-hole transition

Expected sequence:

`current hole TEE CAL -> final 25-45 m zone -> >=12 s -> >=40 m departure -> candidate popup -> visual mini-yardage check -> optional left/right correction -> user taps 이 홀로 이동 -> destination yardage -> next TEE CAL`

GREEN CENTER, when available, improves the end-zone/transition reference because the detector uses true remaining distance to the saved green. It does **not** increase raw GNSS sensor accuracy.

## Prebuild automated checker

`.github/scripts/check-v1136-field-prebuild.py`

The workflow runs this checker **after the full V1.13.6 patch chain is generated and before Gradle compilation**. Any missing marker/DIST/GPS/weather/auto-hole/GREEN/TTS implementation stops the build.

## Final rule

Do not call an APK field-ready unless:

1. PREBUILD GATE passes.
2. Gradle compilation passes.
3. APK asset/function gates pass.
4. Outdoor GPS smoke test confirms TEE CAL -> marker -> DIST.
5. At least one real hole transition confirms candidate popup -> user confirmation -> correct destination yardage.
