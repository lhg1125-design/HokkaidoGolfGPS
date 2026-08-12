from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.5.1 · COURSE DATA PACK' not in s:
    raise SystemExit('v1.6 base version not found')
s=s.replace('V1.5.1 · COURSE DATA PACK','V1.6 · FIELD GPS CAPTURE',1)

# 1) Scorecard containment fix: H9/H18 must stay inside the OUT/IN cards.
old='''            float firstY=top+h*.122f,rowStep=h*.0552f;'''
new='''            float firstY=top+h*.118f,rowStep=h*.0492f;'''
if old not in s:
    raise SystemExit('v1.6 score row spacing pattern missing')
s=s.replace(old,new,1)

# Pull the lower card boundary up slightly so there is a clean visual gap before ROUND SUMMARY.
s=s.replace('''            float top=h*.145f,bottom=h*.705f;''','''            float top=h*.145f,bottom=h*.690f;''',1)

# 2) Field-capture readiness indicator next to source provenance.
# This does not invent data: it only reflects whether the live GPS fix is accurate enough to save.
needle='''            pill(c,new RectF(w*.70f,h*.700f,w*.93f,h*.728f),Color.rgb(236,246,228),hazardSourceLabel(),GREEN,6.5f);'''
insert='''            int capCol=location==null?CORAL:(location.getAccuracy()<=8?GREEN:(location.getAccuracy()<=12?AMBER:CORAL));
            String capTxt=location==null?"CAPTURE WAIT":(location.getAccuracy()<=8?"CAPTURE READY":(location.getAccuracy()<=12?"CAPTURE FAIR":"CAPTURE LOCK"));
            int capBg=capCol==GREEN?Color.rgb(229,244,218):(capCol==AMBER?Color.rgb(255,246,218):Color.rgb(255,238,229));
            pill(c,new RectF(w*.055f,h*.700f,w*.345f,h*.728f),capBg,capTxt,capCol,6.5f);
            pill(c,new RectF(w*.70f,h*.700f,w*.93f,h*.728f),Color.rgb(236,246,228),hazardSourceLabel(),GREEN,6.5f);'''
if needle not in s:
    raise SystemExit('v1.6 capture badge insertion point missing')
s=s.replace(needle,insert,1)

# 3) Make the existing Green/Tee field-capture controls communicate the GPS quality gate.
old_save='''            goldButton(c,greenSave,green==null?CORAL:DEEP,greenSaveLabel(),Color.WHITE,19.6f);
            goldButton(c,teeSave,getRef("t",hole)==null?Color.rgb(53,139,94):DEEP,getRef("t",hole)==null?"TEE 저장":"TEE OK",Color.WHITE,19.6f);'''
new_save='''            boolean capReady=previewMode || (location!=null && location.getAccuracy()<=12 && fixAgeSec()<=15);
            int gBg=capReady?(green==null?CORAL:DEEP):Color.rgb(150,160,150);
            int tBg=capReady?(getRef("t",hole)==null?Color.rgb(53,139,94):DEEP):Color.rgb(150,160,150);
            goldButton(c,greenSave,gBg,greenSaveLabel(),Color.WHITE,19.6f);
            goldButton(c,teeSave,tBg,getRef("t",hole)==null?"TEE 저장":"TEE OK",Color.WHITE,19.6f);'''
if old_save not in s:
    raise SystemExit('v1.6 field capture button pattern missing')
s=s.replace(old_save,new_save,1)

p.write_text(s)
print('applied v1.6 scorecard containment + field GPS capture readiness')
