# V1.13.6 FIELD GPS BEHAVIOR LOCK

Status: **FIELD BEHAVIOR LOCKED**  
Target: `release/v1.13.6-approved-ui-hotfix`  
Companion to: `V1_13_6_APPROVED_UI_LOCK.md`

## 1. TOTAL vs DIST

`TOTAL` and `DIST` must never mean the same thing.

- `TOTAL` = official full-hole length for the selected course / variant / hole.
- `DIST` = live remaining distance for the player.

DIST operates in two stages:

### Stage A — TEE calibrated, GREEN CENTER not yet calibrated

As soon as TEE calibration is stored and GPS is usable:

`DIST = TOTAL - distance(saved TEE anchor, current GPS)`

Rules:

- Clamp the result to `0 ... TOTAL`.
- If there is no usable GPS or no TEE anchor, display `--`.
- Do not copy TOTAL into DIST as a placeholder.
- This mode is intended to be useful immediately after tee-off, before reaching the green.

### Stage B — GREEN CENTER calibrated

When a saved GREEN CENTER exists:

`DIST = distance(current GPS, saved GREEN CENTER)`

This is the preferred accurate remaining-distance mode and overrides the Stage-A estimate.

## 2. Circular live player marker

The approved PASS UI must preserve the proven V1.13.5/V1.13.6 live field marker.

- TEE calibration alone is enough to start the circular player marker when official hole length is known.
- The marker uses current GPS and the TEE-based progress estimate before GREEN CENTER is known.
- When GREEN CENTER is available, the same marker automatically upgrades to the full TEE -> GREEN geographic projection / dogleg-aware 2D mode.
- Keep the white ring, center marker and GPS-accuracy halo behavior.
- Do not remove the marker when applying visual UI patches.

## 3. Calibration reuse — do not force calibration every round

Calibration references are stored per course / variant / hole in persistent app preferences.

### GREEN CENTER

- GREEN CENTER is a stable course reference.
- Normally calibrate it once per hole.
- Reuse it on later rounds.
- Recalibrate only if the original capture was poor or the reference needs correction.

### TEE

- Saved TEE references are reused for automatic hole recognition and field navigation.
- They do not have to be captured on every app launch or every round.
- However, the physical teeing area can move from day to day, so a fresh TEE calibration at the start of a hole is recommended when the tee position has materially shifted or maximum Stage-A DIST accuracy is desired.
- A fresh TEE calibration replaces/updates that hole's current stored TEE anchor.

Calibration data survives normal app restarts. Clearing app data or uninstalling the app removes local calibration data unless a separate backup/restore mechanism is used.

## 4. Automatic hole recognition

Automatic hole recognition applies to Japan courses as well as the other supported courses.

Current behavior:

- Uses saved TEE references for the selected course / variant.
- Requires multiple learned TEE references before automatic switching is considered reliable.
- Selects the nearest saved TEE to the current GPS position.
- Switches when the player is within the field threshold of that saved TEE.
- Includes a cooldown to prevent rapid hole bouncing.

The V1.13.x implementation currently uses at least 3 saved TEE references, an approximately 80 m nearest-TEE threshold and an approximately 45 s switching cooldown.

Do not make automatic hole switching dependent on GREEN CENTER calibration.

## 5. Recommended field workflow

### First learning round

For each hole:

1. Enter/confirm the current hole.
2. At the teeing area, perform `TEE 저장`.
3. Circular player marker starts immediately.
4. `DIST` starts as `TOTAL - travelled-from-TEE`.
5. Play the hole normally.
6. At GREEN CENTER, perform `GREEN CENTER` calibration once when practical.
7. From that point, `DIST` switches to actual current-GPS -> GREEN CENTER distance.

GREEN CENTER calibration is not required before the player can use DIST on the hole.

### Later rounds

- Reuse saved GREEN CENTER data automatically.
- Reuse saved TEE data for auto-hole recognition.
- If today's tee position is close to the stored tee, no mandatory recalibration is required.
- If today's tee box moved noticeably, tap `TEE 저장` once to refresh the anchor.
- With saved GREEN CENTER, DIST can immediately use true remaining distance as soon as the correct hole is active and GPS is usable.

## 6. GPS quality rules

Use the existing V1.13.5/V1.13.6 multi-fix capture engine.

- Do not save a weak single GPS point blindly.
- Use recent stable fixes and spread checks before accepting TEE/GREEN calibration.
- Preserve current accuracy / stale-fix safety logic.
- Preserve Round Log events for `TEE_SAVE` and `GREEN_CENTER_SAVE`.

## 7. QA gate

A field APK is not PASS unless:

- TEE-only calibration starts the circular live marker.
- TEE-only mode produces decreasing DIST as the player advances from the tee.
- DIST never defaults to TOTAL when calibration/GPS is unavailable.
- Saving GREEN CENTER switches DIST to true current-to-green-center distance.
- Saved GREEN CENTER is reusable on a later round without mandatory recalibration.
- Saved TEE anchors participate in automatic hole recognition on Japan courses.
- Hole switching does not require GREEN CENTER references.
- PASS UI layout remains unchanged.

**This document locks the operational GPS behavior; the visual geometry remains controlled by `V1_13_6_APPROVED_UI_LOCK.md`.**
