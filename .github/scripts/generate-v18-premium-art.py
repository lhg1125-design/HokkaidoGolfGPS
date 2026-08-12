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
    ('kami','raw_kamishihoro.jpg',(34,122,72),(185,224,122)),
    ('furano','raw_furano.jpg',(43,102,82),(188,228,158)),
    ('sahoro','raw_sahoro.jpg',(37,95,75),(174,214,142)),
    ('naepo','raw_naepo.jpg',(44,112,70),(192,225,142)),
    ('royal','raw_royal.jpg',(32,104,88),(188,226,169)),
]

def fit_cover(src,size):
    sw,sh=src.size;tw,th=size
    scale=max(tw/sw,th/sh)
    nw,nh=max(1,round(sw*scale)),max(1,round(sh*scale))
    x=src.resize((nw,nh),Image.Resampling.LANCZOS)
    l=(nw-tw)//2;t=(nh-th)//2
    return x.crop((l,t,l+tw,t+th))

def fit_contain(src,size):
    sw,sh=src.size;tw,th=size
    scale=min(tw/sw,th/sh)
    nw,nh=max(1,round(sw*scale)),max(1,round(sh*scale))
    return src.resize((nw,nh),Image.Resampling.LANCZOS)

def rounded_mask(size,r):
    m=Image.new('L',size,0);d=ImageDraw.Draw(m)
    d.rounded_rectangle((0,0,size[0]-1,size[1]-1),radius=r,fill=255)
    return m

def premium(name,rawname,dark,light):
    path=RAW/rawname
    try:
        src=Image.open(path).convert('RGB')
        src=ImageEnhance.Color(src).enhance(1.15)
        src=ImageEnhance.Contrast(src).enhance(1.07)
        src=src.filter(ImageFilter.UnsharpMask(radius=2,percent=120,threshold=3))
        source_ok=True
    except Exception:
        src=base_fallback.copy()
        source_ok=False

    bg=fit_cover(src,(W,H)).filter(ImageFilter.GaussianBlur(18))
    tint=Image.new('RGBA',(W,H),(*dark,128))
    im=Image.blend(bg.convert('RGBA'),tint,0.30)

    # soft vertical light field
    glow=Image.new('RGBA',(W,H),(0,0,0,0));gd=ImageDraw.Draw(glow)
    for y in range(H):
        t=y/(H-1)
        a=int(60*(1-t)+12*t)
        gd.line((0,y,W,y),fill=(light[0],light[1],light[2],a))
    im=Image.alpha_composite(im,glow)

    # large glass card with high-resolution course image
    card=(72,90,W-72,H-90)
    sh=Image.new('RGBA',(W,H),(0,0,0,0));sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((card[0],card[1]+18,card[2],card[3]+18),radius=52,fill=(5,35,20,105))
    sh=sh.filter(ImageFilter.GaussianBlur(20));im=Image.alpha_composite(im,sh)

    art=fit_contain(src,(card[2]-card[0]-42,card[3]-card[1]-42))
    art_bg=Image.new('RGB',(card[2]-card[0],card[3]-card[1]),(236,244,232))
    ax=(art_bg.width-art.width)//2;ay=(art_bg.height-art.height)//2
    art_bg.paste(art,(ax,ay))
    art_bg=ImageEnhance.Sharpness(art_bg).enhance(1.08)
    mask=rounded_mask(art_bg.size,46)
    im.paste(art_bg,(card[0],card[1]),mask)

    # cinematic edge, contour glints and foreground haze -> animation-like still frame
    d=ImageDraw.Draw(im,'RGBA')
    d.rounded_rectangle(card,radius=52,outline=(255,255,255,105),width=3)
    for k in range(5):
        y=H*(.18+k*.14)
        amp=24+4*k
        pts=[]
        for x in range(-30,W+31,18):
            yy=y+math.sin((x/95)+(k*.9))*amp
            pts.append((x,yy))
        d.line(pts,fill=(255,255,255,20),width=2)
    d.ellipse((W*.72,H*.08,W*1.04,H*.38),fill=(255,255,255,22))
    d.ellipse((-W*.18,H*.72,W*.27,H*1.08),fill=(light[0],light[1],light[2],26))

    # tiny provenance chip shape (text is rendered by Android so no baked font mismatch)
    chip=(102,118,330,174)
    d.rounded_rectangle(chip,radius=28,fill=(255,255,255,205),outline=(255,255,255,235),width=2)
    d.ellipse((120,132,148,160),fill=(*light,255))

    out=ROOT/f'v18_course_{name}.webp'
    im.convert('RGB').save(out,'WEBP',quality=90,method=6)
    print(name,'source' if source_ok else 'fallback',out)

for x in specs: premium(*x)
print('generated v1.8 premium course-art pack')
