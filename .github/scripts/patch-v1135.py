from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.13.4 · JP/KR 2D GEO FULL FIT' not in s:
    raise SystemExit('v1.13.5 requires V1.13.4 JP/KR full-fit geo')
s=s.replace('V1.13.4 · JP/KR 2D GEO FULL FIT','V1.13.5 · ALL COURSES LIVE GEO',1)

# -----------------------------------------------------------------------------
# V1.13.5 field-navigation layer
# - Same multi-fix TEE/GREEN capture for Japan, Royal Links and Naepo.
# - Fuse real TEE->GREEN geographic projection with distance-ratio progress.
# - Use visual hole curvature to reduce straight-axis cross-track correction on
#   doglegs, avoiding false lateral pin jumps.
# - Keep published artwork as visual geometry only; no fabricated production
#   hole coordinates are introduced.
# -----------------------------------------------------------------------------

field_anchor='        private byte[] fullCenterBytesV1134=null,fullHalfWBytesV1134=null;'
if field_anchor not in s:
    raise SystemExit('v1.13.5 packed geo field anchor missing')
s=s.replace(field_anchor,field_anchor+r'''
        private final double[] liveLatV1135=new double[7],liveLonV1135=new double[7];
        private final float[] liveAccV1135=new float[7];
        private final long[] liveTsV1135=new long[7];
        private int liveFixCountV1135=0,liveFixIndexV1135=0;
''',1)

loc_anchor='            location=l; lastFixElapsed=SystemClock.elapsedRealtime();'
if loc_anchor not in s:
    raise SystemExit('v1.13.5 setLocation anchor missing')
s=s.replace(loc_anchor,loc_anchor+'\n            recordLiveFixV1135(l);',1)

# Insert generic live-fix helpers before the old Naepo-only helper. Keeping the
# old helper preserves backward compatibility with existing Field Packs.
marker='        private GeoRef naepoCaptureFixV1131(){'
pos=s.find(marker)
if pos<0:
    raise SystemExit('v1.13.5 capture helper anchor missing')
helpers=r'''        private void recordLiveFixV1135(Location l){
            if(l==null || !l.hasAccuracy() || l.getAccuracy()>35f)return;
            int i=liveFixIndexV1135;liveLatV1135[i]=l.getLatitude();liveLonV1135[i]=l.getLongitude();liveAccV1135[i]=Math.max(1f,l.getAccuracy());liveTsV1135[i]=SystemClock.elapsedRealtime();
            liveFixIndexV1135=(i+1)%liveLatV1135.length;if(liveFixCountV1135<liveLatV1135.length)liveFixCountV1135++;
        }
        private int liveRecentSamplesV1135(){
            long now=SystemClock.elapsedRealtime();int n=0;float lim=selected==3?25f:18f;
            for(int i=0;i<liveFixCountV1135;i++)if(liveTsV1135[i]>0 && now-liveTsV1135[i]<=9000 && liveAccV1135[i]<=lim)n++;
            return n;
        }
        private GeoRef liveCaptureFixV1135(){
            if(location==null)return null;long now=SystemClock.elapsedRealtime();float lim=selected==3?25f:18f;double sw=0,la=0,lo=0;
            for(int i=0;i<liveFixCountV1135;i++){
                if(liveTsV1135[i]<=0 || now-liveTsV1135[i]>9000 || liveAccV1135[i]>lim)continue;
                double w=1.0/Math.max(4.0,liveAccV1135[i]*liveAccV1135[i]);sw+=w;la+=liveLatV1135[i]*w;lo+=liveLonV1135[i]*w;
            }
            if(sw<=0)return new GeoRef(location.getLatitude(),location.getLongitude(),false);
            return new GeoRef(la/sw,lo/sw,false);
        }
        private float liveCaptureSpreadV1135(){
            GeoRef c=liveCaptureFixV1135();if(c==null)return 99f;long now=SystemClock.elapsedRealtime();float lim=selected==3?25f:18f;double ss=0,sw=0;
            for(int i=0;i<liveFixCountV1135;i++){
                if(liveTsV1135[i]<=0 || now-liveTsV1135[i]>9000 || liveAccV1135[i]>lim)continue;
                float[] out=new float[1];Location.distanceBetween(c.lat,c.lon,liveLatV1135[i],liveLonV1135[i],out);double w=1.0/Math.max(4.0,liveAccV1135[i]*liveAccV1135[i]);ss+=out[0]*out[0]*w;sw+=w;
            }
            return sw<=0?99f:(float)Math.sqrt(ss/sw);
        }
        private int savedSamplesV1135(String type,int h){return calPrefs.getInt(refKey(type,h)+"_samples",0);}
        private float savedSpreadV1135(String type,int h){return calPrefs.getFloat(refKey(type,h)+"_spread",-1f);}
        private float geoAxisMetersV1135(){
            GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t==null||g==null)return -1f;float[] out=new float[1];Location.distanceBetween(t.lat,t.lon,g.lat,g.lon,out);return out[0];
        }
        private String liveGeoChipV1135(){
            GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t==null)return "FIELD CAL · SAVE TEE";
            int ts=Math.max(1,savedSamplesV1135("t",hole));if(g==null)return "TEE CAL · FIX "+ts;
            int gs=Math.max(1,savedSamplesV1135("g",hole));float sp=Math.max(savedSpreadV1135("t",hole),savedSpreadV1135("g",hole));
            String spread=sp>=0?(" · σ"+Math.round(sp)+"m"):"";return "LIVE 2D · FIX "+Math.min(ts,gs)+spread;
        }
        private int liveGeoColorV1135(){
            GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t==null)return CORAL;if(g==null)return AMBER;float sp=Math.max(savedSpreadV1135("t",hole),savedSpreadV1135("g",hole));return sp<0||sp<=8?GREEN:(sp<=12?AMBER:CORAL);
        }
        private float fullDoglegReliabilityV1135(float q){
            float z=Math.max(0f,Math.min(1f,q));float c0=fullCenterXV1134(0f),c1=fullCenterXV1134(1f),actual=fullCenterXV1134(z),linear=c0+(c1-c0)*z;
            float dev=Math.abs(actual-linear);return Math.max(.30f,Math.min(1f,1f-dev*4.2f));
        }

'''
s=s[:pos]+helpers+s[pos:]

