from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.13.6 APPROVED UI HOTFIX' not in s:
    raise SystemExit('approved live marker requires approved UI hotfix')

needle='''            courseRect.set(imgInner);\n            drawApprovedRulerV1136(c,w,h,imgFrame,totalM);'''
replacement='''            courseRect.set(imgInner);\n            // Restore the proven V1.13.5/V1.13.6 live-field overlay on top of the locked PASS yardage.\n            // Once TEE + GREEN CENTER are calibrated and GPS is usable, the same circular\n            // accuracy halo / player-position marker follows the real 2D geo engine.\n            drawFieldNavV1110(c,imgInner,totalM);\n            drawApprovedRulerV1136(c,w,h,imgFrame,totalM);'''

if 'drawFieldNavV1110(c,imgInner,totalM);' in s:
    print('approved live marker already linked')
elif needle not in s:
    raise SystemExit('approved yardage overlay anchor missing')
else:
    s=s.replace(needle,replacement,1)

p.write_text(s)
print('restored calibrated circular live-GPS marker on approved PASS yardage UI')
