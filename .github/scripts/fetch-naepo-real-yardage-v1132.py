from pathlib import Path
from io import BytesIO
import requests
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT=Path('.')
DATA=ROOT/'.github/data/naepo-real-yardage-v1132.tsv'
RES=ROOT/'app/src/main/res/drawable-nodpi'
TMP=ROOT/'.github/tmp/v1132-naepo'
RES.mkdir(parents=True,exist_ok=True); TMP.mkdir(parents=True,exist_ok=True)

UA='Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 Chrome/143.0.0.0 Mobile Safari/537.36'
s=requests.Session();s.headers.update({'User-Agent':UA,'Referer':'https://m.blog.naver.com/jc_song/224012917731'})

rows=[]
for line in DATA.read_text().splitlines():
    if not line.strip(): continue
    hole_s,url=line.split('\t',1);rows.append((int(hole_s),url.strip()))
if [h for h,_ in rows] != list(range(1,10)):
    raise SystemExit('Naepo source manifest must contain holes 1..9 exactly once')

def map_crop(im:Image.Image)->Image.Image:
    im=im.convert('RGB');a=np.asarray(im).astype(np.int16);h,w,_=a.shape
    # The published sheet places the real hole diagram on the right ~40%.
    # Restrict the detector to that zone so title/distance/pro-tip text can
    # never become part of the in-app yardage image.
    x0=int(w*.60);b=a[:,x0:,:]
    mx=b.max(axis=2)
    g=(b[:,:,1]>b[:,:,0]*1.03)&(b[:,:,1]>b[:,:,2]*1.02)&(b[:,:,1]>55)
    blue=(b[:,:,2]>b[:,:,0]*1.04)&(b[:,:,2]>b[:,:,1]*.92)&(b[:,:,2]>70)
    red=(b[:,:,0]>120)&(b[:,:,0]>b[:,:,1]*1.13)
    mask=(g|blue|red)&(mx<250)
    cols=mask.sum(axis=0);rws=mask.sum(axis=1)
    xs=np.where(cols>max(2,h*.018))[0];ys=np.where(rws>max(2,(w-x0)*.015))[0]
    if len(xs)==0 or len(ys)==0:
        raise ValueError('course-map detector found no colored course component')
    x1=x0+int(xs.min());x2=x0+int(xs.max())+1;y1=int(ys.min());y2=int(ys.max())+1
    m=9
    x1=max(0,x1-m);x2=min(w,x2+m);y1=max(0,y1-m);y2=min(h,y2+m)
    if (x2-x1)<100 or (y2-y1)<260:
        raise ValueError(f'detected crop too small: {(x1,y1,x2,y2)}')
    return im.crop((x1,y1,x2,y2))

proof=[]
for hole,url in rows:
    r=s.get(url,timeout=25);r.raise_for_status()
    if len(r.content)<15000: raise SystemExit(f'H{hole} source unexpectedly small: {len(r.content)}')
    src=Image.open(BytesIO(r.content)).convert('RGB')
    (TMP/f'naepo_h{hole:02d}_source.jpg').write_bytes(b'')
    src.save(TMP/f'naepo_h{hole:02d}_source.jpg','JPEG',quality=96,subsampling=0)
    crop=map_crop(src)
    # Keep the full geometry, but give the stylizer enough pixels to work with.
    if crop.height<1200:
        scale=1200/crop.height
        crop=crop.resize((round(crop.width*scale),1200),Image.Resampling.LANCZOS)
    dst=RES/f'yardage_naepo_{hole:02d}.jpg'
    crop.save(dst,'JPEG',quality=97,subsampling=0,optimize=True)
    proof.append((hole,src,crop))
    print('NAEPO REAL',hole,src.size,'->',crop.size,dst)

# Visual gate/provenance proof: left = published sheet, right = extracted real map.
font=ImageFont.load_default();tw,th=650,400
sheet=Image.new('RGB',(tw*2,th*9),(248,249,241));d=ImageDraw.Draw(sheet)
for row,(hole,src,crop) in enumerate(proof):
    a=src.copy();a.thumbnail((tw-28,th-42),Image.Resampling.LANCZOS)
    b=crop.copy();b.thumbnail((tw-28,th-42),Image.Resampling.LANCZOS)
    y=row*th
    sheet.paste(a,(14,y+28+(th-42-a.height)//2));sheet.paste(b,(tw+14,y+28+(th-42-b.height)//2))
    d.text((14,y+8),f'H{hole} PUBLISHED YARDAGE SHEET',fill=(28,82,48),font=font)
    d.text((tw+14,y+8),f'H{hole} REAL MAP CROP',fill=(28,82,48),font=font)
sheet.save(TMP/'naepo-real-9hole-proof.jpg','JPEG',quality=94)

assets=sorted(RES.glob('yardage_naepo_*.jpg'))
if len(assets)!=9:raise SystemExit(f'expected 9 Naepo real maps, got {len(assets)}')
print('Naepo real yardage assets present:',len(assets))
