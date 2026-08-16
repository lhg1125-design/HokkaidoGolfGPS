from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, random

# H1 FINE MATERIAL LOCK
# Geometry source = Royal Links official JPG only.
# No warp / no AI redraw / no object relocation. Appearance is baked here before APK.
RES=Path('app/src/main/res/drawable-nodpi')
files=sorted(RES.glob('yardage_royallinks_*.jpg'))
if len(files)!=36: raise SystemExit(f'expected 36 Royal Links raw images, got {len(files)}')

def exterior_neutral(rgb):
    r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
    hi=np.maximum(r,np.maximum(g,b)); lo=np.minimum(r,np.minimum(g,b))
    return (r>226)&(g>226)&(b>208)&((hi-lo)<58)

def flood_exterior(mask):
    h,w=mask.shape; seen=np.zeros((h,w),np.uint8); q=[]
    def add(y,x):
        if 0<=y<h and 0<=x<w and seen[y,x]==0 and mask[y,x]: seen[y,x]=1;q.append((y,x))
    for x in range(w): add(0,x);add(h-1,x)
    for y in range(h): add(y,0);add(y,w-1)
    i=0
    while i<len(q):
        y,x=q[i];i+=1
        add(y-1,x);add(y+1,x);add(y,x-1);add(y,x+1)
    return seen.astype(bool)

def morph(mask,mode,px):
    im=Image.fromarray((mask*255).astype('uint8'),'L');k=max(3,px//2*2+1)
    f=ImageFilter.MaxFilter(k) if mode=='expand' else ImageFilter.MinFilter(k)
    return np.asarray(im.filter(f))>0

def style(fp):
    im=Image.open(fp).convert('RGB'); src=np.asarray(im).copy().astype(np.int16);h,w=src.shape[:2]
    r,g,b=src[:,:,0],src[:,:,1],src[:,:,2]
    ext=flood_exterior(exterior_neutral(src)); inside=~ext

    # Conservative appearance masks. All masks retain source pixel coordinates.
    water=inside&(b>112)&((b-r)>16)&((b-g)>-15)
    sand=inside&(r>184)&(g>158)&(b<208)&((r-b)>8)
    fair=inside&(g>143)&((g-r)>32)&((g-b)>32)&(~water)&(~sand)
    rough=inside&(g>103)&((g-r)>17)&((g-b)>18)&(~fair)&(~water)&(~sand)
    fair=morph(fair,'expand',1)&inside&(~water)&(~sand)
    rough=rough&(~fair)&(~water)&(~sand)

    gray=(src[:,:,0]*.299+src[:,:,1]*.587+src[:,:,2]*.114).astype(np.float32);lum=gray/255.
    out=src.astype(np.float32).copy()
    # Palette sampled from the approved H1 fine-design screen.
    FM=np.array([122.,182.,39.]); TM=np.array([82.,122.,18.]); WM=np.array([7.,111.,181.])
    if fair.any():
        sh=lum-.58
        for c,a in enumerate([42.,52.,25.]):
            z=out[:,:,c];z[fair]=np.clip(FM[c]+sh[fair]*a,0,255);out[:,:,c]=z
    if rough.any():
        sh=lum-.46
        for c,a in enumerate([30.,42.,20.]):
            z=out[:,:,c];z[rough]=np.clip(TM[c]+sh[rough]*a,0,255);out[:,:,c]=z
    if water.any():
        sh=lum-.55
        for c,a in enumerate([16.,66.,78.]):
            z=out[:,:,c];z[water]=np.clip(WM[c]+sh[water]*a,0,255);out[:,:,c]=z
    if sand.any():
        inner=morph(sand,'contract',3);rim=sand&(~inner)
        out[inner]=np.array([248,241,216],np.float32);out[rim]=np.array([193,183,137],np.float32)

    base=Image.fromarray(np.clip(out,0,255).astype(np.uint8),'RGB').convert('RGBA')
    # H1-like individual 3D canopy language, strictly clipped to official rough mask.
    forest=Image.new('RGBA',(w,h),(0,0,0,0));fd=ImageDraw.Draw(forest,'RGBA')
    rnd=random.Random(sum((i+1)*ord(c) for i,c in enumerate(fp.name)))
    cols=[(33,109,39,238),(49,131,45,238),(70,148,49,238),(92,160,55,230)]
    for y in range(5,h-5,7):
        for x in range(5,w-5,7):
            if not rough[y,x] or rnd.random()>.57: continue
            rr=rnd.randint(4,8); col=cols[rnd.randrange(len(cols))]
            fd.ellipse((x-rr+2,y-rr+3,x+rr+2,y+rr+3),fill=(8,45,18,80))
            fd.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col)
            fd.ellipse((x-rr*.48,y-rr*.65,x+rr*.08,y-rr*.08),fill=(194,223,103,105))
            if rnd.random()<.35: fd.ellipse((x-2,y-rr*.32-2,x+2,y-rr*.32+2),fill=(190,205,65,145))
    fa=np.asarray(forest).copy();fa[:,:,3]=np.minimum(fa[:,:,3],(rough*255).astype(np.uint8))
    base.alpha_composite(Image.fromarray(fa,'RGBA'))

    # Fine water ripple texture, clipped to source water only.
    rip=Image.new('RGBA',(w,h),(0,0,0,0));rd=ImageDraw.Draw(rip,'RGBA');wy,wx=np.where(water)
    if wx.size:
        for yy in range(int(wy.min())+9,int(wy.max()),15):
            xs=np.flatnonzero(water[yy])
            if xs.size>10:
                l,r0=int(xs.min()),int(xs.max());rd.arc((l+2,yy-4,r0-2,yy+6),10,170,fill=(220,245,250,105),width=1)
    ra=np.asarray(rip).copy();ra[:,:,3]=np.minimum(ra[:,:,3],(water*255).astype(np.uint8));base.alpha_composite(Image.fromarray(ra,'RGBA'))

    result=np.asarray(base.convert('RGB')).copy()
    # Preserve official strategy line, cart path and dark outlines exactly.
    dark=inside&(src.mean(axis=2)<96);hi=src.max(axis=2);lo=src.min(axis=2)
    path=inside&((hi-lo)<48)&(gray>55)&(gray<205)&(~sand)
    result[dark]=src[dark].astype(np.uint8);result[path]=src[path].astype(np.uint8)

    alpha=np.where(ext,0,255).astype(np.uint8);rgba=np.dstack([result,alpha]);ys,xs=np.where(~ext)
    if xs.size==0: raise SystemExit(f'empty course after exterior mask: {fp}')
    pad=max(4,min(im.size)//110);l=max(0,int(xs.min())-pad);r0=min(im.width,int(xs.max())+pad+1);t=max(0,int(ys.min())-pad);b0=min(im.height,int(ys.max())+pad+1)
    outim=Image.fromarray(rgba,'RGBA').crop((l,t,r0,b0));dest=RES/('approved_'+fp.stem+'.webp');outim.save(dest,'WEBP',lossless=True,method=6)
    print(dest.name,'H1-FINE-MATERIAL',outim.size,'raw',im.size,'trim',(l,t,r0,b0))

for fp in files: style(fp)
print('ROYAL LINKS H1 FINE MATERIAL LOCK READY',len(files))
