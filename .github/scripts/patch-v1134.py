from pathlib import Path
import base64
import numpy as np
from PIL import Image

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.13.3 · NAEPO 2D GEO PIN' not in s:
    raise SystemExit('v1.13.4 requires V1.13.3 Naepo 2D geo base')
s=s.replace('V1.13.3 · NAEPO 2D GEO PIN','V1.13.4 · JP/KR 2D GEO FULL FIT',1)

# -----------------------------------------------------------------------------
# Build one visual-corridor table for every logical JP/KR course/variant/hole.
# The source yardage images are already the real full-hole packs. We only
# analyze their drawn corridor so the live GPS pin follows each hole artwork.
# Images remain aspect-fit (contain), never center-cropped.
#
# IMPORTANT: tables are quantized to 8-bit and Base64-packed. Injecting the
# 180 x 41 x 2 values as Java float[][] literals makes the class initializer
# exceed the JVM 64KB method-code limit. 8-bit normalized geometry keeps map
# accuracy within a few pixels while making initialization tiny and lazy.
# -----------------------------------------------------------------------------
root=Path('app/src/main/res/drawable-nodpi')
SAMPLES=41
ROWS=5*2*18

def resource_name(course,variant,hole):
    hh=f'{hole:02d}'
    if course==0: return f'yardage_kamishihoro_{"c" if variant==0 else "m"}{hh}'
    if course==1: return f'yardage_furano_{"palmer" if variant==0 else "king"}{hh}'
    if course==2: return f'yardage_sahoro_{hh}'
    if course==3: return f'yardage_naepo_{((hole-1)%9)+1:02d}'
    if course==4: return f'yardage_royallinks_{"queens" if variant==0 else "kings"}{hh}'
    raise ValueError(course)

def resolve_image(name):
    for ext in ('.jpg','.jpeg','.png','.webp'):
        fp=root/(name+ext)
        if fp.exists(): return fp
    raise SystemExit(f'missing real hole image: {name}')

