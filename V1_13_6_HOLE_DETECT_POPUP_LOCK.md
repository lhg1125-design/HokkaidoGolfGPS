# V1.13.6 HOLE DETECT POPUP LOCK

Status: **PASS FLOW / STORYBOOK POPUP LOCK**  
Target: `release/v1.13.6-approved-ui-hotfix`  
Runtime patches:
- `.github/scripts/patch-v1136-hole-confirm-popup.py`
- `.github/scripts/patch-v1136-hole-confirm-polish.py`

## Purpose

Automatic hole detection is an assist, never an unconditional hole switch. The user must visually verify the detected candidate against the actual hole before the active yardage changes.

## Flow

`finish-zone detection -> candidate popup -> inspect real mini yardage -> optional left/right correction -> 이 홀로 이동 -> save hole -> full yardage changes`

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
- `코스 모양을 보고 맞는지 확인해주세요`

## Left pane — real candidate yardage

**The mini-map must use the exact packaged yardage resource for the candidate hole.**

- Never crop a screenshot of the main UI for this mini-map.
- Never include ruler text, buttons, previous-hole remnants, or any UI garbage in the mini-map.
- Load the same `fullHoleBitmapV1102()` resource that the full PASS yardage screen uses, temporarily bound to the candidate hole.
- Fit-center, no crop, no stretch.
- Overlay only the **numeric hole number**; do not bake text into the yardage source.
- Previous/next circular arrow buttons sit around the mini-map.
- Arrow press changes candidate only and refreshes mini-map/PAR/TOTAL/strategy together.

## Right pane — field readability

Show:

- `PAR n`
- official `TOTAL m`
- `공략법`
- short hole-specific strategy when available
- speaker button for TTS read-aloud

Typography is FIELD LOCKED:

- PAR and official distance use approximately **2x the previous popup font size**, bold, preferably in separate high-contrast chips.
- Strategy heading is bold and enlarged.
- Strategy body is bold and enlarged for outdoor readability.
- Do not reduce these sizes merely to fit a long sentence; wrap strategy text instead.

If no hole-specific strategy exists, show the existing safe generic strategy note.

## Speaker / read-aloud

- Show a clear speaker icon next to `공략법`.
- Tap reads the current candidate's `hole number + PAR + official distance + strategy`.
- Use Android `TextToSpeech` with Korean locale.
- TTS must not require network connectivity when the device has an offline Korean voice installed.
- If Korean TTS data is missing/not supported, keep the popup usable and show a short toast instead of failing.
- When candidate changes with left/right arrows, stop any speech for the previous candidate.

## Buttons

Primary:

- Green `이 홀로 이동`
- Popup button label is **50% larger than the former popup label and bold**.
- On tap: save candidate to active `hole`, reset current navigation marker state as needed, persist state, redraw the full PASS yardage for that hole.

Secondary:

- Neutral `현재 홀 유지`
- Same enlarged bold button typography.
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
- exact packaged candidate mini-map is shown with no screenshot/UI garbage,
- numeric hole overlay is separate from the image,
- arrow changes candidate preview without changing active hole,
- PAR/TOTAL/strategy update with candidate,
- PAR and distance are approximately 2x previous popup font size and bold,
- strategy heading/body are bold and readable outdoors,
- speaker icon reads the current candidate information through Android TTS when available,
- popup button labels are 50% larger and bold,
- `이 홀로 이동` commits and immediately displays the destination yardage,
- dismiss keeps current hole,
- underlying PASS UI remains unchanged.
