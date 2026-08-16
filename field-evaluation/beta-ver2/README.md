# beta ver2 — Field GPS Test Backup

Purpose: preserve the tested APK/source state and field GPS data before the final Dogo CC build removes Naepo/Royal Links maps from the production menu.

## Tested baseline
- Round-log engine/version observed in field logs: `1.13.6-round-log`
- Round-log source lineage commit: `620b69b3d46593df8b14235baad8b9999c0967c3` (`fix: export round log as text`)
- Visual/course-map snapshot branch base: `1ad174b2515e227cc3b062cb973ff28a03e094fe`
- This branch is the archive point named `beta-ver2`.

## Field tests preserved
1. Naepo CC — 1st GPS field test
   - source log: `HokkaidoGolfGPS-round-20260813-172102.txt`
   - archived: `naepo-round-20260813-172102.txt.gz.b64`
   - raw SHA-256: `6672bf05b62318c386bce02252f1923d6a24f1fa74588231f2aa6732928b4863`

2. Royal Links CC — 2nd GPS field test
   - source log: `HokkaidoGolfGPS-round-20260816-120035.txt`
   - archived: `royallinks-round-20260816-120035.txt.gz.b64`
   - raw SHA-256: `5b96cd14d98dc32886111f8cfb9909a0ea3341b2d0cd4cc6c1d5ac781999eeed`

## Recovery
The `.gz.b64` files are gzip-compressed original text logs encoded as Base64. Decode Base64, then gunzip to restore the exact round-log text.

## Final-build policy after this archive
- Naepo CC map: remove from final production menu, keep evaluation data here.
- Royal Links map: remove from final production menu, keep evaluation data here.
- Keep the three Japan courses.
- Add Dogo CC only after its hole images are visually approved against the locked master design.
- Do not build the final APK before Dogo image approval.
