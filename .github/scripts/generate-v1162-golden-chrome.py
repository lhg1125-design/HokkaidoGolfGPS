from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, base64, io, random, hashlib

# V1.16.2 GOLDEN MASTER CHROME
# This is intentionally derived from the user-approved V1.15.2/V1.15.4 visual master.
# Static chrome is built once. Runtime overlays only dynamic course/text/GPS data.
ASSET=Path('.github/assets/furano-v1152')
RES=Path('app/src/main/res/drawable-nodpi')
ARES=Path('app/src/main/assets')
RES.mkdir(parents=True,exist_ok=True); ARES.mkdir(parents=True,exist_ok=True)
for fp in [ASSET/'header.b64',ASSET/'nav.b64']:
    if not fp.exists(): raise SystemExit(f'V1.16.2 missing approved chrome source {fp}')

def b64_image(path):
    raw=base64.b64decode(Path(path).read_text().strip())
    return Image.open(io.BytesIO(raw)).convert('RGBA')

HEADER_SOURCE=b64_image(ASSET/'header.b64')
NAV_SOURCE=b64_image(ASSET/'nav.b64')
W,H=941,1672
if HEADER_SOURCE.size!=(941,156) or NAV_SOURCE.size!=(905,194):
    raise SystemExit('V1.16.2 approved chrome dimensions changed')

JUA='/tmp/Jua-Regular.ttf'; MPLUS='/tmp/MPLUSRounded1c-ExtraBold.ttf'
def F(sz,jp=False): return ImageFont.truetype(MPLUS if jp else JUA,sz)
def txt(d,xy,s,sz,fill,anchor='mm',stroke=0,sf=(15,15,10,255),jp=False):
    d.text(xy,s,font=F(sz,jp),fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=sf)

# Preserve the exact approved sky/weather/back/icon source, but clear only the
# baked course title/subtitle so runtime data can be inserted without drift.
HEADER=HEADER_SOURCE.copy(); ha=np.array(HEADER.convert('RGBA')); hs=np.array(HEADER_SOURCE.convert('RGB'))
for y in range(14,84):
    col=np.median(hs[y,520:680],axis=0).astype(np.uint8)
    ha[y,78:650,:3]=col; ha[y,78:650,3]=255
for y in range(84,151):
    col=np.median(hs[y,520:680],axis=0).astype(np.uint8)
    ha[y,78:610,:3]=col; ha[y,78:610,3]=255
HEADER=Image.fromarray(ha,'RGBA')
# Restore the approved small course icon at lower left of the header.
HEADER.alpha_composite(HEADER_SOURCE.crop((25,87,100,150)),(25,87))

