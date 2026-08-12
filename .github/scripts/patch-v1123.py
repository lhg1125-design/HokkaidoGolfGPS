from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.12.2 · MAP PIN FOCUS' not in s:
    raise SystemExit('v1.12.3 requires v1.12.2 map pin focus')
s=s.replace('V1.12.2 · MAP PIN FOCUS','V1.12.3 · MAX MAP',1)

# Remove the duplicated in-map hole/total title line-by-line so minor spacing
# changes in earlier patches cannot break this final compression pass.
title_anchor='RectF title=new RectF(r.left+12,r.top+6,r.right-12,r.top+34)'
ti=s.find(title_anchor)
if ti<0:
    raise SystemExit('v1.12.3 title rect anchor missing')
tls=s.rfind('\n',0,ti)+1
tle=s.find('\n',ti)
s=s[:tls]+s[tle+1:]

text_anchor='textFit(c,"H"+hole+" · P"+par+" · "+verifiedDistanceLabelV190()'
tx=s.find(text_anchor)
if tx<0:
    raise SystemExit('v1.12.3 title text anchor missing')
tls=s.rfind('\n',0,tx)+1
tle=s.find('\n',tx)
s=s[:tls]+s[tle+1:]

stage_old='RectF stage=new RectF(r.left+8,r.top+38,r.right-8,r.bottom-28);'
st=s.find(stage_old)
if st<0:
    raise SystemExit('v1.12.3 stage anchor missing')
s=s[:st]+stage_old.replace('r.top+38','r.top+7')+s[st+len(stage_old):]

# Direct map movement is self-evident: orange pin moves and REMAIN changes.
# Do not cover the yardage with a simulator toast.
toast='showToast("SIM · "+Math.round(simProgressV1112*100f)+"%");'
if toast not in s:
    raise SystemExit('v1.12.3 SIM toast anchor missing')
s=s.replace(toast,'',1)

p.write_text(s)
print('applied v1.12.3 max-map: no duplicate in-map title and no SIM overlay toast')
