from pathlib import Path

java=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
manifest=Path('app/src/main/AndroidManifest.xml')
if not java.exists(): raise SystemExit('missing generated FieldGpsV09Activity.java')
if not manifest.exists(): raise SystemExit('missing AndroidManifest.xml')
s=java.read_text()
m=manifest.read_text()

checks=[]
def req(label, token, source=s):
    ok=token in source
    checks.append((label,ok))
    if not ok: raise SystemExit(f'PREBUILD FAIL: {label}: missing {token}')

def one(label, token):
    n=s.count(token)
    checks.append((label,n==1))
    if n!=1: raise SystemExit(f'PREBUILD FAIL: {label}: expected 1 occurrence, got {n}')

# 1) Native GPS + stable multi-fix CAL capture.
req('GPS_PROVIDER native updates','LocationManager.GPS_PROVIDER')
req('live fix recorder','recordLiveFixV1135(l);')
req('recent-fix CAL sample check','liveRecentSamplesV1135()')
req('CAL spread stability check','liveCaptureSpreadV1135()')
req('CAL accuracy HOLD','location.getAccuracy()>limit')
req('CAL double-confirm window','confirmUntil=now+3200')

# 2) TEE-first remaining distance and live player marker.
req('TEE-first remaining helper','private int approvedRemainingV1136(')
req('GREEN precise remaining upgrade','if(green!=null)return Math.max(0,Math.round(distance(location,green.lat,green.lon)))')
req('TEE-only fallback','GeoRef tee=getRef("t",hole);')
req('TEE-only remaining subtract','totalM-travelled')
req('TEE starts player marker','if(getRef("t",hole)!=null && navGpsUsableV1133()) drawFieldNavV1110(c,imgInner,totalM);')
req('marker accuracy halo','float uncertainty=Math.max(18f,Math.min(34f,16f+acc*.58f));')
req('marker white ring','p.setColor(Color.WHITE);c.drawCircle(x,y,15.5f,p)')

# 3) GPS status card is based on real Android Location accuracy and stale-fix policy.
req('GPS bars from Location accuracy','float a=location.getAccuracy();bars=a<=5?4:(a<=8?3:(a<=12?2:1))')
req('GPS GOOD/WAIT uses gpsUsable','boolean good=gpsUsable();')
req('navigation uses stale/quality gate','navGpsUsableV1133()')

# 4) Realtime weather/wind from current GPS coordinates; no sample values in final renderer.
req('realtime weather marker','V1.13.6 REALTIME WEATHER')
req('Open-Meteo endpoint','api.open-meteo.com')
req('weather latitude current GPS','final double lat=l.getLatitude(),lon=l.getLongitude();')
req('live temperature','temperature_2m')
req('live wind speed','wind_speed_10m')
req('live wind direction','wind_direction_10m')
req('internet permission','android.permission.INTERNET',m)

# 5) Automatic hole detection: detect -> propose -> user confirms; never silent commit.
req('one-shot field mode','V1.13.6 ONE-SHOT FIELD MODE')
req('auto detection requires current TEE','GeoRef tee=getRef("t",hole)')
req('auto detector uses optional GREEN when available','approvedRemainingV1136(total,greenCenterRef(hole))')
req('finish-zone threshold','float finishBand=Math.max(25f,Math.min(45f,total*.08f));')
req('departure dwell','now-holeExitAtV1136<12000L')
req('departure movement','if(out[0]<40f)return;')
req('auto proposes popup','openHoleDetectPopupV1136(Math.min(18,hole+1));')
req('only accept commits candidate','hole=Math.max(1,Math.min(18,holeDetectCandidateV1136));')
req('candidate actual packaged mini yardage','return fullHoleBitmapV1102();')
req('candidate fit-center','RectF dst=fitCenterV1102(mb,miniInner)')

# 6) GREEN CENTER is optional: it improves current-hole true range and the next-hole
# transition trigger, but it must not be required to start marker/DIST or auto detection.
req('GREEN save remains optional action','if(greenSave.contains(x,y)){saveRef(1);return true;}')
req('TEE save canonical action','if(teeSave.contains(x,y)){saveRef(2);return true;}')
req('GREEN upgrades 2D projection only when present','if(!navEstimatedV1113() && getRef("t",hole)!=null && greenCenterRef(hole)!=null)')

# 7) Final popup visual/TTS layer must exist once only.
req('cute popup final layer','V1.13.6 HOLE POPUP CUTE CHARACTER WALLPAPER + TTS')
one('single speaker Rect declaration','private final RectF holeDetectSpeakV1136')
one('single TTS engine declaration','private android.speech.tts.TextToSpeech holeDetectTtsV1136')
one('single speaker renderer','private void drawHoleDetectSpeakerV1136(')
req('speaker reads hole/PAR/distance/strategy','private String holeDetectSpeechV1136()')

print('V1.13.6 FIELD PREBUILD CHECKLIST')
for label,ok in checks:
    print(f'[PASS] {label}')
print(f'PASS_TOTAL={sum(1 for _,ok in checks if ok)}/{len(checks)}')
print('GREEN_POLICY=OPTIONAL; improves true final distance + transition confidence, not raw Android GPS accuracy')
print('BUILD_READY=YES')