# Exact approved V1.15.2 wood grammar, including grain, separators and leaves.
def make_wood():
    w,h=905,194; im=Image.new('RGBA',(w,h),(0,0,0,0))
    sh=Image.new('RGBA',(w,h),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((5,11,w-5,h-3),radius=26,fill=(25,14,7,120)); sh=sh.filter(ImageFilter.GaussianBlur(8)); im.alpha_composite(sh)
    d=ImageDraw.Draw(im,'RGBA')
    for y in range(5,h-13):
        t=(y-5)/(h-18); c=(int(139-41*t),int(82-31*t),int(34-17*t),255); d.line((5,y,w-5,y),fill=c,width=1)
    d.rounded_rectangle((5,5,w-5,h-13),radius=25,outline=(70,38,16,255),width=4)
    d.arc((9,8,w-9,80),188,352,fill=(255,205,130,72),width=4)
    rnd=random.Random(1152)
    for k in range(11):
        y=23+k*13+rnd.randint(-3,3); pts=[(x,y+rnd.randint(-3,3)) for x in range(20,w-20,40)]; d.line(pts,fill=(220,154,87,44),width=2)
    for x in (299,600):
        d.line((x,14,x,h-28),fill=(47,26,12,150),width=3); d.line((x+3,14,x+3,h-28),fill=(210,143,74,40),width=1)
    for cx,cy,flip in [(20,19,1),(878,19,-1),(20,154,1),(878,154,-1)]:
        for j in range(4):
            ox=(j%2)*12*flip; oy=(j//2)*12
            d.ellipse((cx+ox-8,cy+oy-5,cx+ox+9,cy+oy+8),fill=(67+10*j,145+8*j,24,255),outline=(24,77,12,255),width=2)
            d.line((cx+ox-5*flip,cy+oy+1,cx+ox+6*flip,cy+oy-1),fill=(190,225,75,150),width=1)
    return im
WOOD=make_wood()
wd=ImageDraw.Draw(WOOD)
for cx,lab in zip([148,452,757],['FRONT','CENTER','BACK']):
    txt(wd,(cx,151),lab,27,(255,255,255,255),stroke=2,sf=(20,12,6,255),jp=True)

# Exact approved bottom navigation source and alpha/shadow treatment.
NAV=NAV_SOURCE.copy(); nw,nh=NAV.size
na=Image.new('L',(nw,nh),0); ImageDraw.Draw(na).rounded_rectangle((1,1,nw-2,nh-2),radius=50,fill=255)
sh=Image.new('L',(nw,nh),0); ImageDraw.Draw(sh).rounded_rectangle((4,6,nw-4,nh-1),radius=50,fill=90); sh=sh.filter(ImageFilter.GaussianBlur(7))
NAV.putalpha(Image.fromarray(np.maximum(np.array(na),np.array(sh)).astype(np.uint8)))

# Exact approved score-side panel; runtime paints PAR/H/player content only.
PANEL=Image.new('RGBA',(220,843),(0,0,0,0)); pd=ImageDraw.Draw(PANEL,'RGBA')
psh=Image.new('RGBA',PANEL.size,(0,0,0,0)); ImageDraw.Draw(psh).rounded_rectangle((7,9,217,840),radius=28,fill=(0,0,0,72)); psh=psh.filter(ImageFilter.GaussianBlur(7)); PANEL.alpha_composite(psh)
pd.rounded_rectangle((1,1,208,833),radius=28,fill=(13,84,15,255),outline=(8,48,7,255),width=4)
for yy in range(12,824):
    t=(yy-12)/(824-12); pd.line((12,yy,201,yy),fill=(18-int(6*t),98-int(16*t),19-int(5*t),255),width=1)
pd.rounded_rectangle((5,5,204,829),radius=25,outline=(77,145,31,255),width=3)
for yy in [220,370,520,670]: pd.line((25,yy,190,yy),fill=(130,175,70,150),width=1)

def background():
    a=np.zeros((H,W,4),np.uint8)
    for y in range(H):
        if y<350: col=np.array([247,239,214])
        elif y<1458:
            t=(y-350)/(1458-350); col=np.array([247,239,214])*(1-t)+np.array([234,220,184])*t
        else: col=np.array([237,223,188])
        a[y,:,:3]=col.astype(np.uint8); a[y,:,3]=255
    return Image.fromarray(a,'RGBA')

def target(base):
    d=ImageDraw.Draw(base,'RGBA'); x0,y0,x1,y1=638,1261,908,1388
    sh=Image.new('RGBA',base.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=48,fill=(55,34,15,75)); sh=sh.filter(ImageFilter.GaussianBlur(7)); base.alpha_composite(sh)
    d.rounded_rectangle((x0,y0,x1,y1),radius=48,fill=(246,216,166,255),outline=(142,94,48,255),width=3)
    d.arc((x0+8,y0+5,x1-8,y0+92),190,350,fill=(255,255,255,80),width=4)
    cx,cy=703,1324
    d.ellipse((cx-22,cy-22,cx+22,cy+22),outline=(20,20,15,255),width=5); d.ellipse((cx-7,cy-7,cx+7,cy+7),outline=(20,20,15,255),width=5)
    d.line((cx-34,cy,cx-20,cy),fill=(20,20,15,255),width=5); d.line((cx+20,cy,cx+34,cy),fill=(20,20,15,255),width=5)
    d.line((cx,cy-34,cx,cy-20),fill=(20,20,15,255),width=5); d.line((cx,cy+20,cx,cy+34),fill=(20,20,15,255),width=5)
    txt(d,(804,1324),'타겟',34,(25,23,17,255))

def bubble(base):
    d=ImageDraw.Draw(base,'RGBA'); x0,y0,x1,y1=714,397,918,575
    sh=Image.new('RGBA',base.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=28,fill=(0,0,0,70)); sh=sh.filter(ImageFilter.GaussianBlur(7)); base.alpha_composite(sh)
    d.rounded_rectangle((x0,y0,x1,y1),radius=28,fill=(255,248,224,255),outline=(34,31,24,255),width=3)
    d.polygon([(x0+6,y1-48),(x0-20,y1),(x0+38,y1-24)],fill=(255,248,224,255),outline=(34,31,24,255))
    txt(d,(816,432),'남은 거리',25,(31,30,24,255)); d.line((752,520,880,520),fill=(194,156,95,255),width=2); txt(d,(816,548),'핀까지',23,(31,30,24,255))

base=background(); base.alpha_composite(HEADER,(0,0)); base.alpha_composite(WOOD,(18,156)); base.alpha_composite(PANEL,(18,477)); bubble(base); target(base); base.alpha_composite(NAV,(18,1458))
out=RES/'master_golden_chrome_v1162.webp'; base.save(out,'WEBP',lossless=True,method=6)
sha=hashlib.sha256(out.read_bytes()).hexdigest()
(ARES/'master_golden_v1162.lock').write_text('V1.16.2 USER GOLDEN MASTER CHROME\nsize=941x1672\nsource=V1.15.2/V1.15.4 approved chrome\nsha256='+sha+'\ncourse_geometry=runtime_raw_untouched\n')
print('V1.16.2 GOLDEN MASTER CHROME',out,base.size,sha)
