# HokkaidoGolfGPS Resources Master

## 1. Asset Master Rule

### asset_bg
- `asset_bg_original` is the only review baseline.
- Runtime overlay verification must always be performed on the untouched original background.
- Do not save composite images back into asset_bg.

## 2. Yardage Assets

- Use processed transparent yardage images as the golf course map layer.
- Do not reuse APK embedded yardage JPG images for display rendering.
- APK yardage files are reference sources only for data extraction.

Recommended structure:
```
assets/
 ├─ background/
 │   └─ asset_bg_original.png
 ├─ yardage/
 │   ├─ sahoro/
 │   │   ├─ H01.png ~ H18.png
 │   ├─ japan_course_02/
 │   └─ japan_course_03/
```

## 3. Distance Data Source

JSON source:
- Hole metadata
- Par
- Tee position
- Front / Center / Back fixed values
- Green pin coordinate

Runtime GPS:
- Each APK user calculates distance independently.
- Master and Follower use the same green pin target.
- Display distance = current player GPS position → pin location.

## 4. Runtime Overlay Layer Order

```
1. asset_bg_original
2. transparent yardage PNG
3. distance scale overlay
4. player GPS marker
5. player legend overlay
6. top wood board realtime distance
```

## 5. Top Wood Board UI Rule

FRONT / CENTER / BACK labels already exist in asset_bg.

Only numbers are overlaid.

Rules:
- FRONT: fixed position, GPS unavailable = `--`
- CENTER: fixed STD distance + GPS realtime value
- Remove `| GPS --` style.
- GPS realtime number is bold emphasized.
- BACK: fixed position, GPS unavailable = `--`

## 6. Right Distance Legend Rule

- Player colored circle must sit directly on distance scale line.
- Player name and remaining distance are shown in a dark rounded box.
- Box width must fully contain name text.
- If players approach same position, automatically adjust spacing to avoid overlap.
- Direction: upward means approaching green pin.

## 7. Review Process

Every UI step must generate a review image.

Validation sequence:
1. asset_bg only
2. asset_bg + yardage PNG
3. overlay coordinates
4. GPS simulation
5. multiplayer legend
6. runtime APK verification

## 8. Source Control Rule

GitHub repository:
`lhg1125-design/HokkaidoGolfGPS`

Recommended folders:
```
runtime_overlay/
assets/
data/
apk_reference/
review/
```

## Status

Current baseline:
- Yardage composition: PASS
- Tee 0m alignment: PASS
- Overlay coordinate correction: IN PROGRESS
