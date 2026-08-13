from pathlib import Path
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
# -----------------------------------------------------------------------------
root=Path('app/src/main/res/drawable-nodpi')
SAMPLES=41

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
            band=max(band,int(h*.030)); y1=max(0,yy-band);y2=min(h,yy+band+1);ys,xs=np.where(mask[y1:y2])
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

centers=[]; widths=[]
cache={}
for course in range(5):
    for variant in range(2):
        for hole in range(1,19):
            n=resource_name(course,variant,hole)
            if n not in cache: cache[n]=corridor(resolve_image(n))
            c,w=cache[n]; centers.append(c); widths.append(w)

def jarray(name,data):
    rows=['            {'+','.join(f'{v:.4f}f' for v in row)+'}' for row in data]
    return '        private static final float[][] '+name+'={\n'+',\n'.join(rows)+'\n        };\n'

field_anchor='        private Bitmap cachedHoleBitmapV1133=null; private String cachedHoleNameV1133="";'
if field_anchor not in s: raise SystemExit('v1.13.4 field anchor missing')
extra='''\n        private static final String GEO_SCOPE_V1134="JP_KR_ALL_5_COURSES";\n'''+jarray('FULL_CENTER_X_V1134',centers)+jarray('FULL_HALF_W_V1134',widths)
s=s.replace(field_anchor,field_anchor+extra,1)

# Helpers use the same logical ordering as the build-time table:
# course(0..4) -> variant(0..1) -> hole(1..18).
marker='        private float naepoCenterXV1133(float q){'
pos=s.find(marker)
if pos<0: raise SystemExit('v1.13.4 corridor helper anchor missing')
helpers=r'''        private int fullGeoRowV1134(){
            int cc=Math.max(0,Math.min(4,selected)),vv=Math.max(0,Math.min(1,variant)),hh=Math.max(1,Math.min(18,hole));
            return (cc*2+vv)*18+(hh-1);
        }
        private float fullCenterXV1134(float q){
            int row=fullGeoRowV1134();float z=Math.max(0f,Math.min(1f,q))*(FULL_CENTER_X_V1134[row].length-1);int i=(int)Math.floor(z);int j=Math.min(i+1,FULL_CENTER_X_V1134[row].length-1);float f=z-i;return FULL_CENTER_X_V1134[row][i]*(1f-f)+FULL_CENTER_X_V1134[row][j]*f;
        }
        private float fullHalfWV1134(float q){
            int row=fullGeoRowV1134();float z=Math.max(0f,Math.min(1f,q))*(FULL_HALF_W_V1134[row].length-1);int i=(int)Math.floor(z);int j=Math.min(i+1,FULL_HALF_W_V1134[row].length-1);float f=z-i;return FULL_HALF_W_V1134[row][i]*(1f-f)+FULL_HALF_W_V1134[row][j]*f;
        }
        private RectF fullFitImageRectV1134(RectF stage){
            Bitmap b=fullHoleBitmapV1102();if(b==null)return new RectF(stage);
            RectF safe=new RectF(stage.left+7f,stage.top+7f,stage.right-7f,stage.bottom-7f);
            return fitCenterV1102(b,safe);
        }
'''
s=s[:pos]+helpers+s[pos:]

# Replace the Naepo-only corridor branch with an all-course real-hole branch.
old='''            RectF img=activeHoleImageRectV1133(stage);\n            float targetY=img.top+(.965f-.93f*q)*img.height();\n            float targetX;\n            if(selected==3){\n                float cx=naepoCenterXV1133(q), hw=naepoHalfWV1133(q);targetX=img.left+cx*img.width();\n                if(!navEstimatedV1113()){\n                    float cross=navCrossTrackMetersV1133();float corridorM=currentPar()==3?30f:45f;float frac=Math.max(-1.15f,Math.min(1.15f,cross/corridorM));\n                    targetX+=Math.max(9f,hw*img.width())*frac*.82f;\n                }\n            }else targetX=img.centerX();'''
new='''            RectF img=fullFitImageRectV1134(stage);\n            float targetY=img.top+(.965f-.93f*q)*img.height();\n            float cx=fullCenterXV1134(q),hw=fullHalfWV1134(q);\n            float targetX=img.left+cx*img.width();\n            if(!navEstimatedV1113() && getRef("t",hole)!=null && greenCenterRef(hole)!=null){\n                float cross=navCrossTrackMetersV1133();float corridorM=currentPar()==3?30f:45f;float frac=Math.max(-1.15f,Math.min(1.15f,cross/corridorM));\n                targetX+=Math.max(9f,hw*img.width())*frac*.82f;\n            }'''
if old not in s: raise SystemExit('v1.13.4 all-course nav branch anchor missing')
s=s.replace(old,new,1)

# Make the full-hole renderer use the exact same safe contain rectangle as the
# live marker. This prevents visual disagreement and guarantees no bitmap crop.
old='''            RectF dst=fitCenterV1102(b,new RectF(stage.left+5,stage.top+5,stage.right-5,stage.bottom-5));'''
new='''            RectF dst=fullFitImageRectV1134(stage);'''
if old not in s: raise SystemExit('v1.13.4 full-fit image anchor missing')
s=s.replace(old,new,1)

# Footer text is cosmetic. Earlier layout patches may have already changed its
# wording, so never fail the functional geo/full-fit build just for this label.
if ' · TEE → GREEN · ' in s:
    s=s.replace(' · TEE → GREEN · ',' · FULL FIT · ',1)
elif ' · FULL FIT · ' not in s:
    print('v1.13.4 footer label anchor changed; keeping current footer text')

p.write_text(s)
print('applied v1.13.4 JP/KR all-course real-hole 2D geo + full-fit renderer')
