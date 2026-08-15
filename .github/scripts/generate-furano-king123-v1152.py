from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, base64, io, random

ASSET=Path('.github/assets/furano-v1152')
RES=Path('app/src/main/res/drawable-nodpi')
RES.mkdir(parents=True,exist_ok=True)
SRC={h:RES/f'yardage_furano_king{h:02d}.jpg' for h in (1,2,3)}
for fp in list(SRC.values())+[ASSET/'header.b64',ASSET/'nav.b64']:
    if not fp.exists(): raise SystemExit(f'V1.15.2 missing source {fp}')

def b64_image(path):
    raw=base64.b64decode(Path(path).read_text().strip());return Image.open(io.BytesIO(raw)).convert('RGBA')
HEADER_SOURCE=b64_image(ASSET/'header.b64'); NAV_SOURCE=b64_image(ASSET/'nav.b64')
W,H=941,1672
if HEADER_SOURCE.size!=(941,156) or NAV_SOURCE.size!=(905,194): raise SystemExit('V1.15.2 approved chrome dimensions changed')
JUA='/tmp/Jua-Regular.ttf'; MPLUS='/tmp/MPLUSRounded1c-ExtraBold.ttf'
def F(sz,jp=False): return ImageFont.truetype(MPLUS if jp else JUA,sz)
def txt(d,xy,s,sz,fill,anchor='mm',stroke=0,sf=(15,15,10,255),jp=False):
    d.text(xy,s,font=F(sz,jp),fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=sf)

def isolate_course(src):
    # Keep exact Prince course pixels. Only make the neutral page exterior transparent.
    im=Image.open(src).convert('RGB'); a=np.array(im)
    mx=a.max(2);mn=a.min(2);sat=mx-mn
    bg=(a[:,:,0]>233)&(a[:,:,1]>233)&(a[:,:,2]>222)&(sat<44)
    # Edge-connected background only: preserve white bunkers and labels inside the course.
    seen=np.zeros(bg.shape,np.uint8); stack=[]; hh,ww=bg.shape
    for x in range(ww):
        if bg[0,x]: stack.append((0,x))
        if bg[hh-1,x]: stack.append((hh-1,x))
    for y in range(hh):
        if bg[y,0]: stack.append((y,0))
        if bg[y,ww-1]: stack.append((y,ww-1))
    while stack:
        y,x=stack.pop()
        if y<0 or y>=hh or x<0 or x>=ww or seen[y,x] or not bg[y,x]: continue
        seen[y,x]=1;stack.extend(((y-1,x),(y+1,x),(y,x-1),(y,x+1)))
    alpha=np.where(seen==1,0,255).astype(np.uint8)
    return Image.fromarray(np.dstack([a,alpha]),'RGBA')

course={h:isolate_course(SRC[h]) for h in (1,2,3)}

# Approved H1 header slice: remove old hole label only and overlay exact KING/H/PAR values.
HEADER=HEADER_SOURCE.copy(); ha=np.array(HEADER.convert('RGBA')); hsrc=np.array(HEADER_SOURCE.convert('RGB'))
for y in range(84,151):
    col=np.median(hsrc[y,520:700],axis=0).astype(np.uint8);ha[y,78:505,:3]=col;ha[y,78:505,3]=255
HEADER=Image.fromarray(ha,'RGBA');HEADER.alpha_composite(HEADER_SOURCE.crop((25,87,100,150)),(25,87))

