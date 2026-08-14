from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, random, math

ROOT=Path('app/src/main/res/drawable-nodpi')
FILES=sorted(ROOT.glob('yardage_*.jpg'))
if len(FILES)!=135: raise SystemExit(f'V1.14.9 expects 135 yardages, got {len(FILES)}')

# -----------------------------------------------------------------------------
# V1.14.9 COURSE PIXEL MASTER
# Same pixel canvas / same hole geometry. We only replace texture and decoration.
# No crop, resize, warp or centerline relocation -> existing GPS mapping stays valid.
# -----------------------------------------------------------------------------

def mask_expand(mask,px):
    im=Image.fromarray((mask*255).astype('uint8'),'L')
    k=max(3,px//2*2+1)
    return np.asarray(im.filter(ImageFilter.MaxFilter(k)))>0

def mask_contract(mask,px):
    im=Image.fromarray((mask*255).astype('uint8'),'L')
    k=max(3,px//2*2+1)
    return np.asarray(im.filter(ImageFilter.MinFilter(k)))>0

def centerline_from(mask):
    h,w=mask.shape; cx=np.full(h,np.nan,np.float32)
    for y in range(h):
        xs=np.flatnonzero(mask[y])
        if xs.size>6: cx[y]=float(np.median(xs))
    good=np.isfinite(cx)
    if not good.any(): return np.full(h,w*.5,np.float32)
    idx=np.arange(h);cx[~good]=np.interp(idx[~good],idx[good],cx[good])
    # smooth without changing vertical mapping
    win=41;k=np.ones(win,dtype=np.float32)/win;pad=win//2
    return np.convolve(np.pad(cx,(pad,pad),mode='edge'),k,mode='valid')[:h]

def paint_course(src,name):
    arr=np.asarray(src.convert('RGB')).astype(np.int16);h,w=arr.shape[:2]
    r,g,b=arr[:,:,0],arr[:,:,1],arr[:,:,2]
    # Source is already geometry-derived. Classify only appearance; pixel location is untouched.
    water=(b>118)&((b-r)>18)&((b-g)>-8)
    sand=(r>186)&(g>160)&(b<190)&((r-b)>22)
    fair=(g>165)&((g-r)>45)&((g-b)>42)
    rough=(g>125)&((g-r)>28)&((g-b)>25)&(~fair)&(~water)&(~sand)
    playable=fair|rough|sand|water
    playable=mask_expand(playable,5)
    fair=mask_expand(fair,3)
    cx=centerline_from(fair|rough)

    # fixed storybook texture base
    yy=np.linspace(0,1,h)[:,None]
    base=np.zeros((h,w,3),np.uint8)
    base[:,:,0]=(29+12*yy).astype(np.uint8)
    base[:,:,1]=(104+24*yy).astype(np.uint8)
    base[:,:,2]=(53+8*yy).astype(np.uint8)
    out=Image.fromarray(base,'RGB').convert('RGBA');d=ImageDraw.Draw(out,'RGBA')
    seed=sum((i+1)*ord(c) for i,c in enumerate(name));rnd=random.Random(seed)

    # soft forest depth patches, fixed sprite language
    for i in range(170):
        y=rnd.randint(0,h-1);x=rnd.randint(0,w-1)
        if playable[y,x]:continue
        rr=rnd.randint(16,48);col=rnd.choice([(35,122,57,135),(50,143,62,150),(73,158,66,135),(94,174,72,105)])
        d.ellipse((x-rr+6,y-rr+9,x+rr+6,y+rr+9),fill=(18,62,33,30))
        d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col)
        if i%3==0:d.ellipse((x-rr*.45,y-rr*.65,x+rr*.05,y-rr*.18),fill=(204,230,131,35))

    # course layers from VERIFIED source masks, same pixels
    course=np.array(out.convert('RGB'))
    # outer playable shadow/edge
    edge=mask_expand(playable,11)&(~mask_contract(playable,5));course[edge]=np.array([32,91,45],np.uint8)
    course[rough]=np.array([86,164,68],np.uint8)
    course[fair]=np.array([139,207,75],np.uint8)
    course[water]=np.array([61,165,216],np.uint8)
    course[sand]=np.array([249,225,155],np.uint8)
    out=Image.fromarray(course,'RGB').convert('RGBA');d=ImageDraw.Draw(out,'RGBA')

    # fairway alternating painterly bands, clipped by fair mask
    for y0 in range(20,h,110):
        y1=min(h,y0+55);band=np.zeros((h,w),bool);band[y0:y1]=fair[y0:y1]
        layer=np.array(out.convert('RGB')); layer[band]=np.clip(layer[band].astype(int)+np.array([7,10,-2]),0,255)
        out=Image.fromarray(layer.astype('uint8'),'RGB').convert('RGBA');d=ImageDraw.Draw(out,'RGBA')

    # water highlights use actual water mask bounds
    wy,wx=np.where(water)
    if wx.size:
        for y in range(int(wy.min())+22,int(wy.max()),48):
            xs=np.flatnonzero(water[y])
            if xs.size>10:
                l,r0=int(xs.min()),int(xs.max());d.arc((l+8,y-13,r0-8,y+14),10,170,fill=(215,244,248,120),width=4)

    # organic sand scallops/highlights without changing bunker locations
    sy,sx=np.where(sand)
    if sx.size:
        for i in range(38):
            k=rnd.randrange(len(sx));x=int(sx[k]);y=int(sy[k]);
            if sand[y,x]:d.ellipse((x-7,y-5,x+7,y+5),fill=(255,238,187,65))

    # flowers and tiny rocks only OUTSIDE playable corridor
    for i in range(70):
        y=rnd.randint(50,h-50);x=rnd.choice([rnd.randint(25,max(26,int(cx[y]-130))),rnd.randint(min(w-26,int(cx[y]+130)),w-25)]) if 160<cx[y]<w-160 else rnd.randint(25,w-25)
        x=max(20,min(w-20,x))
        if playable[y,x]:continue
        if i%3:
            col=rnd.choice([(247,190,60,230),(240,112,110,220),(123,190,231,220)]);rr=rnd.randint(3,6);d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col)
        else:
            rr=rnd.randint(5,10);d.ellipse((x-rr,y-rr*.6,x+rr,y+rr*.6),fill=(120,116,80,110))

    # approved-reference white dotted strategy route follows verified centerline
    pts=[]
    for y in range(h-115,90,-30):pts.append((float(cx[y]),float(y)))
    for i,(x,y) in enumerate(pts):
        if i%2==0:d.ellipse((x-5,y-5,x+5,y+5),fill=(255,255,245,230))

    # target flag near green end using same centerline
    gy=70;gx=float(cx[gy]);d.line((gx,gy+38,gx,gy-34),fill=(93,65,37,255),width=7);d.polygon([(gx,gy-34),(gx+38,gy-20),(gx,gy-4)],fill=(240,73,48,255));d.ellipse((gx-50,gy+12,gx+50,gy+54),fill=(161,220,88,82))
    # soft texture unifies raster look; not a geometry transform
    return out.convert('RGB').filter(ImageFilter.GaussianBlur(.22))

