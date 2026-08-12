from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.13.0 · CONCEPT ART SKIN' not in s:
    raise SystemExit('v1.13.1 requires v1.13.0 concept-art skin')
s=s.replace('V1.13.0 · CONCEPT ART SKIN','V1.13.1 · NAEPO FIELD TEST',1)

# -----------------------------------------------------------------------------
# 1) Naepo capture policy: field testing must continue even when consumer GPS
#    is noisier than the final 12 m production target. Up to 25 m is accepted
#    only for Naepo TEST mode, with the raw accuracy and sample count persisted.
#    Five recent usable fixes are weighted for the saved reference coordinate.
# -----------------------------------------------------------------------------
field_anchor='        private Typeface conceptKoV1130,conceptJpV1130;'
if field_anchor not in s:
    raise SystemExit('v1.13.1 concept font field anchor missing')
s=s.replace(field_anchor,field_anchor+'''\n        private final double[] naepoLatV1131=new double[5],naepoLonV1131=new double[5];\n        private final float[] naepoAccV1131=new float[5];\n        private int naepoFixCountV1131=0,naepoFixIndexV1131=0;''',1)

loc_anchor='''            location=l; lastFixElapsed=SystemClock.elapsedRealtime();'''
if loc_anchor not in s:
    raise SystemExit('v1.13.1 setLocation anchor missing')
s=s.replace(loc_anchor,loc_anchor+'''\n            if(selected==3 && l!=null && l.hasAccuracy() && l.getAccuracy()<=35f){\n                naepoLatV1131[naepoFixIndexV1131]=l.getLatitude();\n                naepoLonV1131[naepoFixIndexV1131]=l.getLongitude();\n                naepoAccV1131[naepoFixIndexV1131]=Math.max(1f,l.getAccuracy());\n                naepoFixIndexV1131=(naepoFixIndexV1131+1)%naepoLatV1131.length;\n                if(naepoFixCountV1131<naepoLatV1131.length)naepoFixCountV1131++;\n            }''',1)

marker='        private void roundJapanPremium(Canvas c){roundUnifiedYardageV190(c);}'
pos=s.find(marker)
if pos<0:
    raise SystemExit('v1.13.1 stable renderer marker missing')
