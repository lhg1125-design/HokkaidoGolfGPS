# V1.13.6 APPROVED UI LOCK

Status: **PASS / LOCKED**  
Target branch: `release/v1.13.6-approved-ui-hotfix`  
Base runtime: V1.13.6 ROUND LOG / `FieldGpsV09Activity`  
Purpose: This file is the single reproduction rule for the approved V1.13.6 course UI. Future rebuilds must preserve this visual hierarchy and only bind runtime data into the locked positions.

---

## 1. Absolute rule

The approved UI is a **layout master**, not a fixed screenshot.

- Layout, spacing, card proportions, typography hierarchy, colors, bottom navigation, yardage stage position and ruler position are LOCKED.
- Course name, course variant, hole number, PAR, TOTAL, DIST, yardage image, GPS state, weather, wind direction and wind speed are runtime values.
- Never regenerate the whole course screen from a different Canvas concept.
- Never substitute another V09 / V1.17 / V1.18 layout.
- Score-input redesign is out of scope for this hotfix unless separately approved.

PASS visual hierarchy:

`Course name / Variant`  
`Realtime Weather + Wind + GPS card`  
`Prev arrow | TOTAL | DIST | PAR | Next arrow`  
`GREEN tag`  
`HOLE gold card + PAR gold card`  
`Full-hole yardage image, fit-center, no crop`  
`50 m ruler on right`  
`TEE tag + source footer`  
`GREEN CENTER | TEE 저장 | 외부 지도`  
`홈 | 코스 | 입력 | 카드 | 요약`

---

## 2. Runtime data binding

### Course header

| UI field | Runtime source | Rule |
|---|---|---|
| Korean course name | `ko[selected]` | Current selected course |
| Variant name | `variants[selected][variant]` | CHAMPIONS / MASTERS / PALMER / KING / OUT-IN etc. |
| Hole | `hole` | `H1` ... `H18` |
| PAR | `currentPar()` | Must change with current hole |
| TOTAL | `currentYards() * 0.9144` | Official hole length converted to metres |
| DIST | `distances(greenCenterRef(hole)).center` | Live GPS distance to green center when available; otherwise TOTAL fallback |

`TOTAL` and `DIST` are intentionally different concepts. TOTAL is official full-hole distance. DIST is player-to-green live distance.

### Yardage image

Use the actual current-hole resource selected by course / variant / hole.

Expected resource families:

- Kamishihoro CHAMPIONS: `yardage_kamishihoro_c01` ... `c18`
- Kamishihoro MASTERS: `yardage_kamishihoro_m01` ... `m18`
- Furano PALMER: `yardage_furano_palmer01` ... `palmer18`
- Furano KING: `yardage_furano_king01` ... `king18`
- Sahoro: `yardage_sahoro_01` ... `18`
- Other V1.13.6-supported course packs remain mapped by the original V1.13.6 stack.

Rendering rule:

1. Load the resource for the **current selected course + variant + hole**.
2. Render with `fit-center` / aspect-ratio preserved.
3. **Never crop the tee box or green.**
4. Tee and green must both be visible in the same stage.
5. Do not stretch the course artwork horizontally or vertically.
6. When changing holes, clear the previous frame before drawing the next image. No residual line / image garbage is allowed.

---

## 3. Approved layout geometry

All values below are normalized to screen width `w` and height `h` so the same UI can be reproduced on supported portrait devices.

### Header

- Sky header: `x 0.000–1.000`, `y 0.000–0.056`
- Course title left: approx `x 0.040–0.550`
- Weather/GPS card: `x 0.580–0.978`, `y 0.004–0.052`

### Metrics strip

- Green strip: `x 0.035–0.965`, `y 0.056–0.098`
- Previous-hole arrow: `x 0.040–0.135`
- TOTAL center: `x 0.295`
- DIST center: `x 0.515`
- PAR center: `x 0.720`
- Next-hole arrow: `x 0.865–0.960`

### Main yardage panel

- Panel: `x 0.035–0.965`, `y 0.103–0.842`
- GREEN tag: `x 0.050–0.127`, `y 0.109–0.132`
- HOLE card: `x 0.052–0.168`, `y 0.176–0.238`
- PAR card: `x 0.178–0.258`, `y 0.176–0.238`
- Yardage image frame: `x 0.285–0.685`, `y 0.145–0.790`
- Ruler: right side of image, labels aligned toward `x ~0.905`, tick endpoint `x ~0.945`
- TEE tag: `x 0.050–0.113`, `y 0.807–0.830`

### Action row

- GREEN CENTER: `x 0.035–0.355`, `y 0.850–0.910`
- TEE 저장: `x 0.370–0.670`, `y 0.850–0.910`
- 외부 지도: `x 0.685–0.965`, `y 0.850–0.910`

### Bottom navigation

Five fixed tabs:

1. 홈
2. 코스
3. 입력
4. 카드
5. 요약

Course tab is highlighted while the approved course screen is active.

---

## 4. Yardage ruler LOCK

