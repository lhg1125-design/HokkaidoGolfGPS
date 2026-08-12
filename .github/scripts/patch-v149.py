from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
target='V1.4.3 · FIVE SCREEN GPS'
if target not in s:
    for old in ['V1.4.2 · FIVE SCREEN GPS','V1.4.1 · FIVE SCREEN GPS','V1.4 · FIVE SCREEN GPS','V1.3 · SCORECARD XL','V1.2.2 · ARTWORK FIDELITY']:
        if old in s:
            s=s.replace(old,target,1)
            break
if target not in s:
    marker='public class FieldGpsV09Activity extends Activity implements LocationListener {'
    if marker not in s: raise SystemExit('v1.4.9 class marker not found')
    s=s.replace(marker,marker+'\n    private static final String BUILD_BADGE = "'+target+'";',1)
p.write_text(s)
print('applied v1.4.9 version bridge for v1.5 data pack')
