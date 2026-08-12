from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.10.0 · FIELD BETA' not in s:
    raise SystemExit('v1.10.1 requires v1.10.0 field beta')
s=s.replace('V1.10.0 · FIELD BETA','V1.10.1 · FIELD YARDAGE SAFE',1)

# Separate the hole arrows from the yardage map. The previous pager circle could
# touch the H/PAR/distance chip on tall displays. New order is:
# status -> dedicated pager gutter -> yardage card -> capture controls.
old='courseRect.set(m,h*.287f,w-m,h*.575f);drawActualYardageV190(c,courseRect,par,totalM);drawHolePager(c,h*.301f);'
new='courseRect.set(m,h*.318f,w-m,h*.575f);drawActualYardageV190(c,courseRect,par,totalM);drawHolePager(c,h*.292f);'
if old not in s:
    raise SystemExit('v1.10.1 pager/yardage anchor missing')
s=s.replace(old,new,1)

# V1.10 footer says DIST OK. That is valid for published Japan/Royal distance
# or field-calibrated Naepo distance, but not before Naepo calibration.
old='textFit(c,"DIST OK · "+shapeLabelV1100()+" · "+calStatusV1100(),src.left+10,src.centerY()+3,src.right-10,8.1f,yardageSourceColorV190(),true);'
new='String safeFooter=(selected==3 && fieldGpsMetersV190()==0)?("FIELD CAL REQUIRED · "+calStatusV1100()):("DIST OK · "+shapeLabelV1100()+" · "+calStatusV1100());textFit(c,safeFooter,src.left+10,src.centerY()+3,src.right-10,8.1f,yardageSourceColorV190(),true);'
if old not in s:
    raise SystemExit('v1.10.1 footer anchor missing')
s=s.replace(old,new,1)

p.write_text(s)
print('applied v1.10.1 safe yardage card + calibration truth guard')
