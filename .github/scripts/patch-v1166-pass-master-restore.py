from pathlib import Path
import re

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'CONCEPT REFERENCE LOCK V1.16.3' not in s:
    raise SystemExit('V1.16.6 PASS restore requires V1.16.3 base marker')
if 'PASS MASTER RESTORE V1.16.6' in s:
    print('V1.16.6 PASS master already restored'); raise SystemExit(0)

# The approved Royal Links H1/H2 PASS design keeps the walnut
# FRONT/CENTER/BACK board. V1.16.3 incorrectly suppressed its dynamic values.
anchor='int center=ds.center>=0?ds.center:totalM;'
if anchor not in s:
    raise SystemExit('PASS restore: distance anchor missing')
metric='goldenMetricV1162(c,ds.front,166,Color.rgb(30,145,255));goldenMetricV1162(c,center,470,Color.WHITE);goldenMetricV1162(c,ds.back,775,Color.rgb(255,80,72));'
near=s[s.find(anchor):s.find(anchor)+500]
if 'goldenMetricV1162(c,ds.front' not in near:
    s=s.replace(anchor,anchor+metric,1)

# Restore the approved narrow/tall course viewport LAST, after the static loader
# patch. Restrict replacement to drawGoldenMasterV1162 so no unrelated RectF is touched.
start=s.find('        private void drawGoldenMasterV1162(Canvas c)')
if start<0: raise SystemExit('PASS restore: golden draw method missing')
end=s.find('        private boolean masterSourceMappedV1161()',start)
if end<0: end=len(s)
chunk=s[start:end]
chunk2,n=re.subn(r'RectF slot=new RectF\([^;]+\)',
                 'RectF slot=new RectF(260,365,680,1422)',chunk,count=1)
if n!=1: raise SystemExit('PASS restore: course slot replacement failed')
s=s[:start]+chunk2+s[end:]

# Provenance marker only; no runtime pixel effects.
s=s.replace('        // CONCEPT REFERENCE LOCK V1.16.3','        // PASS MASTER RESTORE V1.16.6\n        // Approved Royal Links H1/H2 layout: wood metrics visible + original course slot.\n        // CONCEPT REFERENCE LOCK V1.16.3',1)

# Hard assertions: this patch is authoritative and must fail before APK build if
# either approved PASS requirement is lost.
if 'RectF slot=new RectF(260,365,680,1422)' not in s:
    raise SystemExit('PASS restore: final course slot not locked')
if 'goldenMetricV1162(c,ds.front,166' not in s:
    raise SystemExit('PASS restore: wood metrics missing')

p.write_text(s)
print('V1.16.6 PASS MASTER RESTORED: wood metrics visible; original course viewport restored')
