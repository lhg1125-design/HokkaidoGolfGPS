# V1.13.6 FIELD GPS BEHAVIOR LOCK

Status: **ONE-SHOT FIELD BEHAVIOR LOCKED / PREBUILD REVIEWED**  
Target: `release/v1.13.6-approved-ui-hotfix`  
Companion to: `V1_13_6_APPROVED_UI_LOCK.md`

## 1. Operating assumption

Each golf course is played **once** on this trip.

Therefore the app must be useful during that single round and must not depend on building calibration data for a later second round.

Primary field action per hole:

`GPS GOOD -> TEE 저장 -> stable CAL -> circular live marker -> live DIST -> play hole -> auto-detect candidate -> user confirm -> next-hole yardage -> next TEE CAL`

`GREEN CENTER` is optional. It is not a mandatory learning step.

---

## 2. CAL method — actual implementation

TEE and optional GREEN CENTER use the V1.13.5/V1.13.6 stable multi-fix capture path.

For the Japan courses:

- Android native `GPS_PROVIDER` is used.
- Recent GPS fixes are collected continuously, up to the existing short rolling buffer.
- A capture uses recent fixes rather than trusting one weak point blindly.
- Normal Japan capture tolerance uses the production multi-fix rule (18 m capture window).
- If the current accuracy is worse than approximately 12 m, at least three recent agreeing fixes are required.
- If recent fixes spread by more than approximately 12 m, capture is rejected and the user retries after GPS settles.
- The save action uses a confirmation window: first tap asks for one more tap at the same physical point; the second tap completes the save.

### TEE CAL

At the physical teeing area:

1. Wait for usable GPS / GOOD condition.
2. Tap `TEE 저장`.
3. When the confirmation message appears, tap `TEE 저장` once more while remaining at the same tee position.
4. The stable weighted GPS reference is persisted for the current hole.
5. The circular player marker and DIST become active immediately.

TEE CAL is the only required per-hole calibration action.

### GREEN CENTER CAL — optional

At/near green center, if convenient:

1. Tap `GREEN CENTER`.
2. Confirm with the second tap using the same stable GPS capture path.
3. The current hole immediately upgrades from TEE-only estimation to true GPS-to-GREEN CENTER distance / full TEE-to-GREEN projection.

Do **not** interrupt play just to perform GREEN CAL. It is optional.

---

## 3. TOTAL vs DIST

- `TOTAL` = official full-hole distance for the selected course / variant / hole.
- `DIST` = live remaining distance for the player.

### Normal one-shot mode — TEE only

Immediately after `TEE 저장` and while GPS is usable:

`DIST = TOTAL - straight-line displacement(saved TEE, current GPS)`

Clamp to `0 ... TOTAL`.

This is an **estimated remaining distance** before GREEN CENTER exists. On a strong dogleg it is not the same as measured path length along the fairway.

If there is no usable GPS or no TEE anchor, show `--`. Never duplicate TOTAL into DIST as a placeholder.

### Optional GREEN CENTER mode

If GREEN CENTER has been saved:

`DIST = straight-line distance(current GPS, saved GREEN CENTER)`

This becomes the preferred approach distance and overrides the TEE-only estimate.

---

## 4. Circular live player marker — actual display rule

The PASS UI must show the proven V1.13.5/V1.13.6 circular live marker immediately after TEE calibration when GPS is usable.

Marker visual:

- orange center dot,
- white circular ring,
- larger GPS-accuracy halo,
- halo quality color derived from the current Android Location accuracy,
- smoothed movement to reduce visual jitter.

Mapping behavior:

- **TEE only:** progress uses TEE + official hole length and follows the extracted visual hole centerline.
- **TEE + GREEN CENTER:** progress upgrades to geographic TEE->GREEN projection; lateral/cross-track information may also be used where the live geo engine supports it.
- A GREEN reference is not required for the marker to start.
- A TEE reference **is** required for the current hole marker.

After confirming a move to the next hole, the next-hole player marker starts after that hole's TEE CAL. The previous hole's GREEN must never be falsely projected onto the new hole yardage.

---

## 5. GPS status display

The top-right GPS UI is tied to live Android Location data.

- `GPS GOOD / WAIT` is based on the existing usable/stale-fix safety policy.
- Signal bars are derived from `Location.getAccuracy()`:
  - approximately <=5 m: 4 bars
  - <=8 m: 3 bars
  - <=12 m: 2 bars
  - worse: 1 bar
- Navigation and marker drawing also pass through the existing `navGpsUsableV1133()` quality/stale-fix gate.
- A stale or unusable fix must not be presented as a trustworthy live player position.

The GPS card is therefore a **quality/status display**, not a fabricated signal indicator.

---

## 6. Weather / wind display