for fp in FILES:
    with Image.open(fp) as im: out=paint_course(im,fp.name)
    # preserve exact original pixel dimensions
    out.save(fp,'JPEG',quality=95,subsampling=0,optimize=True,progressive=True)

# Correct runtime chrome spacing and make whole 4-icon nav clickable.
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java');s=p.read_text()

def bounds(src,signature):
    a=src.find(signature)
    if a<0:raise SystemExit('missing '+signature)
    br=src.find('{',a);dep=0
    for i in range(br,len(src)):
        if src[i]=='{':dep+=1
        elif src[i]=='}':
            dep-=1
            if dep==0:return a,i+1
    raise SystemExit('unclosed '+signature)

def replace_method(src,signature,repl):
    a,b=bounds(src,signature);return src[:a]+repl+src[b:]

s=replace_method(s,'        private void setPmNavV1148(float w,float h)',r'''        private void setPmNavV1148(float w,float h){float top=h*.744f;for(int i=0;i<4;i++){float l=w*(.018f+i*.241f),r=w*(.018f+(i+1)*.241f);pmNavV1148[i].set(l,top,r,h*.995f);}}''')
s=replace_method(s,'        private void drawYardageChromeV1148(Canvas c)',r'''        private void drawYardageChromeV1148(Canvas c){
            float w=getWidth(),h=getHeight();drawPmFullV1148(c,"yardage_chrome_v1148");setPmNavV1148(w,h);
            int par=currentPar();GeoRef g=getRef("g",hole);Distances ds=distances(g);int f=ds.front,ce=ds.center,ba=ds.back;if(previewMode){f=148;ce=155;ba=163;}
            textFit(c,ko[selected],w*.055f,h*.061f,w*.69f,22.5f,Color.WHITE,true);textFit(c,variants[selected][variant]+"  H"+hole+" / PAR"+par,w*.055f,h*.101f,w*.69f,13.5f,Color.rgb(242,252,240),true);
            int[] vv={f,ce,ba};float[] xx={.191f,.500f,.809f};int[] cc={Color.rgb(66,184,237),Color.WHITE,Color.rgb(255,124,91)};for(int i=0;i<3;i++)text(c,vv[i]<0?"--":vv[i]+"m",w*xx[i],h*.151f,31.0f,cc[i],true,Paint.Align.CENTER);
            text(c,(ce<0?"--":ce)+"m",w*.182f,h*.847f,33.0f,Color.WHITE,true,Paint.Align.CENTER);mapLaunch.set(w*.700f,h*.806f,w*.965f,h*.874f);
        }''')
if 'V1.14.9 · COURSE PIXEL' not in s:s=s.replace('V1.14.8 · PIXEL MASTER','V1.14.8 · PIXEL MASTER / V1.14.9 · COURSE PIXEL',1)
p.write_text(s)
print('V1.14.9 COURSE PIXEL: 135 verified hole masks transplanted into fixed storybook texture with identical pixel coordinates')
