from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
old='if(selected==3){GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t!=null&&g!=null)return Math.round(distance(t.lat,t.lon,g.lat,g.lon)/.9144f);return 0;}'
new='if(selected==3){GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t!=null&&g!=null){float[] o=new float[1];Location.distanceBetween(t.lat,t.lon,g.lat,g.lon,o);return Math.round(o[0]/.9144f);}return 0;}'
if old not in s:
    raise SystemExit('v1.7.0 Naepo distance fix anchor missing')
s=s.replace(old,new,1)
p.write_text(s)
print('fixed v1.7.0 Naepo tee-green distance calculation')
