# V1.13.6 FIELD GPS BEHAVIOR LOCK

Status: **ONE-SHOT FIELD BEHAVIOR LOCKED**  
Target: `release/v1.13.6-approved-ui-hotfix`  
Companion to: `V1_13_6_APPROVED_UI_LOCK.md`

## 1. Operating assumption

Each golf course is played **once** on this trip.

Therefore the app must be useful during that single round and must not depend on building calibration data for a later second round.

Primary field action per hole:

`TEE 저장 -> circular live marker -> live DIST -> play hole -> automatic/sequential H+1 assist`

`GREEN CENTER` is optional. It is not a mandatory learning step.

## 2. TOTAL vs DIST

- `TOTAL` = official full-hole distance for the selected course / variant / hole.
- `DIST` = live estimated remaining distance for the player.

### Normal one-shot mode — TEE only

Immediately after `TEE 저장` and while GPS is usable:

`DIST = TOTAL - distance(saved TEE, current GPS)`

Clamp to `0 ... TOTAL`.

If there is no usable GPS or no TEE anchor, show `--`. Never duplicate TOTAL into DIST as a placeholder.

### Optional GREEN CENTER mode

If the player voluntarily saves GREEN CENTER:

`DIST = distance(current GPS, saved GREEN CENTER)`

This overrides the TEE-only estimate, but GREEN CENTER is not required for normal use.

## 3. Circular live player marker

The PASS UI must show the proven V1.13.5/V1.13.6 circular live marker immediately after TEE calibration.

- TEE-only operation is sufficient.
- Keep center dot, white ring and GPS-accuracy halo.
- Before GREEN CENTER exists, marker progress is based on TEE + official hole length.
- If GREEN CENTER exists, the same marker upgrades to the full geographic TEE -> GREEN projection.
- Never remove this marker when applying visual UI patches.

## 4. Calibration policy

### Required

`TEE 저장` once at the start of each hole.

Reason:

- establishes the current physical tee anchor,
- starts the circular marker,
- starts DIST,
- gives the one-shot hole-transition logic its current-hole reference.

### Optional

`GREEN CENTER`.

It may be used for verification or improved final approach distance, but the golfer must not be required to walk to the green and calibrate it for a future round.

There is no second-round learning requirement in this project.

## 5. Japan automatic hole movement — one-shot sequential assist

The old learned-TEE recognizer depended on already-saved TEE references from other holes and is not appropriate for a first-and-only visit.

For the Japan trip, hole movement is therefore changed to a conservative **same-round sequential auto-advance assist**:

1. Current hole must have a TEE calibration.
2. App watches the current hole's live DIST.
3. When estimated DIST enters the final approximately 25-45 m zone, the hole-exit detector is armed.
4. The app does not switch immediately while the player is still around the green.
5. After at least about 12 seconds and approximately 40 m of movement away from the armed end-zone point, the app advances `Hn -> Hn+1`.
6. The next hole then waits for that hole's `TEE 저장` before starting its marker/DIST.

This behavior applies to the supported Japan courses as well.

The previous/next hole arrow buttons remain available at all times as the reliable manual fallback. GREEN CENTER is not required for hole switching.

## 6. Per-hole field workflow

For every hole:

1. Confirm the displayed hole.
2. At the teeing area tap `TEE 저장` and complete the existing confirmation/stable-GPS capture.
3. Circular player marker appears immediately.
4. `DIST` begins from TOTAL and decreases with GPS movement.
5. Play the hole normally.
6. Do not stop play just to calibrate GREEN CENTER.
7. Near completion, one-shot sequential auto-advance is armed and changes to the next hole after leaving the end zone.
8. If auto-advance is not appropriate for the hole geometry, use the existing next-hole arrow.

## 7. GPS quality

Keep the existing V1.13.5/V1.13.6 multi-fix capture rules.

- Do not accept a weak single point blindly.
- Preserve recent-fix and spread checks.
- Preserve stale-fix safety logic.
- Preserve `TEE_SAVE` and optional `GREEN_CENTER_SAVE` Round Log events.

## 8. QA gate

A field APK is not PASS unless all of these are true:

- TEE calibration alone starts the circular live marker.
- TEE calibration alone starts DIST.
- DIST decreases from TOTAL as the player moves away from the TEE.
- Missing TEE/GPS shows `--`, not a copied TOTAL value.
- GREEN CENTER is optional, not required by the normal hole flow.
- If GREEN CENTER is saved, DIST changes to actual current-GPS -> GREEN CENTER distance.
- Japan courses use the one-shot sequential H+1 assist without requiring future-round learned TEE data.
- Manual previous/next hole arrows remain functional.
- PASS UI geometry remains unchanged.

**This document is the source of truth for the one-time Japan field operation. No second-round learning workflow is required.**
