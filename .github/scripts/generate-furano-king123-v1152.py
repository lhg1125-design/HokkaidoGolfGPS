from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, cv2, math, base64, io

ASSET=Path('.github/assets/furano-v1152')
RES=Path('app/src/main/res/drawable-nodpi')
RES.mkdir(parents=True,exist_ok=True)
H1SRC=RES/'yardage_furano_king01.jpg'
for fp in [H1SRC,ASSET/'king02.b64',ASSET/'king03.b64']+[ASSET/f'master_{i}.b64' for i in range(1,5)]:
    if not fp.exists(): raise SystemExit(f'V1.15.2 missing source {fp}')

def b64_image(paths):
    raw=base64.b64decode(''.join(Path(x).read_text().strip() for x in paths));return Image.open(io.BytesIO(raw)).convert('RGBA')
master=b64_image([ASSET/f'master_{i}.b64' for i in range(1,5)]); W,H=master.size
if (W,H)!=(941,1672): raise SystemExit(f'V1.15.2 master size {(W,H)} != (941,1672)')
mrgb=np.array(master.convert('RGB'))
JUA='/tmp/Jua-Regular.ttf'; MPLUS='/tmp/MPLUSRounded1c-ExtraBold.ttf'
def F(sz,jp=False): return ImageFont.truetype(MPLUS if jp else JUA,sz)
def txt(d,xy,s,sz,fill,anchor='mm',stroke=0,sf=(15,15,10,255),jp=False):
    d.text(xy,s,font=F(sz,jp),fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=sf)

# Keep Furano course pixels untouched. Only strip the near-white page background from H1.
def alpha_h1(src):
    im=Image.open(src).convert('RGB'); a=np.array(im); mx=a.max(2);mn=a.min(2);sat=mx-mn
    bg=(a[:,:,0]>235)&(a[:,:,1]>235)&(a[:,:,2]>225)&(sat<42)
    alpha=(~bg).astype(np.uint8)*255
    alpha=cv2.morphologyEx(alpha,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8),1)
    rgba=np.dstack([a,alpha])
    return Image.fromarray(rgba,'RGBA')

course={1:alpha_h1(H1SRC),2:b64_image([ASSET/'king02.b64']),3:b64_image([ASSET/'king03.b64'])}
for hh in (2,3):
    if course[hh].getchannel('A').getextrema()[0]==255: raise SystemExit(f'V1.15.2 H{hh} source lost alpha')

HEADER=master.crop((0,0,W,156)).copy(); ha=np.array(HEADER.convert('RGBA'))
for y in range(84,151):
    col=np.median(mrgb[y,520:700],axis=0).astype(np.uint8);ha[y,78:505,:3]=col;ha[y,78:505,3]=255
HEADER=Image.fromarray(ha,'RGBA');HEADER.alpha_composite(master.crop((25,87,100,150)),(25,87))

orig_wood=master.crop((18,156,923,350)); wood=np.array(orig_wood.convert('RGB'));wm=np.zeros(wood.shape[:2],np.uint8)
for x0,x1 in [(55,285),(335,590),(640,865)]: cv2.rectangle(wm,(x0,25),(x1,178),255,-1)
clean=cv2.inpaint(wood,wm,12,cv2.INPAINT_TELEA);WOOD=Image.fromarray(clean).convert('RGBA')
for box,pos in [((0,0,905,14),(0,0)),((0,182,905,194),(0,182)),((0,0,54,194),(0,0)),((866,0,905,194),(866,0))]: WOOD.alpha_composite(orig_wood.crop(box),pos)
for x in [294,595]: WOOD.alpha_composite(orig_wood.crop((x-3,10,x+4,184)),(x-3,10))

NAV=master.crop((18,1458,923,1652)).copy();nw,nh=NAV.size
na=Image.new('L',(nw,nh),0);nd=ImageDraw.Draw(na);nd.rounded_rectangle((1,1,nw-2,nh-2),radius=50,fill=255)
sh=Image.new('L',(nw,nh),0);sd=ImageDraw.Draw(sh);sd.rounded_rectangle((4,6,nw-4,nh-1),radius=50,fill=90);sh=sh.filter(ImageFilter.GaussianBlur(7))
NAV.putalpha(Image.fromarray(np.maximum(np.array(na),np.array(sh)).astype(np.uint8)))

