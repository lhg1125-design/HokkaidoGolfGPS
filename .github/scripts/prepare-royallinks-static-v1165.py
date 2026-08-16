from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

RES=Path('app/src/main/res/drawable-nodpi')
files=sorted(RES.glob('yardage_royallinks_*.jpg'))
if len(files)!=36:
    raise SystemExit(f'expected 36 Royal Links raw images, got {len(files)}')

def exterior_neutral(rgb):
    r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
    hi=np.maximum(r,np.maximum(g,b)); lo=np.minimum(r,np.minimum(g,b))
    return (r>226)&(g>226)&(b>208)&((hi-lo)<58)

def flood_exterior(mask):
    h,w=mask.shape
    seen=np.zeros((h,w),np.uint8)
    q=[]
    def add(y,x):
        if 0<=y<h and 0<=x<w and seen[y,x]==0 and mask[y,x]:
            seen[y,x]=1; q.append((y,x))
    for x in range(w): add(0,x); add(h-1,x)
    for y in range(h): add(y,0); add(y,w-1)
    i=0
    while i<len(q):
        y,x=q[i]; i+=1
        add(y-1,x); add(y+1,x); add(y,x-1); add(y,x+1)
    return seen.astype(bool)

def style(fp):
    im=Image.open(fp).convert('RGB')
    arr=np.asarray(im).copy()
    ext=flood_exterior(exterior_neutral(arr))
    rgba=np.dstack([arr,np.where(ext,0,255).astype(np.uint8)])
    ys,xs=np.where(~ext)
    if xs.size==0: raise SystemExit(f'empty course after exterior mask: {fp}')
    pad=max(6,min(im.size)//90)
    l=max(0,int(xs.min())-pad); r=min(im.width,int(xs.max())+pad+1)
    t=max(0,int(ys.min())-pad); b=min(im.height,int(ys.max())+pad+1)
    out=Image.fromarray(rgba,'RGBA').crop((l,t,r,b))

    # Display styling is completed here, outside the APK. Geometry is never warped,
    # stretched or regenerated. Only color/contrast/sharpness are tuned.
    rgb=out.convert('RGB')
    rgb=ImageEnhance.Color(rgb).enhance(1.18)
    rgb=ImageEnhance.Contrast(rgb).enhance(1.06)
    rgb=ImageEnhance.Sharpness(rgb).enhance(1.12)
    rgb=rgb.filter(ImageFilter.GaussianBlur(0.18))
    alpha=out.getchannel('A')
    out=rgb.convert('RGBA'); out.putalpha(alpha)

    dest=RES/('approved_'+fp.stem+'.webp')
    out.save(dest,'WEBP',lossless=True,method=6)
    return dest,out.size,im.size,(l,t,r,b)

for fp in files:
    dest,size,raw,crop=style(fp)
    print(dest.name,'approved',size,'raw',raw,'exterior_trim',crop)

print('ROYAL LINKS STATIC COURSE ART READY',len(files))
