from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RES=Path('app/src/main/res/drawable-nodpi')
JUA='/tmp/Jua-Regular.ttf'
MPLUS='/tmp/MPLUSRounded1c-ExtraBold.ttf'

def F(sz,jp=False): return ImageFont.truetype(MPLUS if jp else JUA,sz)
def txt(d,xy,s,sz,fill,anchor='mm',stroke=0,stroke_fill=(10,20,16,255),jp=False):
    d.text(xy,s,font=F(sz,jp),fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=stroke_fill)

def bubble(base):
    d=ImageDraw.Draw(base,'RGBA');x0,y0,x1,y1=714,397,918,575
    sh=Image.new('RGBA',base.size,(0,0,0,0));sd=ImageDraw.Draw(sh,'RGBA')
    sd.rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=28,fill=(0,0,0,70));sd.polygon([(x0+12,y1-42),(x0-14,y1+5),(x0+43,y1-18)],fill=(0,0,0,55))
    sh=sh.filter(ImageFilter.GaussianBlur(7));base.alpha_composite(sh);d=ImageDraw.Draw(base,'RGBA')
    d.rounded_rectangle((x0,y0,x1,y1),radius=28,fill=(255,248,224,255),outline=(34,31,24,255),width=3)
    d.polygon([(x0+6,y1-48),(x0-20,y1),(x0+38,y1-24)],fill=(255,248,224,255));d.line((x0-20,y1,x0+7,y1-49),fill=(34,31,24,255),width=3);d.line((x0-20,y1,x0+38,y1-24),fill=(34,31,24,255),width=3)
    txt(d,(816,432),'남은 거리',25,(31,30,24,255));d.line((752,520,880,520),fill=(194,156,95,255),width=2);txt(d,(816,548),'핀까지',23,(31,30,24,255))

def target(base):
    d=ImageDraw.Draw(base,'RGBA');x0,y0,x1,y1=638,1261,908,1388
    sh=Image.new('RGBA',base.size,(0,0,0,0));sd=ImageDraw.Draw(sh,'RGBA');sd.rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=48,fill=(55,34,15,75));sh=sh.filter(ImageFilter.GaussianBlur(7));base.alpha_composite(sh);d=ImageDraw.Draw(base,'RGBA')
    d.rounded_rectangle((x0,y0,x1,y1),radius=48,fill=(246,216,166,255),outline=(142,94,48,255),width=3);d.arc((x0+8,y0+5,x1-8,y0+92),190,350,fill=(255,255,255,80),width=4)
    cx,cy=703,1324;d.ellipse((cx-22,cy-22,cx+22,cy+22),outline=(20,20,15,255),width=5);d.ellipse((cx-7,cy-7,cx+7,cy+7),outline=(20,20,15,255),width=5);d.line((cx-34,cy,cx-20,cy),fill=(20,20,15,255),width=5);d.line((cx+20,cy,cx+34,cy),fill=(20,20,15,255),width=5);d.line((cx,cy-34,cx,cy-20),fill=(20,20,15,255),width=5);d.line((cx,cy+20,cx,cy+34),fill=(20,20,15,255),width=5);txt(d,(804,1324),'타겟',34,(25,23,17,255))

def ruler(base,hole):
    # Rebuild after the strict central cleanup: no part of the 200m pill may be hidden by course pixels.
    d=ImageDraw.Draw(base,'RGBA');top={1:250,2:250,3:400}[hole];rx,yt,yb=798,655,1165
    d.line((rx,yt,rx,yb),fill=(76,71,54,255),width=2)
    for v in range(top,49,-50):
        yy=yb-(v/top)*(yb-yt);d.line((rx,yy,rx+18,yy),fill=(76,71,54,255),width=2);txt(d,(832,yy),f'{v}m',20,(42,40,31,255),anchor='lm',jp=True)
    if top>=200:
        yy=yb-(200/top)*(yb-yt);x0,x1=655,782
        sh=Image.new('RGBA',base.size,(0,0,0,0));sd=ImageDraw.Draw(sh,'RGBA');sd.rounded_rectangle((x0+3,yy-23,x1+3,yy+31),radius=24,fill=(20,40,90,55));sh=sh.filter(ImageFilter.GaussianBlur(4));base.alpha_composite(sh);d=ImageDraw.Draw(base,'RGBA')
        d.rounded_rectangle((x0,yy-27,x1,yy+27),radius=24,fill=(32,91,194,255),outline=(255,255,255,255),width=3);txt(d,((x0+x1)/2,yy),'200m',25,(255,255,255,255),stroke=1,stroke_fill=(20,54,115,255),jp=True)
        d.ellipse((rx-13,yy-13,rx+13,yy+13),fill=(255,255,255,255),outline=(39,38,27,255),width=2);d.ellipse((rx-7,yy-7,rx+7,yy+7),fill=(255,140,30,255))

for hole in (1,2,3):
    fp=RES/f'furano_king_h{hole}_base_v1152.webp';base=Image.open(fp).convert('RGBA');bubble(base);ruler(base,hole);target(base);base.save(fp,'WEBP',lossless=True,method=6);print('V1153 CHROME RESTORED',hole,fp)
