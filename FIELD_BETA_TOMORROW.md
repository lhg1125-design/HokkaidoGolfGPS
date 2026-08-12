# HokkaidoGolfGPS V1.10 — Tomorrow Field Beta Checklist

Goal: confirm the APK behaves like a real round before the Hokkaido trip, without treating guide-only geometry as precise GPS data.

## 0. Install / reset (5 min)
- Install `HokkaidoGolfGPS-v1.10.0-field-beta-debug.apk`.
- Allow Precise Location while using the app.
- Disable battery optimization for the app during the test if Android aggressively suspends GPS.
- Keep the screen on and confirm the home screen is fully visible above the navigation bar.

## 1. Static course check (10 min)
Check these priority holes first because official guide evidence exists:
- Kamishihoro CHAMPIONS H4: right-side large pond + creek before green.
- Kamishihoro CHAMPIONS H7: uphill / left pot bunker warning.
- Kamishihoro CHAMPIONS H11: long front bunker / right-side safe line.
- Kamishihoro MASTERS H12: downhill / left-front pond.
- Kamishihoro MASTERS H13: gentle right dogleg + creek on second-shot zone.
- Kamishihoro MASTERS H15: pond around roughly half of green + large bunkers both sides.
- Furano PALMER H15: pond around green + cross bunker.
- Furano KING H17: pond + bunker left of green; right-side strategy.
- Sahoro: distance and PAR are verified; unverified hole-shape details must remain GUIDE rather than exact GPS claims.

## 2. Outdoor GPS check (15–20 min)
- Stand in open sky for 2–3 minutes.
- Confirm GPS status changes from WAIT/LOCK toward FAIR/GOOD.
- Confirm the app does not freeze when GPS accuracy changes repeatedly.
- Select a Korea practice course and save one TEE and one GREEN CENTER reference as a rehearsal.
- Confirm the footer changes from `GPS G- T-` to the saved state.
- Kill and reopen the app; confirm saved references and round state remain.

## 3. Round-flow rehearsal (15 min)
- Configure 3 players.
- Enter strokes and putts for H1–H3.
- Move H1 → H2 → H3 → H2 and confirm each hole keeps its own values.
- Confirm a tapped target from one hole disappears after changing holes.
- Open Score Input, Scorecard, Summary, then return Home.
- Confirm no text/button is clipped at the bottom or under system navigation.

## 4. Failure checks
Record any of these immediately with a screenshot:
- wrong hole/PAR/distance
- map or distance label clipped
- touch target overlaps another button
- GPS becomes stale but remains displayed as GOOD
- saved TEE/GREEN disappears after restart
- score from another hole/player appears in the wrong slot
- app ANR/crash or black screen

## Data trust rules for the beta
- Japan trip-course REGULAR yardages: published-source values.
- Royal Links WHITE: official meter values.
- Naepo: only field-saved TEE ↔ GREEN data may be treated as actual hole distance.
- `GUIDE` water/bunker drawings are strategy illustrations unless captured by field GPS.
- Front/Center/Back must only be treated as live exact values when the related field GPS references exist.

## Pass target
The beta is considered ready for the trip when:
1. APK launches 10/10 times without crash/ANR.
2. All priority holes display the correct PAR/distance and the expected official-guide warning.
3. 3-player scoring survives app restart.
4. TEE/GREEN capture survives app restart.
5. Pixel 6 class and compact 720×1600 screenshots show no clipping.