# Replace nav progress with dogleg-aware geographic fusion. TEE-only behavior
# remains the same truthful distance-from-tee estimate until GREEN is captured.
a=s.find('        private float navProgressV1110(){')
b=s.find('        private int navRemainV1110(',a)
if a<0 or b<0: raise SystemExit('v1.13.5 nav progress boundary missing')
nav_progress=r'''        private float navProgressV1110(){
            if(previewMode)return simProgressV1112;
            if(location==null || !navGpsUsableV1133())return -1f;
            GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t==null)return -1f;
            if(g==null){int total=verifiedMetersV190();if(total<=0)return -1f;float walked=distance(location,t.lat,t.lon);return Math.max(0f,Math.min(1f,walked/Math.max(1f,total)));}
            double lat0=Math.toRadians((t.lat+g.lat)*.5);double gx=(g.lon-t.lon)*Math.cos(lat0),gy=g.lat-t.lat;double px=(location.getLongitude()-t.lon)*Math.cos(lat0),py=location.getLatitude()-t.lat;double den=gx*gx+gy*gy;if(den<1e-15)return -1f;
            float proj=(float)((px*gx+py*gy)/den);proj=Math.max(0f,Math.min(1f,proj));
            float dt=distance(location,t.lat,t.lon),dg=distance(location,g.lat,g.lon);float ratio=(dt+dg)<1f?proj:dt/(dt+dg);
            float trust=fullDoglegReliabilityV1135(proj);float q=trust*proj+(1f-trust)*ratio;return Math.max(0f,Math.min(1f,q));
        }
'''
s=s[:a]+nav_progress+s[b:]