- Ruler interval: **50 m**.
- Labels: `50m, 100m, 150m ...` up to the current hole maximum.
- Ruler font is large and bold as approved.
- Ruler does not change the yardage artwork geometry.
- Tee is the bottom / 0 m anchor.
- Green is the upper distance end.
- Do not move the artwork to make a label fit. Move/scale only the ruler text region if necessary.

---

## 5. Realtime GPS LOCK

GPS must use Android native location updates from the V1.13.6 stack.

- Position source: device GPS.
- Signal bars use `Location.getAccuracy()`.
- Current mapping:
  - `<= 5 m`: 4 bars
  - `<= 8 m`: 3 bars
  - `<= 12 m`: 2 bars
  - `> 12 m`: 1 bar
- Status is `GOOD` only when the existing `gpsUsable()` criteria pass.
- DIST uses the current location and current-hole green reference when available.
- TEE / GREEN save actions preserve the existing V1.13.6 confirmation and coordinate-storage logic.
- Do not replace or fork the GPS core merely for UI changes.

---

## 6. Realtime weather / wind LOCK

The approved top-right card must not display hardcoded sample weather.

Current implementation:

- Query position: latest device GPS latitude / longitude.
- Weather provider: Open-Meteo current weather endpoint.
- Runtime fields:
  - `temperature_2m`
  - `weather_code`
  - `wind_speed_10m`
  - `wind_direction_10m`
- Wind speed unit: **m/s**.
- Wind direction display: `N / NE / E / SE / S / SW / W / NW`.
- Refresh rule: approximately 10 minutes, or when moved more than 1 km.
- On network/API failure: do **not** invent values. Show `--` or retain the last valid observation.
- GPS signal remains independent of weather network availability.

---

## 7. Dynamic fields vs locked visual fields

### Dynamic — must follow the current hole/course

- Course name
- Course variant
- H1–H18
- PAR
- TOTAL
- DIST
- Yardage artwork
- 50 m ruler maximum
- Previous / next hole state
- GPS quality
- Temperature
- Weather condition
- Wind direction
- Wind speed
- TEE / GREEN saved coordinates

### Locked — must not be redesigned without a new PASS

- Sky-blue header height
- White weather/GPS card location and shape
- Green TOTAL/DIST/PAR strip
- Round previous/next arrow design
- Gold HOLE/PAR cards and their relative widths
- Main pale-green yardage panel
- Yardage image central placement
- Right ruler placement
- GREEN / TEE tags
- Three lower action buttons
- Five storybook bottom-nav tabs
- Rounded typography language
- Cream/green/sky/gold approved color hierarchy

---

## 8. Home screen reproduction rule

The home screen must come from the **original V1.13.6 ROUND LOG UI stack / approved raster assets**, not a newly improvised Canvas home.

- Preserve the V1.13.6 home artwork and course-selection flow.
- Preserve current course selection and variant selection behavior.
- Preserve the original round-start action.
- The course-screen hotfix must not silently replace the home artwork.

---

## 9. Build / QA gate

A reproduced APK is not PASS unless all of the following are true:

- Original V1.13.6 ROUND LOG logic is present.
- Approved UI hotfix marker is present.
- Current-hole yardage image changes correctly for every hole.
- No tee/green crop.
- No hole-switch residual graphics.
- PAR and TOTAL match the selected hole.
- DIST changes with real GPS location when a green reference is available.
- GPS bars reflect actual accuracy.
- Weather/wind are realtime or `--`; never fixed demo values.
- Home screen remains the V1.13.6 approved/original stack.
- Score input behavior is not altered by this UI-only hotfix.

---

## 10. Reproduction sequence

For a future rebuild:

1. Start from the V1.13.6 ROUND LOG base stack.
2. Restore the original V1.13.6 concept/home assets.
3. Restore all supported hole-yardage resources.
4. Apply the original patch chain through `patch-v1136`.
5. Apply `patch-v1136-approved-ui-hotfix.py`.
6. Apply `patch-v1136-realtime-weather.py`.
7. Build with JDK 17 / Gradle 8.9.
8. Verify full-hole resources and fonts are packaged.
9. Run visual QA against this LOCK document.
10. Only then publish the APK.

Current hotfix scripts:

- `.github/scripts/patch-v1136-approved-ui-hotfix.py`
- `.github/scripts/patch-v1136-realtime-weather.py`

Current hotfix workflow:

- `.github/workflows/build-v1130-concept.yml`

---

## 11. DO NOT

- Do not redraw the PASS screen into a different layout.
- Do not hardcode H1 / PAR5 / 478 m as permanent values.
- Do not hardcode `19°`, `E`, `2.0 m/s`.
- Do not crop the lower tee box.
- Do not enlarge the yardage image by stretching.
- Do not substitute a schematic fairway when a real hole image exists.
- Do not modify score-entry UX as part of this hotfix.
- Do not touch the protected `beta-ver2` field-test baseline.

**This MD is the visual/data-binding source of truth for V1.13.6 APPROVED UI reproduction.**