# Approved wood grammar recreated without touching course pixels.
def make_wood():
    w,h=905,194;im=Image.new('RGBA',(w,h),(0,0,0,0))
    sh=Image.new('RGBA',(w,h),(0,0,0,0));sd=ImageDraw.Draw(sh);sd.rounded_rectangle((5,11,w-5,h-3),radius=26,fill=(25,14,7,120));sh=sh.filter(ImageFilter.GaussianBlur(8));im.alpha_composite(sh)
    d=ImageDraw.Draw(im,'RGBA')
    for y in range(5,h-13):
        t=(y-5)/(h-18);c=(int(139-41*t),int(82-31*t),int(34-17*t),255);d.line((5,y,w-5,y),fill=c,width=1)
    d.rounded_rectangle((5,5,w-5,h-13),radius=25,outline=(70,38,16,255),width=4);d.arc((9,8,w-9,80),188,352,fill=(255,205,130,72),width=4)
    rnd=random.Random(1152)
    for k in range(11):
        y=23+k*13+rnd.randint(-3,3);pts=[(x,y+rnd.randint(-3,3)) for x in range(20,w-20,40)];d.line(pts,fill=(220,154,87,44),width=2)
    for x in (299,600):d.line((x,14,x,h-28),fill=(47,26,12,150),width=3);d.line((x+3,14,x+3,h-28),fill=(210,143,74,40),width=1)
    for cx,cy,flip in [(20,19,1),(878,19,-1),(20,154,1),(878,154,-1)]:
        for j in range(4):
            ox=(j%2)*12*flip;oy=(j//2)*12;d.ellipse((cx+ox-8,cy+oy-5,cx+ox+9,cy+oy+8),fill=(67+10*j,145+8*j,24,255),outline=(24,77,12,255),width=2);d.line((cx+ox-5*flip,cy+oy+1,cx+ox+6*flip,cy+oy-1),fill=(190,225,75,150),width=1)
    return im
WOOD=make_wood()

NAV=NAV_SOURCE.copy();nw,nh=NAV.size
na=Image.new('L',(nw,nh),0);ImageDraw.Draw(na).rounded_rectangle((1,1,nw-2,nh-2),radius=50,fill=255)
sh=Image.new('L',(nw,nh),0);ImageDraw.Draw(sh).rounded_rectangle((4,6,nw-4,nh-1),radius=50,fill=90);sh=sh.filter(ImageFilter.GaussianBlur(7))
NAV.putalpha(Image.fromarray(np.maximum(np.array(na),np.array(sh)).astype(np.uint8)))

PANEL=Image.new('RGBA',(220,843),(0,0,0,0));pd=ImageDraw.Draw(PANEL,'RGBA')
psh=Image.new('RGBA',PANEL.size,(0,0,0,0));ImageDraw.Draw(psh).rounded_rectangle((7,9,217,840),radius=28,fill=(0,0,0,72));psh=psh.filter(ImageFilter.GaussianBlur(7));PANEL.alpha_composite(psh)
pd.rounded_rectangle((1,1,208,833),radius=28,fill=(13,84,15,255),outline=(8,48,7,255),width=4)
for yy in range(12,824):
    t=(yy-12)/(824-12);pd.line((12,yy,201,yy),fill=(18-int(6*t),98-int(16*t),19-int(5*t),255),width=1)
pd.rounded_rectangle((5,5,204,829),radius=25,outline=(77,145,31,255),width=3)
for yy in [220,370,520,670]: pd.line((25,yy,190,yy),fill=(130,175,70,150),width=1)

def background():
    a=np.zeros((H,W,4),np.uint8)
    for y in range(H):
        if y<350: col=np.array([247,239,214])
        elif y<1458:
            t=(y-350)/(1458-350);col=np.array([247,239,214])*(1-t)+np.array([234,220,184])*t
        else: col=np.array([237,223,188])
        a[y,:,:3]=col.astype(np.uint8);a[y,:,3]=255
    return Image.fromarray(a,'RGBA')

def target(base):
    d=ImageDraw.Draw(base,'RGBA');x0,y0,x1,y1=638,1261,908,1388
    sh=Image.new('RGBA',base.size,(0,0,0,0));ImageDraw.Draw(sh).rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=48,fill=(55,34,15,75));sh=sh.filter(ImageFilter.GaussianBlur(7));base.alpha_composite(sh)
    d.rounded_rectangle((x0,y0,x1,y1),radius=48,fill=(246,216,166,255),outline=(142,94,48,255),width=3);d.arc((x0+8,y0+5,x1-8,y0+92),190,350,fill=(255,255,255,80),width=4)
    cx,cy=703,1324;d.ellipse((cx-22,cy-22,cx+22,cy+22),outline=(20,20,15,255),width=5);d.ellipse((cx-7,cy-7,cx+7,cy+7),outline=(20,20,15,255),width=5);d.line((cx-34,cy,cx-20,cy),fill=(20,20,15,255),width=5);d.line((cx+20,cy,cx+34,cy),fill=(20,20,15,255),width=5);d.line((cx,cy-34,cx,cy-20),fill=(20,20,15,255),width=5);d.line((cx,cy+20,cx,cy+34),fill=(20,20,15,255),width=5);txt(d,(804,1324),'타겟',34,(25,23,17,255))

def bubble(base):
    d=ImageDraw.Draw(base,'RGBA');x0,y0,x1,y1=714,397,918,575
    sh=Image.new('RGBA',base.size,(0,0,0,0));ImageDraw.Draw(sh).rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=28,fill=(0,0,0,70));sh=sh.filter(ImageFilter.GaussianBlur(7));base.alpha_composite(sh);d.rounded_rectangle((x0,y0,x1,y1),radius=28,fill=(255,248,224,255),outline=(34,31,24,255),width=3);d.polygon([(x0+6,y1-48),(x0-20,y1),(x0+38,y1-24)],fill=(255,248,224,255),outline=(34,31,24,255));txt(d,(816,432),'남은 거리',25,(31,30,24,255));d.line((752,520,880,520),fill=(194,156,95,255),width=2);txt(d,(816,548),'핀까지',23,(31,30,24,255))

