from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
s=s.replace('"V1.7 · KOREA FIELD TEST"','"V1.8 · PREMIUM COURSE ART"')
p.write_text(s)
print('fixed v1.8 premium home badge')
