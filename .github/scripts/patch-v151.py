from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

# Preview V1.5 on a verified official-guide hole: Kamishihoro Champions H4.
s=s.replace('selected=0; variant=0; hole=11;','selected=0; variant=0; hole=4;',1)
s=s.replace('demo.setLatitude(43.2585100);demo.setLongitude(143.2283600);demo.setAccuracy(5f);',
            'demo.setLatitude(43.2587150);demo.setLongitude(143.2283600);demo.setAccuracy(5f);',1)

marker='''            if(previewMode && selected==0 && variant==0 && h==11){
                if(type.equals("gf")) return new GeoRef(43.25970,143.22836,true);
                if(type.equals("g") || type.equals("gc")) return new GeoRef(43.25982,143.22836,true);
                if(type.equals("gb")) return new GeoRef(43.25994,143.22836,true);
                if(type.equals("t")) return new GeoRef(43.25720,143.22836,true);
            }'''
if marker not in s:
    raise SystemExit('v1.5.1 preview ref marker not found')
new='''            if(previewMode && selected==0 && variant==0 && h==4){
                if(type.equals("gf")) return new GeoRef(43.26011,143.22836,true);
                if(type.equals("g") || type.equals("gc")) return new GeoRef(43.26023,143.22836,true);
                if(type.equals("gb")) return new GeoRef(43.26035,143.22836,true);
                if(type.equals("t")) return new GeoRef(43.25720,143.22836,true);
            }
'''+marker
s=s.replace(marker,new,1)

s=s.replace('V1.5 · COURSE DATA PACK','V1.5.1 · COURSE DATA PACK',1)
p.write_text(s)
print('applied v1.5.1 official-guide H4 preview')