def corridor(fp):
    im=Image.open(fp).convert('RGB')
    a=np.asarray(im).astype(np.int16); h,w,_=a.shape
    ey=max(4,h//25); ex=max(4,w//12)
    corners=np.concatenate([
        a[:ey,:ex].reshape(-1,3),a[:ey,-ex:].reshape(-1,3),
        a[-ey:,:ex].reshape(-1,3),a[-ey:,-ex:].reshape(-1,3)])
    bg=np.median(corners,axis=0)
    diff=np.sqrt(((a-bg)**2).sum(axis=2))
    mx=a.max(axis=2); mn=a.min(axis=2); sat=mx-mn
    mask=(diff>36)&((sat>20)|(mx<216))
    cs=[]; ws=[]
    for i in range(SAMPLES):
        q=i/(SAMPLES-1)
        yf=.965-.93*q
        yy=int(round(yf*(h-1))); band=max(3,int(h*.012))
        y1=max(0,yy-band); y2=min(h,yy+band+1)
        ys,xs=np.where(mask[y1:y2])
        if len(xs)<12:
            band=max(band,int(h*.030)); y1=max(0,yy-band); y2=min(h,yy+band+1); ys,xs=np.where(mask[y1:y2])
        if len(xs)<8:
            c=.5; hw=.20
        else:
            lo=float(np.percentile(xs,6)); hi=float(np.percentile(xs,94))
            c=((lo+hi)*.5)/max(1,w-1); hw=max(.035,((hi-lo)*.5)/max(1,w-1))
        cs.append(c); ws.append(hw)
    for _ in range(2):
        cs=[cs[0]]+[float(np.median(cs[max(0,i-1):min(SAMPLES,i+2)])) for i in range(1,SAMPLES-1)]+[cs[-1]]
        ws=[ws[0]]+[float(np.median(ws[max(0,i-1):min(SAMPLES,i+2)])) for i in range(1,SAMPLES-1)]+[ws[-1]]
    return cs,ws

centers=[]; widths=[]; cache={}
for course in range(5):
    for variant in range(2):
        for hole in range(1,19):
            n=resource_name(course,variant,hole)
            if n not in cache: cache[n]=corridor(resolve_image(n))
            c,w=cache[n]; centers.append(c); widths.append(w)
if len(centers)!=ROWS or len(widths)!=ROWS:
    raise SystemExit(f'v1.13.4 geo row count mismatch: {len(centers)}/{len(widths)}')

def packed_b64(data):
    flat=[]
    for row in data:
        if len(row)!=SAMPLES: raise SystemExit('v1.13.4 geo sample count mismatch')
        flat.extend(max(0,min(255,int(round(float(v)*255.0)))) for v in row)
    raw=bytes(flat)
    if len(raw)!=ROWS*SAMPLES: raise SystemExit('v1.13.4 packed size mismatch')
    return base64.b64encode(raw).decode('ascii')

center_b64=packed_b64(centers)
width_b64=packed_b64(widths)

field_anchor='        private Bitmap cachedHoleBitmapV1133=null; private String cachedHoleNameV1133="";'
if field_anchor not in s: raise SystemExit('v1.13.4 field anchor missing')
extra=f'''\n        private static final String GEO_SCOPE_V1134="JP_KR_ALL_5_COURSES";\n        private static final int FULL_GEO_SAMPLES_V1134={SAMPLES};\n        private static final String FULL_CENTER_PACK_V1134="{center_b64}";\n        private static final String FULL_HALF_W_PACK_V1134="{width_b64}";\n        private byte[] fullCenterBytesV1134=null,fullHalfWBytesV1134=null;\n'''
s=s.replace(field_anchor,field_anchor+extra,1)

marker='        private float naepoCenterXV1133(float q){'
pos=s.find(marker)
if pos<0: raise SystemExit('v1.13.4 corridor helper anchor missing')
helpers=r'''        private int fullGeoRowV1134(){
            int cc=Math.max(0,Math.min(4,selected)),vv=Math.max(0,Math.min(1,variant)),hh=Math.max(1,Math.min(18,hole));
            return (cc*2+vv)*18+(hh-1);
        }
        private byte[] fullCenterBytesV1134(){
            if(fullCenterBytesV1134==null)fullCenterBytesV1134=android.util.Base64.decode(FULL_CENTER_PACK_V1134,android.util.Base64.NO_WRAP);
            return fullCenterBytesV1134;
        }
        private byte[] fullHalfWBytesV1134(){
            if(fullHalfWBytesV1134==null)fullHalfWBytesV1134=android.util.Base64.decode(FULL_HALF_W_PACK_V1134,android.util.Base64.NO_WRAP);
            return fullHalfWBytesV1134;
        }
        private float fullGeoSampleV1134(byte[] pack,int row,float q){
            float z=Math.max(0f,Math.min(1f,q))*(FULL_GEO_SAMPLES_V1134-1);int i=(int)Math.floor(z),j=Math.min(i+1,FULL_GEO_SAMPLES_V1134-1);float f=z-i;int base=row*FULL_GEO_SAMPLES_V1134;
            float a=(pack[base+i]&255)/255f,b=(pack[base+j]&255)/255f;return a*(1f-f)+b*f;
        }
        private float fullCenterXV1134(float q){return fullGeoSampleV1134(fullCenterBytesV1134(),fullGeoRowV1134(),q);}
        private float fullHalfWV1134(float q){return fullGeoSampleV1134(fullHalfWBytesV1134(),fullGeoRowV1134(),q);}
        private RectF fullFitImageRectV1134(RectF stage){
            Bitmap b=fullHoleBitmapV1102();if(b==null)return new RectF(stage);
            RectF safe=new RectF(stage.left+7f,stage.top+7f,stage.right-7f,stage.bottom-7f);
            return fitCenterV1102(b,safe);
        }
'''
s=s[:pos]+helpers+s[pos:]

old='''            RectF img=activeHoleImageRectV1133(stage);\n            float targetY=img.top+(.965f-.93f*q)*img.height();\n            float targetX;\n            if(selected==3){\n                float cx=naepoCenterXV1133(q), hw=naepoHalfWV1133(q);targetX=img.left+cx*img.width();\n                if(!navEstimatedV1113()){\n                    float cross=navCrossTrackMetersV1133();float corridorM=currentPar()==3?30f:45f;float frac=Math.max(-1.15f,Math.min(1.15f,cross/corridorM));\n                    targetX+=Math.max(9f,hw*img.width())*frac*.82f;\n                }\n            }else targetX=img.centerX();'''
new='''            RectF img=fullFitImageRectV1134(stage);\n            float targetY=img.top+(.965f-.93f*q)*img.height();\n            float cx=fullCenterXV1134(q),hw=fullHalfWV1134(q);\n            float targetX=img.left+cx*img.width();\n            if(!navEstimatedV1113() && getRef("t",hole)!=null && greenCenterRef(hole)!=null){\n                float cross=navCrossTrackMetersV1133();float corridorM=currentPar()==3?30f:45f;float frac=Math.max(-1.15f,Math.min(1.15f,cross/corridorM));\n                targetX+=Math.max(9f,hw*img.width())*frac*.82f;\n            }'''
if old not in s: raise SystemExit('v1.13.4 all-course nav branch anchor missing')
s=s.replace(old,new,1)

old='''            RectF dst=fitCenterV1102(b,new RectF(stage.left+5,stage.top+5,stage.right-5,stage.bottom-5));'''
new='''            RectF dst=fullFitImageRectV1134(stage);'''
if old not in s: raise SystemExit('v1.13.4 full-fit image anchor missing')
s=s.replace(old,new,1)

if ' · TEE → GREEN · ' in s:
    s=s.replace(' · TEE → GREEN · ',' · FULL FIT · ',1)
elif ' · FULL FIT · ' not in s:
    print('v1.13.4 footer label anchor changed; keeping current footer text')

p.write_text(s)
print('applied v1.13.4 JP/KR all-course real-hole 2D geo + packed full-fit renderer')
