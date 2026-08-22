# SAHORO H01 Runtime Overlay Resources

## asset_bg_original
- Source: user provided original background image
- Usage: overlay base only
- Rule: Never use previously composited review images as base

## Overlay Rules V1
- Yardage transparent PNG only
- JSON provides yardage values only
- FRONT/CENTER/BACK text labels remain in asset_bg
- Distance values are runtime overlay
- GPS unavailable: `--`

## Distance Logic
- STD: fixed hole data from JSON
- GPS: realtime player position to pin distance
- Master and Follower use identical pin distance calculation

## Player Legend
- Player color circle aligned on distance scale line
- Name and remaining distance box must fully contain text
- Auto Y-offset when players overlap

## Review Base
Use this asset_bg_original as the only validation reference.