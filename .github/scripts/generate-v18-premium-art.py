from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import math

W,H=1080,1180
ROOT=Path('app/src/main/res/drawable-nodpi')
RAW=Path('.github/tmp/v18')
ROOT.mkdir(parents=True,exist_ok=True)
RAW.mkdir(parents=True,exist_ok=True)

fallback_src=ROOT/'concept_course_exact.webp'
base_fallback=Image.open(fallback_src).convert('RGB') if fallback_src.exists() else Image.new('RGB',(W,H),(42,115,68))

specs=[
    ('kami','raw_kamishihoro.jpg',(22,90,55),(185,224,122)),
    ('furano','raw_furano.jpg',(22,82,63),(188,228,158)),
    ('sahoro','raw_sahoro.jpg',(22,75,58),(174,214,142)),
    ('naepo','raw_naepo.jpg',(25,88,54),(192,225,142)),
    ('royal','raw_royal.jpg',(20,82,68),(188,226,169)),
]

def fit_cover(src,size):
    sw,sh=src.size;tw,th=size
    scale=max(tw/sw,th/sh)
    nw,nh=max(1,round(sw*scale)),max(1,round(sh*scale))
    x=src.resize((nw,nh),Image.Resampling.LANCZOS)
    l=(nw-tw)//2;t=(nh-th)//2
    return x.crop((l,t,l+tw,t+th))

def premium(name,rawname,dark,light):
    path=RAW/rawname
    try:
        src=Image.open(path).convert('RGB')
        source_ok=True
    except Exception:
        src=base_fallback.copy();source_ok=False

    src=ImageEnhance.Color(src).enhance(1.12)
    src=ImageEnhance.Contrast(src).enhance(1.08)
    src=ImageEnhance.Sharpness(src).enhance(1.08)
    src=src.filter(ImageFilter.UnsharpMask(radius=1.6,percent=105,threshold=3))
    im=fit_cover(src,(W,H)).convert('RGBA')

    shade=Image.new('RGBA',(W,H),(0,0,0,0));sd=ImageDraw.Draw(shade)
    for y in range(H):
        t=y/(H-1)
        top=max(0.0,1.0-t/0.28)
        bottom=max(0.0,(t-0.72)/0.28)
        a=int(82*top+96*bottom)
        if a>0: sd.line((0,y,W,y),fill=(dark[0],dark[1],dark[2],a))
    im=Image.alpha_composite(im,shade)

    overlay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(overlay,'RGBA')
    d.rectangle((0,0,W,6),fill=(255,255,255,72))
    d.rectangle((0,H-7,W,H),fill=(5,36,22,70))
    d.ellipse((W*.70,-H*.10,W*1.08,H*.30),fill=(255,255,255,15))
    d.ellipse((-W*.18,H*.78,W*.30,H*1.10),fill=(light[0],light[1],light[2],15))

    for k in range(2):
        y=H*(.37+k*.30);pts=[]
        for x in range(-20,W+21,24):
            yy=y+math.sin((x/150)+(k*1.25))*18
            pts.append((x,yy))
        d.line(pts,fill=(255,255,255,10),width=2)
    im=Image.alpha_composite(im,overlay)

    out=ROOT/f'v18_course_{name}.webp'
    im.convert('RGB').save(out,'WEBP',quality=93,method=6)
    print(name,'source' if source_ok else 'fallback',src.size,'->',out)

for x in specs: premium(*x)
print('generated v1.8 immersive premium course-art pack')

# Final visual-only pass for all 135 full-hole yardage images. This module does
# not crop, resize or warp, so GPS geometry and corridor mapping stay unchanged.
import storybook_yardage_v1139