helpers=r'''        private GeoRef naepoCaptureFixV1131(){
            if(location==null)return null;
            if(selected!=3 || naepoFixCountV1131<=0)return new GeoRef(location.getLatitude(),location.getLongitude(),false);
            double sw=0,la=0,lo=0;
            for(int i=0;i<naepoFixCountV1131;i++){
                float a=Math.max(2f,naepoAccV1131[i]);double w=1.0/(a*a);sw+=w;la+=naepoLatV1131[i]*w;lo+=naepoLonV1131[i]*w;
            }
            if(sw<=0)return new GeoRef(location.getLatitude(),location.getLongitude(),false);
            return new GeoRef(la/sw,lo/sw,false);
        }
        private int savedAccV1131(String type,int h){
            String k=refKey(type,h);return Math.round(calPrefs.getFloat(k+"_acc",-1f));
        }
        private int savedSamplesV1131(String type,int h){
            String k=refKey(type,h);return calPrefs.getInt(k+"_samples",0);
        }
        private int naepoRepeatDeltaV1131(){
            if(selected!=3)return -1;int ph=((hole-1)%9)+1;GeoRef a=getRef("t",ph),b=getRef("t",ph+9);if(a==null||b==null)return -1;
            float[] o=new float[1];Location.distanceBetween(a.lat,a.lon,b.lat,b.lon,o);return Math.round(o[0]);
        }
        private String naepoFixLabelV1131(){
            if(previewMode)return "SIM · 5 FIX AVG";
            if(location==null)return "GPS WAIT";
            String q=location.getAccuracy()<=12?"GOOD":(location.getAccuracy()<=25?"TEST":"HOLD");
            return q+" · ±"+Math.round(location.getAccuracy())+"m · FIX "+Math.max(1,naepoFixCountV1131)+"/5";
        }
        private int naepoFixColorV1131(){
            if(previewMode)return GREEN;if(location==null)return CORAL;return location.getAccuracy()<=12?GREEN:(location.getAccuracy()<=25?AMBER:CORAL);
        }
        private String naepoActiveGreenV1131(){
            boolean second=hole>9;boolean red=(variant==0?!second:second);return red?"RED GREEN":"YELLOW GREEN";
        }
        private void drawNaepoFieldCanvasV1131(Canvas c,RectF r,int par,int totalM){
            softShadow(c,r,30);box(c,r,Color.rgb(250,249,229),30);
            RectF stage=new RectF(r.left+8,r.top+7,r.right-8,r.bottom-28);
            gradient(c,stage,Color.rgb(242,249,221),Color.rgb(202,235,179),24);
            c.save();Path clip=new Path();clip.addRoundRect(stage,24,24,Path.Direction.CW);c.clipPath(clip);
            // Field-calibration lane only. This intentionally does NOT invent a
            // Naepo hole shape/hazard position; the live GPS axis is the truth.
            float cx=stage.centerX(),top=stage.top+42,bottom=stage.bottom-34;
            p.setColor(Color.argb(40,255,255,255));for(int i=0;i<7;i++){float y=stage.top+i*stage.height()/6f;c.drawRect(stage.left,y,stage.right,y+stage.height()/12f,p);}
            p.setStyle(Paint.Style.STROKE);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeWidth(Math.max(18f,stage.width()*.10f));p.setColor(Color.argb(96,72,161,76));c.drawLine(cx,bottom,cx,top,p);
            p.setStrokeWidth(3f);p.setColor(Color.argb(155,54,80,54));for(int k=1;k<=5;k++){float y=bottom-(bottom-top)*k/6f;c.drawLine(cx-stage.width()*.12f,y,cx+stage.width()*.12f,y,p);}p.setStyle(Paint.Style.FILL);p.setStrokeCap(Paint.Cap.BUTT);

            // Same physical tee concept; two greens remain clearly differentiated.
            p.setColor(DEEP);c.drawRoundRect(new RectF(cx-42,bottom-8,cx+42,bottom+8),8,8,p);text(c,"TEE",cx,bottom+31,7.2f,DEEP,true,Paint.Align.CENTER);
            float gxL=cx-stage.width()*.13f,gxR=cx+stage.width()*.13f,gy=top;
            p.setColor(Color.rgb(61,145,74));c.drawOval(new RectF(gxL-42,gy-17,gxL+42,gy+17),p);c.drawOval(new RectF(gxR-42,gy-17,gxR+42,gy+17),p);
            p.setColor(Color.rgb(216,54,62));c.drawCircle(gxL,gy,8,p);p.setColor(Color.rgb(246,198,38));c.drawCircle(gxR,gy,8,p);
            boolean red=naepoActiveGreenV1131().startsWith("RED");float agx=red?gxL:gxR;
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4f);p.setColor(Color.argb(220,255,255,255));c.drawCircle(agx,gy,19,p);p.setStyle(Paint.Style.FILL);

            if(totalM>0){
                p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4f);p.setColor(Color.argb(150,31,99,58));c.drawLine(cx,bottom,agx,gy,p);p.setStyle(Paint.Style.FILL);
            }
            c.restore();

            RectF topChip=new RectF(stage.left+10,stage.top+9,stage.right-10,stage.top+39);box(c,topChip,Color.argb(238,255,255,245),15);
            textFit(c,"H"+naepoPhysicalHole(hole)+" · P"+par+" · "+naepoActiveGreenV1131(),topChip.left+10,topChip.centerY()+3,topChip.right-10,7.6f,DEEP,true);

            RectF fixChip=new RectF(stage.left+10,stage.bottom-34,stage.right-10,stage.bottom-7);box(c,fixChip,Color.argb(240,255,255,245),13);
            String f=totalM>0?("FIELD CAL "+totalM+"m · "+naepoFixLabelV1131()):("1 TEE 저장  →  2 GREEN CENTER 저장 · "+naepoFixLabelV1131());
            textFit(c,f,fixChip.left+8,fixChip.centerY()+3,fixChip.right-8,6.1f,naepoFixColorV1131(),true);

            int rep=naepoRepeatDeltaV1131();
            if(rep>=0){RectF rr=new RectF(stage.left+10,stage.top+44,stage.left+154,stage.top+69);box(c,rr,Color.argb(236,255,246,218),12);text(c,"TEE REPEAT Δ "+rep+"m",rr.centerX(),rr.centerY()+3,6.0f,rep<=8?GREEN:(rep<=15?AMBER:CORAL),true,Paint.Align.CENTER);}
            else {RectF rr=new RectF(stage.left+10,stage.top+44,stage.left+146,stage.top+69);box(c,rr,Color.argb(228,255,255,245),12);text(c,"GPS AXIS · NOT GEO MAP",rr.centerX(),rr.centerY()+3,5.5f,Color.rgb(96,111,79),true,Paint.Align.CENTER);}

            if(totalM>0)drawDistanceRulerV1102(c,new RectF(stage.left+4,stage.top+16,stage.right-4,stage.bottom-18),totalM);
            drawFieldNavV1110(c,stage,totalM);

            RectF src=new RectF(r.left+12,r.bottom-25,r.right-12,r.bottom-4);box(c,src,Color.argb(242,255,255,255),10);
            String srcLabel=totalM>0?"NAEPO FIELD CAL · LIVE GPS · TEE → GREEN":"NAEPO FIELD CAL · CAPTURE REQUIRED";
            textFit(c,srcLabel,src.left+8,src.centerY()+3,src.right-8,5.8f,totalM>0?GREEN:CORAL,true);
        }

'''
s=s[:pos]+helpers+s[pos:]