Weather is not hardcoded.

- The latest actual device GPS latitude/longitude triggers the weather query.
- Provider: Open-Meteo current weather endpoint.
- Displayed runtime values:
  - temperature,
  - weather condition,
  - 10 m wind speed in m/s,
  - 10 m wind direction.
- Refresh: approximately every 10 minutes or after about 1 km movement.
- Network/API failure: retain the last valid value or show `--`; never substitute demonstration weather.

Weather network status and GPS positioning are independent: GPS can remain live even when weather data cannot refresh.

---

## 7. GREEN CENTER role — optional transition reference, not GPS sensor correction

GREEN CENTER has two useful same-round effects when the player chooses to save it:

1. **Approach accuracy:** DIST becomes actual current-GPS -> saved GREEN CENTER distance.
2. **Next-hole transition confidence:** the auto-hole detector calls the same remaining-distance engine. Therefore, when GREEN CENTER exists, the final 25-45 m finish-zone is referenced to the real saved green position instead of only the TEE/TOTAL estimate. This makes the timing of the next-hole candidate popup more trustworthy.

Important technical distinction:

- GREEN CENTER does **not** improve the raw Android GPS accuracy number itself.
- GREEN CENTER does **not** replace the next hole's TEE CAL.
- GREEN CENTER does **not** get drawn as a false reference point on the next-hole mini-map.
- It is an optional geometric/transition reference for the current-hole finish and next-hole detection sequence.

So the field rule is:

`TEE CAL = required`  
`GREEN CENTER CAL = optional accuracy/transition upgrade`

---

## 8. Automatic hole detection — detect, ask, then switch

Automatic detection must **never silently change the active hole**.

For the one-time Japan round:

1. Current hole must have a TEE calibration.
2. App watches live `DIST`.
3. With no GREEN CAL, DIST uses the TEE/TOTAL estimate.
4. With GREEN CAL, DIST and finish-zone detection use true GPS -> GREEN CENTER range.
5. When remaining distance enters approximately the final 25-45 m zone, the exit detector is armed.
6. The player must remain in the sequence for at least about 12 seconds and then move approximately 40 m away from the armed finish point.
7. The app **proposes** the next sequential hole; it does not commit it.
8. A storybook confirmation popup appears.
9. The popup shows the candidate's exact packaged yardage mini-map, overlaid hole number, large PAR / TOTAL, bold strategy and speaker/TTS control.
10. If wrong, the user changes the candidate with popup left/right arrows.
11. Only `이 홀로 이동` saves the candidate as active `hole` and opens that full yardage.
12. `현재 홀 유지` / close leaves the current hole unchanged.
13. Permanent main-screen previous/next arrows remain as manual fallback.

This flow applies to all supported Japan courses.

---

## 9. Hole-detect popup visual lock

- Overlay on top of the existing PASS course screen.
- Actual packaged candidate yardage only; never screenshot crop.
- Fit-center / no crop / no stretch.
- Numeric hole number is a separate overlay.
- PAR and official distance are large bold outdoor-readable values.
- Strategy heading/body are bold.
- Speaker icon reads hole number + PAR + distance + strategy through Android TTS when available.
- Cute storybook/initial-screen mascot family may decorate the background, but readable panes stay opaque and the mini-yardage remains clean.
- Bottom button labels are enlarged bold.

---

## 10. Per-hole field workflow

1. Confirm displayed hole / yardage.
2. Wait for usable GPS.
3. At tee, complete the two-tap stable `TEE 저장` CAL.
4. Confirm circular marker appears.
5. Confirm `DIST` starts and updates as GPS position changes.
6. Play normally.
7. GREEN CENTER may be saved if convenient; it is not required.
8. Near hole completion, wait for the automatic candidate popup.
9. Compare the actual mini yardage with the physical next hole.
10. Correct candidate with popup arrows if necessary.
11. Tap `이 홀로 이동`.
12. At the next tee, perform that hole's TEE CAL and continue.

---

## 11. Prebuild QA gate

The build must stop before Gradle compilation unless all of these are present in the generated final source:

- native GPS provider path,
- stable multi-fix CAL capture and spread checks,
- TEE-first DIST path,
- GREEN true-range upgrade path,
- TEE-first circular player marker,
- GPS accuracy halo,
- live GPS quality bars,
- realtime weather/wind from GPS coordinates,
- one-shot auto-hole detector,
- no silent hole change,
- confirmation popup,
- exact packaged mini-yardage,
- optional GREEN transition reference,
- single final cute/TTS popup implementation with no duplicate TTS field declarations.

Automated checker:

`.github/scripts/check-v1136-field-prebuild.py`

**This document is the source of truth for the one-time Japan field operation. No second-round learning workflow is required.**