# Replace the full field-nav renderer. It keeps V1.13.4 full-fit registration,
# adds curvature-gated cross-track, and shows a compact live calibration chip.
a=s.find('        private void drawFieldNavV1110(Canvas c,RectF stage,int totalM){')
b=s.find('        private String fieldReadyLabelV1114(){',a)
if a<0 or b<0: raise SystemExit('v1.13.5 field nav boundary missing')
field_nav=r'''        private void drawFieldNavV1110(Canvas c,RectF stage,int totalM){
            if(!navReadyV1110()){
                RectF wait=new RectF(stage.right-100,stage.top+7,stage.right-8,stage.top+27);box(c,wait,Color.argb(224,255,247,218),10);textFit(c,"TEE CAL",wait.left+8,wait.centerY()+3,wait.right-8,5.2f,AMBER,true);return;
            }
            float q=navProgressV1110();if(q<0)return;RectF img=fullFitImageRectV1134(stage);
            float targetY=img.top+(.965f-.93f*q)*img.height();float cx=fullCenterXV1134(q),hw=fullHalfWV1134(q);float targetX=img.left+cx*img.width();
            if(!navEstimatedV1113() && getRef("t",hole)!=null && greenCenterRef(hole)!=null){
                float cross=navCrossTrackMetersV1133();float corridorM=currentPar()==3?30f:45f;float frac=Math.max(-1.15f,Math.min(1.15f,cross/corridorM));float trust=fullDoglegReliabilityV1135(q);
                targetX+=Math.max(9f,hw*img.width())*frac*.82f*trust;
            }
            targetX=Math.max(img.left+8f,Math.min(img.right-8f,targetX));targetY=Math.max(img.top+10f,Math.min(img.bottom-10f,targetY));
            if(navSmoothHoleV1133!=hole || navSmoothVariantV1133!=variant || Float.isNaN(navSmoothXV1133)){navSmoothHoleV1133=hole;navSmoothVariantV1133=variant;navSmoothXV1133=targetX;navSmoothYV1133=targetY;}
            else{float acc=previewMode?6f:(location!=null?location.getAccuracy():25f);float alpha=acc<=8f?.18f:(acc<=15f?.12f:.08f);navSmoothXV1133+=alpha*(targetX-navSmoothXV1133);navSmoothYV1133+=alpha*(targetY-navSmoothYV1133);}
            float x=navSmoothXV1133,y=navSmoothYV1133;float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/250.0));float acc=previewMode?6f:(location!=null?Math.max(3f,location.getAccuracy()):25f);int quality=acc<=8?GREEN:(acc<=15?AMBER:CORAL);int orange=Color.rgb(255,132,35);float uncertainty=Math.max(18f,Math.min(34f,16f+acc*.58f));
            p.setColor(Color.argb((int)(25+35*pulse),Color.red(quality),Color.green(quality),Color.blue(quality)));c.drawCircle(x,y,uncertainty+4f*pulse,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.2f);p.setColor(Color.argb(145,Color.red(quality),Color.green(quality),Color.blue(quality)));c.drawCircle(x,y,uncertainty,p);p.setStrokeWidth(4f);p.setColor(Color.WHITE);c.drawCircle(x,y,15.5f,p);p.setStyle(Paint.Style.FILL);p.setColor(orange);c.drawCircle(x,y,11.5f,p);p.setColor(Color.rgb(255,240,218));c.drawCircle(x,y,3.2f,p);
            RectF chip=new RectF(stage.left+8,stage.bottom-28,Math.min(stage.right-8,stage.left+170),stage.bottom-7);box(c,chip,Color.argb(226,255,255,247),10);textFit(c,liveGeoChipV1135(),chip.left+7,chip.centerY()+3,chip.right-7,5.2f,liveGeoColorV1135(),true);
        }

'''
s=s[:a]+field_nav+s[b:]

# Operational status applies to every course now.
a=s.find('        private String fieldReadyLabelV1114(){')
b=s.find('        private int fieldReadyBgV1114(){',a)
if a<0 or b<0: raise SystemExit('v1.13.5 field-ready label boundary missing')
label=r'''        private String fieldReadyLabelV1114(){
            if(previewMode)return "LIVE 2D SIM";if(location==null)return "GPS WAIT";if(!navGpsUsableV1133())return "GPS CHECK";
            boolean t=getRef("t",hole)!=null,g=greenCenterRef(hole)!=null;if(t&&g)return "LIVE 2D";if(t&&verifiedMetersV190()>0)return "TEE CAL";return "SAVE TEE";
        }
'''
s=s[:a]+label+s[b:]
# Treat LIVE 2D as green-ready in the existing background helper.
s=s.replace('if(x.equals("FIELD READY")||x.equals("SIM READY"))','if(x.equals("FIELD READY")||x.equals("SIM READY")||x.equals("LIVE 2D")||x.equals("LIVE 2D SIM"))',1)
s=s.replace('if(x.equals("EST READY"))','if(x.equals("EST READY")||x.equals("TEE CAL"))',1)

