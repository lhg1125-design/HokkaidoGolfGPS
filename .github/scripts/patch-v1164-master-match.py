from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'CONCEPT REFERENCE LOCK V1.16.3' not in s or 'drawGoldenMasterV1162' not in s:
    raise SystemExit('V1.16.4 requires V1.16.3 master renderer')
if 'IMAGE MASTER MATCH V1.16.4' in s:
    print('V1.16.4 already applied'); raise SystemExit(0)

# The approved image master is the visual source of truth. Remove the redundant
# top FRONT/CENTER/BACK distance values while retaining the master wood header.
s=s.replace('goldenMetricV1162(c,ds.front,166,Color.rgb(30,145,255));goldenMetricV1162(c,center,470,Color.WHITE);goldenMetricV1162(c,ds.back,775,Color.rgb(255,80,72));','/* V1.16.4 master match: redundant top distance metrics intentionally suppressed */',1)

# Enlarge the actual official-hole image into the master artwork viewport.
# Aspect ratio is preserved by masterFitSourceV1161; raw Royal Links bytes remain untouched.
s=s.replace('RectF slot=new RectF(250,355,690,1435)','RectF slot=new RectF(238,350,704,1442)',1)

# Make the remaining-distance bubble the single dominant distance readout.
s=s.replace('goldenTextV1162(c,remain+"m",816,500,48,Color.rgb(25,25,20),Paint.Align.CENTER,false);','goldenTextV1162(c,remain+"m",816,500,52,Color.rgb(25,25,20),Paint.Align.CENTER,false);',1)

# Provenance marker.
s=s.replace('        // CONCEPT REFERENCE LOCK V1.16.3','        // IMAGE MASTER MATCH V1.16.4\n        // Approved image master is the runtime visual source of truth.\n        // CONCEPT REFERENCE LOCK V1.16.3',1)

p.write_text(s)
print('V1.16.4 IMAGE MASTER MATCH: redundant top metrics removed + official course viewport enlarged')
