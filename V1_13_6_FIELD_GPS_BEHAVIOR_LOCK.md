# V1.13.6 FIELD GPS BEHAVIOR LOCK

Status: **ONE-SHOT FIELD BEHAVIOR LOCKED**  
Target: `release/v1.13.6-approved-ui-hotfix`  
Companion to: `V1_13_6_APPROVED_UI_LOCK.md`

## 1. Operating assumption

Each golf course is played **once** on this trip.

Therefore the app must be useful during that single round and must not depend on building calibration data for a later second round.

Primary field action per hole:

`TEE 저장 -> circular live marker -> live DIST -> play hole -> auto-detect candidate -> user confirm -> next-hole yardage`

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

## 5. Japan automatic hole detection — confirm before switching

Automatic detection must **never silently change the active hole**.

For the Japan trip, the detector works as a conservative same-round sequential candidate detector:

1. Current hole must have a TEE calibration.
2. App watches the current hole's live DIST.
3. When estimated DIST enters the final approximately 25-45 m zone, the hole-exit detector is armed.
4. The app does not propose a new hole while the player is still around the green.
5. After at least about 12 seconds and approximately 40 m of movement away from the armed end-zone point, the app proposes the next sequential hole as the candidate.
6. A storybook confirmation popup appears. The current hole is still unchanged at this point.
7. Popup shows the candidate's **actual packaged yardage mini-map**, large overlaid hole number, PAR / TOTAL and a one-line strategy note.
8. If the candidate is wrong, the user changes the candidate with left/right arrows inside the popup.
9. Only when the user taps `이 홀로 이동` is the active `hole` state saved and the full PASS yardage screen changed to that hole.
10. `현재 홀 유지` or the close button dismisses the popup and keeps the current hole.

This behavior applies to all supported Japan courses. GREEN CENTER is not required for detection or switching.

The permanent previous/next hole arrows on the PASS course screen remain available as a manual fallback.

## 6. Hole-detect popup visual lock

Popup visual language follows the approved Golf-Anime / storybook direction.

- Dim the existing PASS UI with a translucent overlay; never replace the underlying screen.
- Large cream rounded card with soft green outline.
- Pale sky header, small mascot and short phrase: `다음 홀을 찾았어요!`.
- Left pane: actual candidate yardage mini-map, fit-center/no crop.
- Overlay **only the numeric hole number** on the mini-map; do not bake the number into the source image.
- Left/right circular arrows change only the candidate preview, not the live active hole.
- Right pane: `PAR`, official metres, `공략 한 줄`, and a short confirmation tip.
- Primary button: green `이 홀로 이동`.
- Secondary button: neutral `현재 홀 유지`.
- On primary confirmation, save the candidate as active hole and immediately display that full-hole yardage.

The popup must use the exact same packaged yardage resource as the destination course screen so the golfer can visually compare the mini-map with the real hole before committing.

## 7. Per-hole field workflow

For every hole:

1. Confirm the displayed hole.
2. At the teeing area tap `TEE 저장` and complete the existing stable-GPS capture.
3. Circular player marker appears immediately.
4. `DIST` begins from TOTAL and decreases with GPS movement.
5. Play the hole normally.
6. Do not stop play just to calibrate GREEN CENTER.
7. Near completion, the app detects a likely transition and shows the candidate confirmation popup.
8. Compare the actual mini yardage with the real course. If wrong, change candidate with popup arrows.
9. Tap `이 홀로 이동`; only then the app saves the new hole and opens that full yardage screen.
10. At the next tee, perform `TEE 저장` and continue.

## 8. GPS quality

Keep the existing V1.13.5/V1.13.6 multi-fix capture rules.

- Do not accept a weak single point blindly.
- Preserve recent-fix and spread checks.
- Preserve stale-fix safety logic.
- Preserve `TEE_SAVE` and optional `GREEN_CENTER_SAVE` Round Log events.

## 9. QA gate

A field APK is not PASS unless all of these are true:

- TEE calibration alone starts the circular live marker.
- TEE calibration alone starts DIST.
- DIST decreases from TOTAL as the player moves away from the TEE.
- Missing TEE/GPS shows `--`, not a copied TOTAL value.
- GREEN CENTER is optional, not required by the normal hole flow.
- Auto detection opens a confirmation popup and does not silently change holes.
- Candidate mini-map uses the actual packaged yardage for that candidate hole.
- Popup arrows change only the candidate preview.
- `이 홀로 이동` commits the candidate and immediately opens that hole's yardage.
- `현재 홀 유지` leaves the active hole unchanged.
- Manual previous/next hole arrows remain functional.
- PASS UI geometry remains unchanged behind the overlay.

**This document is the source of truth for the one-time Japan field operation. No second-round learning workflow is required.**