PANEL=master.crop((18,477,238,1320)).copy();pd=ImageDraw.Draw(PANEL,'RGBA')
for yy in range(12,824):
    t=(yy-12)/(824-12);col=(17-int(5*t),96-int(15*t),18-int(5*t),255);pd.line((12,yy,201,yy),fill=col,width=1)
pd.rounded_rectangle((5,5,208,833),radius=26,outline=(71,139,30,255),width=3)
for yy in [220,370,520,670]: pd.line((25,yy,195,yy),fill=(130,175,70,150),width=1)

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
    sh=Image.new('RGBA',base.size,(0,0,0,0));sd=ImageDraw.Draw(sh);sd.rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=48,fill=(55,34,15,75));sh=sh.filter(ImageFilter.GaussianBlur(7));base.alpha_composite(sh)
    mask=Image.new('L',base.size,0);ImageDraw.Draw(mask).rounded_rectangle((x0,y0,x1,y1),radius=48,fill=255)
    ga=np.zeros((H,W,4),np.uint8)
    for y in range(y0,y1+1):
        t=(y-y0)/(y1-y0);col=np.array([255,237,205])*(1-t)+np.array([229,180,105])*t;ga[y,x0:x1+1,:3]=col.astype(np.uint8);ga[y,x0:x1+1,3]=255
    gi=Image.fromarray(ga,'RGBA');gi.putalpha(mask);base.alpha_composite(gi);d=ImageDraw.Draw(base)
    d.rounded_rectangle((x0,y0,x1,y1),radius=48,outline=(142,94,48,255),width=3);d.arc((x0+8,y0+5,x1-8,y0+92),190,350,fill=(255,255,255,80),width=4)
    cx,cy=703,1324;d.ellipse((cx-22,cy-22,cx+22,cy+22),outline=(20,20,15,255),width=5);d.ellipse((cx-7,cy-7,cx+7,cy+7),outline=(20,20,15,255),width=5)
    d.line((cx-34,cy,cx-20,cy),fill=(20,20,15,255),width=5);d.line((cx+20,cy,cx+34,cy),fill=(20,20,15,255),width=5);d.line((cx,cy-34,cx,cy-20),fill=(20,20,15,255),width=5);d.line((cx,cy+20,cx,cy+34),fill=(20,20,15,255),width=5);txt(d,(804,1324),'타겟',34,(25,23,17,255))

def bubble(base):
    d=ImageDraw.Draw(base,'RGBA');x0,y0,x1,y1=714,397,918,575
    sh=Image.new('RGBA',base.size,(0,0,0,0));sd=ImageDraw.Draw(sh);sd.rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=28,fill=(0,0,0,70));sd.polygon([(x0+10,y1-42),(x0-18,y1+7),(x0+40,y1-18)],fill=(0,0,0,50));sh=sh.filter(ImageFilter.GaussianBlur(7));base.alpha_composite(sh);d=ImageDraw.Draw(base)
    d.rounded_rectangle((x0,y0,x1,y1),radius=28,fill=(255,248,224,255),outline=(34,31,24,255),width=3);d.polygon([(x0+6,y1-48),(x0-20,y1),(x0+38,y1-24)],fill=(255,248,224,255),outline=(34,31,24,255));txt(d,(816,432),'남은 거리',25,(31,30,24,255));d.line((752,520,880,520),fill=(194,156,95,255),width=2);txt(d,(816,548),'핀까지',23,(31,30,24,255))

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
    target(base);base.alpha_composite(NAV,(18,1458));out=RES/f'furano_king_h{hole}_base_v1152.webp';base.save(out,'WEBP',lossless=True,method=6);print('V1152 ASSET',out,base.size)

build(1,4,(274,286,298));build(2,3,(142,154,166));build(3,4,(355,367,379))
