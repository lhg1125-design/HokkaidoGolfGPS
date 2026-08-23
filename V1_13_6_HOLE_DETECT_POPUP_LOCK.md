# V1.13.6 HOLE DETECT POPUP LOCK

Status: **PASS FLOW / STORYBOOK POPUP LOCK**  
Target: `release/v1.13.6-approved-ui-hotfix`  
Runtime patch: `.github/scripts/patch-v1136-hole-confirm-popup.py`

## Purpose

Automatic hole detection is an assist, never an unconditional hole switch. The user must visually verify the detected candidate against the actual hole before the active yardage changes.

## Flow

`finish-zone detection -> candidate popup -> inspect mini yardage -> optional left/right correction -> 이 홀로 이동 -> save hole -> full yardage changes`

- Detection itself does not modify `hole`.
- Popup left/right arrows modify only the candidate preview.
- `이 홀로 이동` is the only action that commits the candidate.
- `현재 홀 유지` and close keep the current hole unchanged.

## Visual language

- Overlay on top of the existing PASS course screen.
- Translucent dark-green dim layer behind the popup.
- Large rounded cream card with soft green outline/shadow.
- Pale-sky storybook header.
- Small golf mascot and short confirmation copy.
- Avoid technical/debug language.

Header copy:

- `다음 홀을 찾았어요!`
- `미니맵을 보고 실제 홀과 맞는지 확인해주세요`

## Left pane — real candidate yardage

- Use the exact packaged yardage resource of the current candidate.
- Fit-center, no crop, no stretch.
- Overlay only the **numeric hole number**; do not bake text into the yardage source.
- Previous/next circular arrow buttons sit around the mini-map.
- Arrow press changes candidate only and refreshes mini-map/PAR/TOTAL/strategy together.

## Right pane — quick identification

Show:

- `PAR n`
- official `TOTAL m`
- `공략 한 줄`
- short hole-specific strategy when available
- if no specific strategy exists, show the existing safe generic strategy note

Strategy text is identification/support information only; it must not change the detected hole automatically.

## Buttons

Primary:

- Green `이 홀로 이동`
- On tap: save candidate to active `hole`, reset current navigation marker state as needed, persist state, redraw the full PASS yardage for that hole.

Secondary:

- Neutral `현재 홀 유지`
- Hide popup and keep current hole.

Close `×` behaves like `현재 홀 유지`.

## Auto-detection trigger

For first-and-only course play:

- Current hole requires TEE calibration.
- When live remaining distance reaches approximately the final 25-45 m zone, arm the exit detector.
- After at least approximately 12 seconds and approximately 40 m departure from that end-zone point, propose the next sequential hole.
- Do not auto-commit.
- The candidate may be corrected manually with popup arrows.

## QA

Popup is not PASS unless:

- actual active hole remains unchanged when popup first appears,
- actual packaged candidate mini-map is shown,
- numeric hole overlay is separate from the image,
- arrow changes candidate preview without changing active hole,
- PAR/TOTAL/strategy update with candidate,
- `이 홀로 이동` commits and immediately displays the destination yardage,
- dismiss keeps current hole,
- underlying PASS UI remains unchanged.