# Naepo uses the honest field-cal canvas instead of the generic schematic map.
old_null='''            if(b==null){\n                drawActualYardageV190(c,r,par,totalM);\n                RectF tag=new RectF(r.left+18,r.top+55,r.left+135,r.top+83);box(c,tag,Color.argb(225,255,247,218),14);text(c,"SCHEMATIC FULL HOLE",tag.centerX(),tag.centerY()+3,5.8f,DEEP,true,Paint.Align.CENTER);\n                return;\n            }'''
new_null='''            if(b==null){\n                if(selected==3){drawNaepoFieldCanvasV1131(c,r,par,totalM);return;}\n                drawActualYardageV190(c,r,par,totalM);\n                RectF tag=new RectF(r.left+18,r.top+55,r.left+135,r.top+83);box(c,tag,Color.argb(225,255,247,218),14);text(c,"SCHEMATIC FULL HOLE",tag.centerX(),tag.centerY()+3,5.8f,DEEP,true,Paint.Align.CENTER);\n                return;\n            }'''
if old_null not in s:
    raise SystemExit('v1.13.1 full-hole fallback anchor missing')
s=s.replace(old_null,new_null,1)

# Naepo field-test capture accepts weak-but-usable fixes up to 25 m. Other
# courses retain the stricter 12 m reference-capture gate.
old_gate='''            if(!previewMode && location.getAccuracy()>12){showToast("GPS ±"+Math.round(location.getAccuracy())+"m · 12m 이하에서 저장");return;}'''
new_gate='''            float captureLimit=(selected==3?25f:12f);\n            if(!previewMode && location.getAccuracy()>captureLimit){showToast("GPS ±"+Math.round(location.getAccuracy())+"m · "+Math.round(captureLimit)+"m 이하에서 저장");return;}'''
if old_gate not in s:
    raise SystemExit('v1.13.1 reference accuracy gate anchor missing')
s=s.replace(old_gate,new_gate,1)

