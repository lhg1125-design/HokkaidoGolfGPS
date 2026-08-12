from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.12.2 · MAP PIN FOCUS' not in s:
    raise SystemExit('v1.12.3 requires v1.12.2 map pin focus')
s=s.replace('V1.12.2 · MAP PIN FOCUS','V1.12.3 · MAX MAP',1)

# Remove the duplicated in-map hole/total title; the compact top metric row
# already carries TOTAL / REMAIN / PAR. Give that space directly to hole art.
old='''            RectF title=new RectF(r.left+12,r.top+6,r.right-12,r.top+34);box(c,title,Color.argb(238,255,255,255),14);
            textFit(c,"H"+hole+" · P"+par+" · "+verifiedDistanceLabelV190(),title.left+10,title.centerY()+3,title.right-10,8.0f,DEEP,true);
            RectF stage=new RectF(r.left+8,r.top+38,r.right-8,r.bottom-28);'''
new='''            RectF stage=new RectF(r.left+8,r.top+7,r.right-8,r.bottom-28);'''
if old not in s:
    raise SystemExit('v1.12.3 duplicate map title anchor missing')
s=s.replace(old,new,1)

# Direct map movement is self-evident: orange pin moves and REMAIN changes.
# Do not cover the yardage with a simulator toast.
old='''                showToast("SIM · "+Math.round(simProgressV1112*100f)+"%");invalidate();return true;'''
new='''                invalidate();return true;'''
if old not in s:
    raise SystemExit('v1.12.3 SIM toast anchor missing')
s=s.replace(old,new,1)

p.write_text(s)
print('applied v1.12.3 max-map: no duplicate in-map title and no SIM overlay toast')
