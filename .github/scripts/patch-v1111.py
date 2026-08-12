from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.11.0 · FIELD NAV BETA' not in s:
    raise SystemExit('v1.11.1 requires v1.11.0 field nav beta')
s=s.replace('V1.11.0 · FIELD NAV BETA','V1.11.1 · FIELD NAV SAFE',1)
old='''            String mode=previewMode?"SIM AXIS":"GPS AXIS";\n            String msg=mode+" · "+(remain>=0?remain+"m TO GREEN":"--")+" · "+navAccuracyV1110();'''
new='''            String mode=previewMode?"SIM AXIS":"GPS AXIS";\n            String msg=previewMode?(mode+" · "+(remain>=0?remain+"m":"--")):(mode+" · "+(remain>=0?remain+"m":"--")+" · "+navAccuracyV1110());'''
if old not in s:
    raise SystemExit('v1.11.1 nav status anchor missing')
s=s.replace(old,new,1)
p.write_text(s)
print('applied v1.11.1 compact-safe field nav status')
