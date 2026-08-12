from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.11.4 · FIELD READY NAV' not in s:
    raise SystemExit('v1.12.0 requires v1.11.4 field-ready nav')
s=s.replace('V1.11.4 · FIELD READY NAV','V1.12.0 · FIELD BETA KIT',1)
p.write_text(s)
print('applied v1.12.0 field beta kit banner')
