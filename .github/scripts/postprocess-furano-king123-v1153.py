from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np, base64, io, math

# V1.15.3 Furano KING H1-H3 review lock
# - H1 keeps the field-verified KING H1 geometry.
# - H2/H3 are reconstructed ONLY from exact user-approved 408_2.webp / 408_3.webp bytes.
# - No geometry warp, rotation, crop distortion, hazard relocation or object redraw.
# - Only palette/contrast is normalized to the approved H1 storybook master.
# - Fixed safe rectangles guarantee zero overlap with wood HUD / bottom navigation.

RES=Path('app/src/main/res/drawable-nodpi')
ASSET=Path('.github/assets/furano-v1152')
W,H=941,1672
SAFE={1:(267,365,673,1422),2:(302,365,638,1422),3:(339,365,601,1422)}
PAR={1:4,2:3,3:4}
JUA='/tmp/Jua-Regular.ttf';MPLUS='/tmp/MPLUSRounded1c-ExtraBold.ttf'

def font(sz,jp=False): return ImageFont.truetype(MPLUS if jp else JUA,sz)
def text(d,xy,s,sz,fill,anchor='mm',stroke=0,stroke_fill=(10,20,16,255),jp=False):
    d.text(xy,s,font=font(sz,jp),fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=stroke_fill)

def exact_h2():
    raw=base64.b64decode(''.join((ASSET/f'king02.part{i}').read_text().strip() for i in (1,2,3,4)),validate=True)
    im=Image.open(io.BytesIO(raw)).convert('RGBA')
    if im.size!=(127,400): raise SystemExit(f'H2 source size changed: {im.size}')
    return im

def exact_h3():
    raw=base64.b64decode((ASSET/'king03.b64').read_text().strip(),validate=True)
    im=Image.open(io.BytesIO(raw)).convert('RGBA')
    if im.size!=(99,400): raise SystemExit(f'H3 source size changed: {im.size}')
    return im

def isolate_h1():
    fp=RES/'yardage_furano_king01.jpg'
    im=Image.open(fp).convert('RGB');a=np.array(im)
    mx=a.max(2);mn=a.min(2);sat=mx-mn
    bg=(a[:,:,0]>230)&(a[:,:,1]>230)&(a[:,:,2]>216)&(sat<48)
    hh,ww=bg.shape;seen=np.zeros(bg.shape,np.uint8);stack=[]
    for x in range(ww):
        if bg[0,x]:stack.append((0,x))
        if bg[hh-1,x]:stack.append((hh-1,x))
    for y in range(hh):
        if bg[y,0]:stack.append((y,0))
        if bg[y,ww-1]:stack.append((y,ww-1))
    while stack:
        y,x=stack.pop()
        if x<0 or x>=ww or y<0 or y>=hh or seen[y,x] or not bg[y,x]:continue
        seen[y,x]=1;stack.extend(((y-1,x),(y+1,x),(y,x-1),(y,x+1)))
    alpha=np.where(seen,0,255).astype(np.uint8)
    out=Image.fromarray(np.dstack([a,alpha]),'RGBA');box=out.getchannel('A').getbbox()
    if not box:raise SystemExit('H1 alpha-tight crop failed')
    return out.crop(box)

def alpha_tight(im):
    im=im.convert('RGBA');box=im.getchannel('A').getbbox()
    if not box:raise SystemExit('empty approved course image')
    return im.crop(box)

def clean_header(base,hole,par):
    # Rebuild header only; match approved master spacing and avoid arrow/car collision.
    d=ImageDraw.Draw(base,'RGBA')
    for y in range(0,156):
        t=y/155.0;col=(int(8+5*t),int(52+47*t),int(143+58*t),255);d.line((0,y,W,y),fill=col,width=1)
    # back arrow lives completely above the car glyph
    d.line((66,33,39,56),fill='white',width=8);d.line((39,56,66,79),fill='white',width=8);d.line((40,56,87,56),fill='white',width=8)
    text(d,(97,57),'후라노 골프코스',38,(255,255,255,255),anchor='lm',stroke=2,stroke_fill=(0,42,110,180))
    d.rounded_rectangle((39,103,78,129),radius=7,outline=(255,255,255,255),width=4)
    d.line((47,103,54,93),fill='white',width=4);d.line((54,93,72,93),fill='white',width=4);d.line((72,93,78,103),fill='white',width=4)
    d.ellipse((45,125,53,133),fill='white');d.ellipse((67,125,75,133),fill='white')
    text(d,(95,119),f'KING · H{hole} · PAR {par}',27,(255,255,255,255),anchor='lm',stroke=1,stroke_fill=(0,42,110,170),jp=True)
    sx,sy=780,45;d.ellipse((sx-15,sy-15,sx+15,sy+15),fill=(255,196,20,255))
    for ang in range(0,360,45):
        r=27;x0=sx+math.cos(math.radians(ang))*20;y0=sy+math.sin(math.radians(ang))*20;x1=sx+math.cos(math.radians(ang))*r;y1=sy+math.sin(math.radians(ang))*r
        d.line((x0,y0,x1,y1),fill=(255,196,20,255),width=4)
    d.ellipse((742,44,786,79),fill=(255,255,247,255));d.ellipse((768,35,811,80),fill=(255,255,247,255));d.ellipse((793,49,825,79),fill=(255,255,247,255));d.rounded_rectangle((744,59,825,81),radius=11,fill=(255,255,247,255))
    text(d,(842,59),'22°C',31,(255,255,255,255),anchor='lm',stroke=2,stroke_fill=(0,42,110,170),jp=True)