# Replace single-fix reference capture with stable multi-fix capture for all
# courses. Naepo retains its wider TEST tolerance; others allow 18m only when
# at least three recent fixes agree.
a=s.find('        private void saveRef(int kind){')
b=s.find('        private GeoRef getRef(String type,int h){',a)
if a<0 or b<0: raise SystemExit('v1.13.5 saveRef boundary missing')
save=r'''        private void saveRef(int kind){
            if(location==null){showToast("GPS 위치를 먼저 잡아주세요");return;}float limit=selected==3?25f:18f;int samples=liveRecentSamplesV1135();float spread=liveCaptureSpreadV1135();
            if(!previewMode && location.getAccuracy()>limit){showToast("GPS ±"+Math.round(location.getAccuracy())+"m · HOLD");return;}
            if(!previewMode && location.getAccuracy()>12f && samples<3){showToast("GPS FIX 3개 이상 모은 후 저장");return;}
            if(!previewMode && samples>=3 && spread>12f){showToast("GPS 흔들림 σ"+Math.round(spread)+"m · 잠시 후 재시도");return;}
            long now=SystemClock.uptimeMillis();if(confirmKind!=kind || now>confirmUntil){confirmKind=kind;confirmUntil=now+3200;showToast(kind==1?"GREEN CENTER에서 한 번 더 눌러 저장":"TEE에서 한 번 더 눌러 저장");invalidate();return;}
            String type=kind==1?"g":"t",k=refKey(type,hole);GeoRef cap=liveCaptureFixV1135();if(cap==null){showToast("GPS FIX 없음");return;}int n=Math.max(1,samples);float rawAcc=location.getAccuracy();float sp=n>=2?spread:rawAcc;
            calPrefs.edit().putLong(k+"_lat",Double.doubleToRawLongBits(cap.lat)).putLong(k+"_lon",Double.doubleToRawLongBits(cap.lon)).putFloat(k+"_acc",rawAcc).putInt(k+"_samples",n).putFloat(k+"_spread",sp).putLong(k+"_ts",System.currentTimeMillis()).apply();
            confirmKind=0;confirmUntil=0;String mode=n>=3?(" · "+n+"FIX σ"+Math.round(sp)+"m"):(" · ±"+Math.round(rawAcc)+"m");showToast("H"+hole+" "+(kind==1?"GREEN CENTER":"TEE")+" 저장"+mode);navSmoothXV1133=Float.NaN;navSmoothYV1133=Float.NaN;maybeAutoHole();invalidate();
        }

'''
s=s[:a]+save+s[b:]

# Preview-only TEE/GREEN refs for every non-Naepo course. These exist solely to
# exercise LIVE 2D in CI screenshots; production still requires real captures.
get_marker='        private GeoRef getRef(String type,int h){'
pos=s.find(get_marker)
if pos<0: raise SystemExit('v1.13.5 getRef marker missing')
insert=pos+len(get_marker)
preview=r'''
            if(previewMode && selected>=0 && selected!=3 && (type.equals("t")||type.equals("g"))){
                int hh=Math.max(1,Math.min(18,h));double meters=Math.max(80.0,yards[selected][variant][hh-1]*.9144);double ang=Math.toRadians((selected*53+variant*31+hh*19)%360);double north=Math.cos(ang)*meters/111111.0,east=Math.sin(ang)*meters/(111320.0*Math.cos(Math.toRadians(courseLat[selected])));double clat=courseLat[selected]+(hh-9.5)*.000025,clon=courseLon[selected]+(hh-9.5)*.000018;
                if(type.equals("t"))return new GeoRef(clat-north*.5,clon-east*.5,true);return new GeoRef(clat+north*.5,clon+east*.5,true);
            }
'''
s=s[:insert]+preview+s[insert:]

p.write_text(s)
print('applied v1.13.5 all-course stable capture + dogleg-aware live geo fusion')
