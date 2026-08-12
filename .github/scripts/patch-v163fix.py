from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
old='for(int pl=0;pl<n;pl){'
if old not in s:
    raise SystemExit('v1.6.3 malformed player loop not found')
s=s.replace(old,'for(int pl=0;pl<n;pl++){')
p.write_text(s)
print('fixed v1.6.3 dynamic-player loop increments')