def cream_row(y):
    if y<350:return (247,239,214,255)
    t=max(0,min(1,(y-350)/(1458-350)));a=np.array([247,239,214],float);b=np.array([234,220,184],float);c=(a*(1-t)+b*t).astype(np.uint8)
    return tuple(c.tolist())+(255,)

def clear_course_window(base):
    d=ImageDraw.Draw(base,'RGBA')
    for y in range(350,1458):d.line((238,y,700,y),fill=cream_row(y),width=1)

def preserve_geometry_tone(im,hole):
    # Pixel positions and alpha are untouched. This is a color-only transform.
    im=alpha_tight(im);a=np.array(im.convert('RGBA'));rgb=a[:,:,:3].astype(np.float32);alpha=a[:,:,3]
    body=alpha>8;hh,ww=body.shape
    out=rgb.copy()
    # Find each row's exact opaque bounds; use only edge depth to identify perimeter foliage.
    edge_zone=np.zeros(body.shape,bool)
    for y in range(hh):
        xs=np.flatnonzero(body[y])
        if xs.size<2:continue
        lo,hi=int(xs.min()),int(xs.max());span=max(1,hi-lo+1);depth=max(3,int(span*.22))
        edge_zone[y,lo:min(hi+1,lo+depth)]=True;edge_zone[y,max(lo,hi-depth+1):hi+1]=True
    R,G,B=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];mx=rgb.max(2);mn=rgb.min(2);sat=mx-mn
    sand=body&(R>178)&(G>165)&(B>145)&(sat<115)
    path=body&(sat<52)&(mx>70)&(mx<235)
    foliage=body&edge_zone&(G>R*.98)&(G>B*1.08)&(sat>28)&~sand&~path
    grass=body&~foliage&~sand&~path
    # Master-like foliage: deeper green base, retain original leaf luminance/detail.
    lum=(R*.30+G*.59+B*.11);t=np.clip((lum-35)/190,0,1)
    forest=np.stack([18+52*t,72+103*t,22+35*t],axis=2)
    out[foliage]=rgb[foliage]*.28+forest[foliage]*.72
    # Master-like turf: brighter center, slightly warmer dark rough. Original shading is retained.
    bright=grass&(mx>120)
    rough=grass&~bright
    tg=np.clip((mx-45)/190,0,1)
    fair=np.stack([74+76*tg,156+69*tg,42+36*tg],axis=2)
    roug=np.stack([45+48*tg,120+70*tg,37+28*tg],axis=2)
    out[bright]=rgb[bright]*.48+fair[bright]*.52
    out[rough]=rgb[rough]*.55+roug[rough]*.45
    out[sand]=rgb[sand]*.30+np.array([246,223,177],dtype=np.float32)*.70
    out[path]=rgb[path]*.68+np.array([202,207,190],dtype=np.float32)*.32
    out=np.clip(out,0,255).astype(np.uint8)
    tuned=Image.fromarray(np.dstack([out,alpha]),'RGBA')
    tuned=ImageEnhance.Contrast(tuned).enhance(1.035)
    tuned=ImageEnhance.Sharpness(tuned).enhance(1.08)
    tuned.putalpha(Image.fromarray(alpha))
    return tuned

def paste_course(base,im,hole):
    x0,y0,x1,y1=SAFE[hole];sw=x1-x0;sh=y1-y0;im=preserve_geometry_tone(im,hole)
    scale=min(sw/im.width,sh/im.height);nw=max(1,round(im.width*scale));nh=max(1,round(im.height*scale));im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    x=x0+(sw-nw)//2;y=y0+(sh-nh)//2
    buf=Image.new('RGBA',(sw,sh),(0,0,0,0));shadow=Image.new('RGBA',im.size,(0,0,0,0));shadow.putalpha(im.getchannel('A').filter(ImageFilter.GaussianBlur(5)).point(lambda v:int(v*.18)))
    buf.alpha_composite(shadow,(x-x0+4,y-y0+6));buf.alpha_composite(im,(x-x0,y-y0));base.alpha_composite(buf,(x0,y0))
    return (x,y,nw,nh)

sources={1:isolate_h1(),2:exact_h2(),3:exact_h3()}
for hole in (1,2,3):
    fp=RES/f'furano_king_h{hole}_base_v1152.webp'
    if not fp.exists():raise SystemExit(f'missing generated base {fp}')
    base=Image.open(fp).convert('RGBA')
    if base.size!=(W,H):raise SystemExit(f'base canvas changed: {fp} {base.size}')
    clean_header(base,hole,PAR[hole]);clear_course_window(base);box=paste_course(base,sources[hole],hole)
    base.save(fp,'WEBP',lossless=True,method=6)
    print('V1153 FIX',hole,'safe',SAFE[hole],'placed',box,'source',sources[hole].size,'out',fp)

(RES/'furano_king123_v1153.lock').write_text('FURANO KING H1-H3 REVIEW LOCK\nH2=exact 408_2.webp\nH3=exact 408_3.webp\ngeometry unchanged; tone only\nstrict safe clip + clean header\n')