SAFE=(260,365,680,1422)
def contain(im):
    x0,y0,x1,y1=SAFE;sc=min((x1-x0)/im.width,(y1-y0)/im.height);ww=im.width*sc;hh=im.height*sc
    return x0+(x1-x0-ww)/2,y0+(y1-y0-hh)/2,ww,hh

def wood_text(base,vals):
    base.alpha_composite(WOOD,(18,156));d=ImageDraw.Draw(base)
    for cx,val,col,lab in zip([166,470,775],vals,[(30,145,255,255),(255,255,255,255),(255,80,72,255)],['FRONT','CENTER','BACK']):
        fn=F(70,True);fm=F(28,True);fl=F(27,True);ss=str(val);nw=d.textbbox((0,0),ss,font=fn,stroke_width=5)[2];mw=d.textbbox((0,0),'m',font=fm,stroke_width=3)[2];x=cx-(nw+7+mw)/2
        d.text((x,239),ss,font=fn,fill=col,anchor='lm',stroke_width=5,stroke_fill=(10,8,5,255));d.text((x+nw+7,247),'m',font=fm,fill=col,anchor='lm',stroke_width=3,stroke_fill=(10,8,5,255));d.text((cx,307),lab,font=fl,fill='white',anchor='mm',stroke_width=2,stroke_fill=(20,12,6,255))

def build(hole,par,vals):
    base=background();base.alpha_composite(HEADER,(0,0));d=ImageDraw.Draw(base);txt(d,(96,120),f'KING · H{hole} · PAR {par}',29,(255,255,255,255),anchor='lm',stroke=1,sf=(0,51,130,180),jp=True);wood_text(base,vals)
    base.alpha_composite(PANEL,(18,477));d=ImageDraw.Draw(base);txt(d,(106,542),'PAR',33,(255,255,255,255),anchor='rm',stroke=3,sf=(5,26,4,255));txt(d,(114,542),str(par),33,(255,188,36,255),anchor='lm',stroke=3,sf=(5,26,4,255));txt(d,(129,620),f'H{hole}',76,(255,255,255,255),stroke=4,sf=(5,24,4,255))
    ci=course[hole];x,y,ww,hh=contain(ci);cr=ci.resize((round(ww),round(hh)),Image.Resampling.LANCZOS);sh=Image.new('RGBA',cr.size,(0,0,0,0));sh.putalpha(cr.getchannel('A').filter(ImageFilter.GaussianBlur(5)).point(lambda v:int(v*.14)));base.alpha_composite(sh,(round(x)+4,round(y)+6));base.alpha_composite(cr,(round(x),round(y)))
    bubble(base);d=ImageDraw.Draw(base);total=vals[1];top=max(150,int(math.ceil(total/50))*50);rx,yt,yb=798,655,1165;d.line((rx,yt,rx,yb),fill=(78,72,53,255),width=2)
    for v in range(top,49,-50):
        yy=yb-(v/top)*(yb-yt);d.line((rx,yy,rx+18,yy),fill=(78,72,53,255),width=2);txt(d,(832,yy),f'{v}m',20,(42,40,31,255),anchor='lm',jp=True)
    if total>=200:
        yy=yb-(200/top)*(yb-yt);d.rounded_rectangle((646,yy-30,777,yy+30),radius=27,fill=(31,92,196,255),outline='white',width=3);txt(d,(711,yy),'200m',26,(255,255,255,255),stroke=1,sf=(20,55,120,255),jp=True);d.ellipse((rx-13,yy-13,rx+13,yy+13),fill='white',outline=(39,38,27,255),width=2);d.ellipse((rx-7,yy-7,rx+7,yy+7),fill=(255,140,30,255))
    target(base);base.alpha_composite(NAV,(18,1458));out=RES/f'furano_king_h{hole}_base_v1152.webp';base.save(out,'WEBP',lossless=True,method=6);print('V1152 ASSET',hole,src_desc[hole],ci.size,out,base.size)

src_desc={h:SRC[h].name for h in SRC}
# Values previously reviewed by the user for Furano KING H1-H3.
build(1,4,(274,286,298));build(2,3,(142,154,166));build(3,4,(355,367,379))
