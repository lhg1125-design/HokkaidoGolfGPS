from pathlib import Path

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
# Avoid duplicate insertion if the original metrics somehow survived.
near=s[s.find(anchor):s.find(anchor)+500]
if 'goldenMetricV1162(c,ds.front' not in near:
    s=s.replace(anchor,anchor+metric,1)

# Restore the approved narrow/tall course viewport so the score panel,
# remaining-distance bubble, ruler, target button and bottom navigation never
# collide with course art.
s=s.replace('RectF slot=new RectF(220,205,735,1435)','RectF slot=new RectF(260,365,680,1422)',1)

# Provenance marker only; no runtime pixel effects.
s=s.replace('        // CONCEPT REFERENCE LOCK V1.16.3','        // PASS MASTER RESTORE V1.16.6\n        // Approved Royal Links H1/H2 layout: wood metrics visible + original course slot.\n        // CONCEPT REFERENCE LOCK V1.16.3',1)

p.write_text(s)
print('V1.16.6 PASS MASTER RESTORED: wood metrics visible; original course viewport restored')
