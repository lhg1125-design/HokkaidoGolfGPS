from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.9.0 · ACTUAL YARDAGE PACK' not in s:
    raise SystemExit('v1.9.1 requires v1.9.0 actual yardage pack')
s=s.replace('V1.9.0 · ACTUAL YARDAGE PACK','V1.9.1 · ACTUAL YARDAGE SAFE UI',1)

# Keep the round arrow buttons in their own row. In V1.9.0 they touched the
# top source chip inside the yardage card on tall phones. This creates a true
# no-overlap gutter between status, hole pager and the yardage canvas.
old='courseRect.set(m,h*.287f,w-m,h*.575f);drawActualYardageV190(c,courseRect,par,totalM);drawHolePager(c,h*.301f);'
new='courseRect.set(m,h*.318f,w-m,h*.575f);drawActualYardageV190(c,courseRect,par,totalM);drawHolePager(c,h*.292f);'
if old not in s:
    raise SystemExit('v1.9.1 yardage/pager layout anchor missing')
s=s.replace(old,new,1)

# Naepo has no verified published per-hole length in the current data pack.
# Until TEE + GREEN CENTER are captured, never render the word VERIFIED.
old='goldText(c,yardageSourceV190()+" · DISTANCE VERIFIED",src.centerX(),src.centerY(),8.4f,yardageSourceColorV190());'
new='String verifyFooter=(selected==3 && fieldGpsMetersV190()==0)?"GPS CALIBRATION · SAVE TEE + GREEN":(yardageSourceV190()+" · DISTANCE VERIFIED");goldText(c,verifyFooter,src.centerX(),src.centerY(),8.4f,yardageSourceColorV190());'
if old not in s:
    raise SystemExit('v1.9.1 verification footer anchor missing')
s=s.replace(old,new,1)

p.write_text(s)
print('applied v1.9.1 safe yardage pager + Naepo verification guard')
