from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.11.3 · FIRST ROUND NAV' not in s:
    raise SystemExit('v1.11.4 requires v1.11.3 first-round nav')
s=s.replace('V1.11.3 · FIRST ROUND NAV','V1.11.4 · FIELD READY NAV',1)

marker='        private void roundJapanPremium(Canvas c){roundUnifiedYardageV190(c);}'
pos=s.find(marker)
if pos<0: raise SystemExit('v1.11.4 renderer marker missing')
helpers=r'''        private String fieldReadyLabelV1114(){
            if(previewMode)return "SIM READY";
            if(location==null)return "GPS WAIT";
            if(!gpsUsable())return "GPS CHECK";
            boolean t=getRef("t",hole)!=null,g=greenCenterRef(hole)!=null;
            if(t&&g)return "FIELD READY";
            if(t&&verifiedMetersV190()>0)return "EST READY";
            if(!t)return "SAVE TEE";
            return "SAVE GREEN";
        }
        private int fieldReadyBgV1114(){
            String x=fieldReadyLabelV1114();
            if(x.equals("FIELD READY")||x.equals("SIM READY"))return Color.argb(112,199,239,176);
            if(x.equals("EST READY"))return Color.argb(108,255,226,143);
            return Color.argb(70,255,255,255);
        }

'''
s=s[:pos]+helpers+s[pos:]

# Capture kind=1 is key "g" (= green center). Keep method signatures intact and
# only correct user-visible wording so a FRONT label can never imply the wrong point.
s=s.replace('"GREEN FRONT"','"GREEN CENTER"')
s=s.replace('"GREEN 저장"','"GREEN CENTER 저장"')
s=s.replace('"GREEN OK"','"GREEN CENTER OK"')

# The provenance remains in the full-hole footer. Use the small header pill for
# operational readiness, which is what matters during a live round.
old='''            pill(c,new RectF(w*.69f,h*.086f,w*.94f,h*.128f),Color.argb(62,255,255,255),yardageSourceV190(),Color.WHITE,7.0f);'''
new='''            pill(c,new RectF(w*.69f,h*.086f,w*.94f,h*.128f),fieldReadyBgV1114(),fieldReadyLabelV1114(),Color.WHITE,7.0f);'''
if old not in s:
    raise SystemExit('v1.11.4 header readiness anchor missing')
s=s.replace(old,new,1)

p.write_text(s)
print('applied v1.11.4 truthful GREEN CENTER + FIELD/EST READY UI')
