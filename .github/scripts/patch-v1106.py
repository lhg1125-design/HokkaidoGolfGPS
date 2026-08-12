from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.10.5 · HOKKAIDO FULL HOLE VERIFIED' not in s:
    raise SystemExit('v1.10.6 requires v1.10.5 verified full-hole renderer')
s=s.replace('V1.10.5 · HOKKAIDO FULL HOLE VERIFIED','V1.10.6 · HOKKAIDO 126 HOLE PACK',1)
p.write_text(s)
print('applied v1.10.6 preserved 126 full-hole resource pack')
