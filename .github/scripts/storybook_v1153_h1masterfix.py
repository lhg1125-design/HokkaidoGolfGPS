from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
old='if(hole==1)return new RectF(267.41f,365f,672.59f,1422f);'
new='if(hole==1)return new RectF(260f,390f,625f,1452f);'
if old not in s:
    if new not in s:
        raise SystemExit('Furano KING H1 master rect anchor missing')
else:
    s=s.replace(old,new,1)

# The H1 visual sprite is the approved 365x1062 master at x=260,y=390.
# Runtime GPS/player position mapping must use that exact rectangle.
if 'V1.15.3 · FURANO H1 MASTER RECT' not in s:
    s=s.replace('V1.15.2 · FURANO KING123 GOLDEN','V1.15.2 · FURANO KING123 GOLDEN / V1.15.3 · FURANO H1 MASTER RECT',1)

p.write_text(s)
print('V1.15.3 FURANO H1 MASTER RECT: runtime map/GPS bounds locked to (260,390)-(625,1452); H2/H3 unchanged')
