from pathlib import Path
import numpy as np
from PIL import Image

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.13.2 · NAEPO REAL YARDAGE' not in s:
    raise SystemExit('v1.13.3 requires V1.13.2 Naepo real yardage')
s=s.replace('V1.13.2 · NAEPO REAL YARDAGE','V1.13.3 · NAEPO 2D GEO PIN',1)

# -----------------------------------------------------------------------------
# Build-time visual registration: derive a smooth tee->green visual centerline
# from each of the 9 real Naepo yardage crops. This does not claim geographic
# registration of the published artwork; it only makes the GPS progress marker
# follow the actual drawn hole corridor instead of a generic straight axis.
# -----------------------------------------------------------------------------
root=Path('app/src/main/res/drawable-nodpi')
centers=[]; widths=[]
SAMPLES=41
for hole in range(1,10):
    fp=root/f'yardage_naepo_{hole:02d}.jpg'
    if not fp.exists(): raise SystemExit(f'missing {fp}')
    im=Image.open(fp).convert('RGB')
    a=np.asarray(im).astype(np.int16); h,w,_=a.shape
    corners=np.concatenate([a[:max(4,h//25),:max(4,w//12)].reshape(-1,3),a[:max(4,h//25),-max(4,w//12):].reshape(-1,3),a[-max(4,h//25):,:max(4,w//12)].reshape(-1,3),a[-max(4,h//25):,-max(4,w//12):].reshape(-1,3)])
    bg=np.median(corners,axis=0)
    diff=np.sqrt(((a-bg)**2).sum(axis=2))
    mx=a.max(axis=2); mn=a.min(axis=2); sat=mx-mn
    # Real course body is colored and far from the cream/white matte.
    mask=(diff>38)&((sat>22)|(mx<215))
    cs=[]; ws=[]
    for i in range(SAMPLES):
        q=i/(SAMPLES-1)
        yf=.965-.93*q
        yy=int(round(yf*(h-1))); band=max(3,int(h*.012))
        y1=max(0,yy-band); y2=min(h,yy+band+1)
        ys,xs=np.where(mask[y1:y2])
        if len(xs)<12:
            # Wider local search for thin tee/green ends.
            band=max(band,int(h*.028)); y1=max(0,yy-band);y2=min(h,yy+band+1);ys,xs=np.where(mask[y1:y2])
        if len(xs)<8:
            c=.5; hw=.20
        else:
            lo=float(np.percentile(xs,6)); hi=float(np.percentile(xs,94))
            c=((lo+hi)*.5)/(w-1); hw=max(.035,((hi-lo)*.5)/(w-1))
        cs.append(c);ws.append(hw)
    # light smoothing so tiny labels/OB strokes do not make the marker jitter.
    for _ in range(2):
        cs=[cs[0]]+[float(np.median(cs[max(0,i-1):min(SAMPLES,i+2)])) for i in range(1,SAMPLES-1)]+[cs[-1]]
        ws=[ws[0]]+[float(np.median(ws[max(0,i-1):min(SAMPLES,i+2)])) for i in range(1,SAMPLES-1)]+[ws[-1]]
    centers.append(cs);widths.append(ws)

def jarray(name,data):
    rows=[]
    for row in data:
        rows.append('            {'+','.join(f'{v:.4f}f' for v in row)+'}')
    return '        private static final float[][] '+name+'={\n'+',\n'.join(rows)+'\n        };\n'

field_anchor='        private Typeface conceptKoV1130,conceptJpV1130;'
if field_anchor not in s: raise SystemExit('v1.13.3 field anchor missing')
extra='''\n        private float simCrossTrackV1133=0f;\n        private float navSmoothXV1133=Float.NaN,navSmoothYV1133=Float.NaN;\n        private int navSmoothHoleV1133=-1,navSmoothVariantV1133=-1;\n        private Bitmap cachedHoleBitmapV1133=null; private String cachedHoleNameV1133="";\n'''+jarray('NAEPO_CENTER_X_V1133',centers)+jarray('NAEPO_HALF_W_V1133',widths)
s=s.replace(field_anchor,field_anchor+extra,1)

# Cache the high-resolution hole bitmap. onDraw intentionally refreshes often
# for the pulse animation, so repeated BitmapFactory decoding is wasteful.
a=s.find('        private Bitmap fullHoleBitmapV1102(){')
b=s.find('        private RectF fitCenterV1102(',a)
if a<0 or b<0: raise SystemExit('v1.13.3 bitmap method boundary missing')
cache_method=r'''        private Bitmap fullHoleBitmapV1102(){
            String n=fullHoleResourceV1102();if(n==null)return null;
            if(n.equals(cachedHoleNameV1133) && cachedHoleBitmapV1133!=null && !cachedHoleBitmapV1133.isRecycled())return cachedHoleBitmapV1133;
            int id=getResources().getIdentifier(n,"drawable",ctx.getPackageName());if(id==0)return null;
            try{
                Bitmap b=BitmapFactory.decodeResource(getResources(),id);
                cachedHoleNameV1133=n;cachedHoleBitmapV1133=b;return b;
            }catch(Exception e){return null;}
        }
'''
s=s[:a]+cache_method+s[b:]

# Naepo test mode accepts a wider GPS quality window for navigation as well as
# capture. Other courses keep the production gpsUsable() policy.
old='''        private boolean navEstimatedV1113(){
            return !previewMode && gpsUsable() && getRef("t",hole)!=null && greenCenterRef(hole)==null && verifiedMetersV190()>0;
        }'''
new='''        private boolean navGpsUsableV1133(){
            if(previewMode)return true;
            if(selected!=3)return gpsUsable();
            return location!=null && location.hasAccuracy() && location.getAccuracy()<=25f && fixAgeSec()<=15;
        }
        private boolean navEstimatedV1113(){
            return !previewMode && navGpsUsableV1133() && getRef("t",hole)!=null && greenCenterRef(hole)==null && verifiedMetersV190()>0;
        }'''
if old not in s: raise SystemExit('v1.13.3 nav estimated anchor missing')
s=s.replace(old,new,1)
s=s.replace('if(location==null || !gpsUsable())return -1f;','if(location==null || !navGpsUsableV1133())return -1f;',1)
s=s.replace('return previewMode || (gpsUsable() && getRef("t",hole)!=null && (greenCenterRef(hole)!=null || verifiedMetersV190()>0));','return previewMode || (navGpsUsableV1133() && getRef("t",hole)!=null && (greenCenterRef(hole)!=null || verifiedMetersV190()>0));',1)

# Helpers for the curved visual centerline + perpendicular GPS displacement.
marker='        private void drawFieldNavV1110(Canvas c,RectF stage,int totalM){'
pos=s.find(marker)
if pos<0: raise SystemExit('v1.13.3 field nav marker missing')
helpers=r'''        private float naepoCenterXV1133(float q){
            int ph=((hole-1)%9);float z=Math.max(0f,Math.min(1f,q))*(NAEPO_CENTER_X_V1133[ph].length-1);int i=(int)Math.floor(z);int j=Math.min(i+1,NAEPO_CENTER_X_V1133[ph].length-1);float f=z-i;return NAEPO_CENTER_X_V1133[ph][i]*(1f-f)+NAEPO_CENTER_X_V1133[ph][j]*f;
        }
        private float naepoHalfWV1133(float q){
            int ph=((hole-1)%9);float z=Math.max(0f,Math.min(1f,q))*(NAEPO_HALF_W_V1133[ph].length-1);int i=(int)Math.floor(z);int j=Math.min(i+1,NAEPO_HALF_W_V1133[ph].length-1);float f=z-i;return NAEPO_HALF_W_V1133[ph][i]*(1f-f)+NAEPO_HALF_W_V1133[ph][j]*f;
        }
        private float navCrossTrackMetersV1133(){
            if(previewMode)return simCrossTrackV1133;
            if(location==null)return 0f;GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t==null||g==null)return 0f;
            double lat0=Math.toRadians((t.lat+g.lat)*.5);double c=Math.cos(lat0);
            double gx=(g.lon-t.lon)*111320.0*c,gy=(g.lat-t.lat)*111111.0;
            double px=(location.getLongitude()-t.lon)*111320.0*c,py=(location.getLatitude()-t.lat)*111111.0;
            double len=Math.sqrt(gx*gx+gy*gy);if(len<1.0)return 0f;
            // Positive means golfer's right looking from tee toward green.
            return (float)((px*gy-py*gx)/len);
        }
        private RectF activeHoleImageRectV1133(RectF stage){
            Bitmap b=fullHoleBitmapV1102();if(b==null)return new RectF(stage);
            return fitCenterV1102(b,new RectF(stage.left+5,stage.top+5,stage.right-5,stage.bottom-5));
        }
'''
s=s[:pos]+helpers+s[pos:]

# Replace the simple center-column pin with a marker that follows the extracted
# real-hole corridor. Cross-track is applied only when TEE+GREEN are available;
# first-round TEE-only estimation stays on the centerline.
a=s.find('        private void drawFieldNavV1110(Canvas c,RectF stage,int totalM){')
b=s.find('        private String fieldReadyLabelV1114(){',a)
if a<0 or b<0: raise SystemExit('v1.13.3 field nav method boundary missing')
method=r'''        private void drawFieldNavV1110(Canvas c,RectF stage,int totalM){
            if(!navReadyV1110()){
                RectF wait=new RectF(stage.right-92,stage.top+7,stage.right-8,stage.top+27);box(c,wait,Color.argb(224,255,247,218),10);textFit(c,"TEE 저장",wait.left+8,wait.centerY()+3,wait.right-8,5.2f,AMBER,true);return;
            }
            float q=navProgressV1110();if(q<0)return;
            RectF img=activeHoleImageRectV1133(stage);
            float targetY=img.top+(.965f-.93f*q)*img.height();
            float targetX;
            if(selected==3){
                float cx=naepoCenterXV1133(q), hw=naepoHalfWV1133(q);targetX=img.left+cx*img.width();
                if(!navEstimatedV1113()){
                    float cross=navCrossTrackMetersV1133();float corridorM=currentPar()==3?30f:45f;float frac=Math.max(-1.15f,Math.min(1.15f,cross/corridorM));
                    targetX+=Math.max(9f,hw*img.width())*frac*.82f;
                }
            }else targetX=img.centerX();
            targetX=Math.max(img.left+8f,Math.min(img.right-8f,targetX));targetY=Math.max(img.top+10f,Math.min(img.bottom-10f,targetY));

            if(navSmoothHoleV1133!=hole || navSmoothVariantV1133!=variant || Float.isNaN(navSmoothXV1133)){
                navSmoothHoleV1133=hole;navSmoothVariantV1133=variant;navSmoothXV1133=targetX;navSmoothYV1133=targetY;
            }else{
                float acc=previewMode?6f:(location!=null?location.getAccuracy():25f);float alpha=acc<=8f?.18f:(acc<=15f?.12f:.08f);
                navSmoothXV1133+=alpha*(targetX-navSmoothXV1133);navSmoothYV1133+=alpha*(targetY-navSmoothYV1133);
            }
            float x=navSmoothXV1133,y=navSmoothYV1133;float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/250.0));
            float acc=previewMode?6f:(location!=null?Math.max(3f,location.getAccuracy()):25f);int quality=acc<=8?GREEN:(acc<=15?AMBER:CORAL);int orange=Color.rgb(255,132,35);
            float uncertainty=Math.max(18f,Math.min(34f,16f+acc*.58f));
            p.setColor(Color.argb((int)(25+35*pulse),Color.red(quality),Color.green(quality),Color.blue(quality)));c.drawCircle(x,y,uncertainty+4f*pulse,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.2f);p.setColor(Color.argb(145,Color.red(quality),Color.green(quality),Color.blue(quality)));c.drawCircle(x,y,uncertainty,p);
            p.setStrokeWidth(4f);p.setColor(Color.WHITE);c.drawCircle(x,y,15.5f,p);p.setStyle(Paint.Style.FILL);
            p.setColor(orange);c.drawCircle(x,y,11.5f,p);p.setColor(Color.rgb(255,240,218));c.drawCircle(x,y,3.2f,p);
        }

'''
s=s[:a]+method+s[b:]

# Slim active-green status: a colored dot + short label, not another large card.
old='''            if(selected==3){
                RectF ng=new RectF(stage.left+8,stage.top+7,stage.left+128,stage.top+31);
                int nc=naepoRedFlagV1132(hole)?Color.rgb(218,62,70):Color.rgb(241,184,32);
                box(c,ng,Color.argb(238,255,255,245),12);
                textFit(c,naepoRealMapLabelV1132(),ng.left+7,ng.centerY()+3,ng.right-7,5.8f,nc,true);
            }'''
new='''            if(selected==3){
                boolean red=naepoRedFlagV1132(hole);int nc=red?Color.rgb(218,62,70):Color.rgb(241,184,32);
                RectF ng=new RectF(stage.left+7,stage.top+6,stage.left+75,stage.top+26);box(c,ng,Color.argb(232,255,255,245),10);
                p.setColor(nc);c.drawCircle(ng.left+11,ng.centerY(),4.5f,p);textFit(c,red?"RED":"YELLOW",ng.left+20,ng.centerY()+3,ng.right-6,5.2f,nc,true);
            }'''
if old not in s: raise SystemExit('v1.13.3 active green chip anchor missing')
s=s.replace(old,new,1)

# Preview can now test both progress and lateral displacement with one tap.
old='''            if(screen==1 && previewMode && courseRect.contains(x,y)){
                float nt=courseRect.top+42f,nb=courseRect.bottom-30f;
                simProgressV1112=Math.max(0f,Math.min(1f,(nb-y)/Math.max(1f,nb-nt)));
                invalidate();return true;
            }'''
new='''            if(screen==1 && previewMode && courseRect.contains(x,y)){
                float nt=courseRect.top+42f,nb=courseRect.bottom-30f;simProgressV1112=Math.max(0f,Math.min(1f,(nb-y)/Math.max(1f,nb-nt)));
                simCrossTrackV1133=Math.max(-42f,Math.min(42f,(x-courseRect.centerX())/Math.max(1f,courseRect.width()*.36f)*35f));
                navSmoothXV1133=Float.NaN;navSmoothYV1133=Float.NaN;invalidate();return true;
            }'''
if old not in s: raise SystemExit('v1.13.3 preview touch anchor missing')
s=s.replace(old,new,1)

p.write_text(s)
print('applied V1.13.3 Naepo curved centerline + 2D cross-track GPS pin + uncertainty pulse + bitmap cache')