old_write='''            calPrefs.edit().putLong(k+"_lat",Double.doubleToRawLongBits(location.getLatitude())).putLong(k+"_lon",Double.doubleToRawLongBits(location.getLongitude())).apply();\n            confirmKind=0;confirmUntil=0;showToast("H"+hole+" "+(kind==1?"GREEN CENTER":"TEE")+" 저장 완료");maybeAutoHole();invalidate();'''
new_write='''            GeoRef cap=(selected==3?naepoCaptureFixV1131():new GeoRef(location.getLatitude(),location.getLongitude(),false));\n            int samples=selected==3?Math.max(1,naepoFixCountV1131):1;float rawAcc=location.getAccuracy();\n            calPrefs.edit().putLong(k+"_lat",Double.doubleToRawLongBits(cap.lat)).putLong(k+"_lon",Double.doubleToRawLongBits(cap.lon)).putFloat(k+"_acc",rawAcc).putInt(k+"_samples",samples).putLong(k+"_ts",System.currentTimeMillis()).apply();\n            confirmKind=0;confirmUntil=0;String weak=(selected==3&&rawAcc>12f)?" · TEST ±"+Math.round(rawAcc)+"m":"";showToast("H"+hole+" "+(kind==1?"GREEN CENTER":"TEE")+" 저장 완료"+weak);maybeAutoHole();invalidate();'''
if old_write not in s:
    raise SystemExit('v1.13.1 reference write anchor missing')
s=s.replace(old_write,new_write,1)

# Make the visible capture buttons follow the same Naepo 25 m test policy.
s=s.replace('location.getAccuracy()<=12 && fixAgeSec()<=15','location.getAccuracy()<=(selected==3?25:12) && fixAgeSec()<=15')

# Simulator refs make the complete Naepo field flow inspectable off-site. They
# are generated only in PREVIEW/SIM mode and are never persisted as course data.
get_anchor='''        private GeoRef getRef(String type,int h){'''
if get_anchor not in s:
    raise SystemExit('v1.13.1 getRef anchor missing')
s=s.replace(get_anchor,get_anchor+'''\n            if(previewMode && selected==3){\n                int ph=((h-1)%9)+1;int pa=parForHole(h);double meters=pa==3?165.0:(pa==5?485.0:345.0);\n                double baseLat=36.6743245+(ph-5)*0.000055,baseLon=126.6698247+(ph-5)*0.000035;\n                double teeLat=baseLat-meters/111111.0,teeLon=baseLon;boolean second=h>9;boolean red=(variant==0?!second:second);\n                double greenLon=baseLon+(red?-0.00015:0.00015);\n                if(type.equals("t"))return new GeoRef(teeLat,teeLon,true);\n                if(type.equals("g"))return new GeoRef(baseLat,greenLon,true);\n            }''',1)

# Home card wording: make it obvious that Naepo is the deliberate live field
# rehearsal course rather than an incomplete official map pack.
old_region='''            String[] region={"JP 01","JP 02","JP 03","KR TEST","KR OFFICIAL"};'''
new_region='''            String[] region={"JP 01","JP 02","JP 03","NAEPO FIELD","KR OFFICIAL"};'''
if old_region not in s:
    raise SystemExit('v1.13.1 home region anchor missing')
s=s.replace(old_region,new_region,1)

# Naepo field guide is now explicitly about test sequence and repeatability.
old_guide='''            if(selected==3){\n                int m=currentOfficialM();\n                return m>0?("FIELD CAL 완료 · TEE↔GREEN 직선 "+m+"m · 벙커/워터 GPS를 현장에서 추가 저장"):("내포 9H TWO-GREEN 테스트 · TEE와 GREEN을 저장하면 이 홀의 실제 GPS 거리로 전환");\n            }'''
new_guide='''            if(selected==3){\n                int m=currentOfficialM(),rep=naepoRepeatDeltaV1131();\n                if(m>0)return "FIELD CAL "+m+"m · 오렌지 위치/잔여거리 확인 · 2회차 TEE 반복오차"+(rep>=0?(" Δ"+rep+"m"):" 측정 예정");\n                return "내포 FIELD TEST · TEE 저장 → GREEN CENTER 저장 → 오렌지 위치/잔여거리/스코어 흐름 점검";\n            }'''
if old_guide not in s:
    raise SystemExit('v1.13.1 Naepo strategy anchor missing')
s=s.replace(old_guide,new_guide,1)

p.write_text(s)
print('applied v1.13.1 Naepo concept field-test canvas + tolerant GPS capture + repeatability check')
