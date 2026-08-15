from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RES=Path('app/src/main/res/drawable-nodpi')
JUA='/tmp/Jua-Regular.ttf'

def F(sz): return ImageFont.truetype(JUA,sz)
def txt(d,xy,s,sz,fill,anchor='mm'):
    d.text(xy,s,font=F(sz),fill=fill,anchor=anchor)

def bubble(base):
    # Restore the exact fixed right speech-bubble shell after central course cleanup.
    d=ImageDraw.Draw(base,'RGBA');x0,y0,x1,y1=714,397,918,575
    sh=Image.new('RGBA',base.size,(0,0,0,0))
    sd=ImageDraw.Draw(sh,'RGBA');sd.rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=28,fill=(0,0,0,70))
    sd.polygon([(x0+12,y1-42),(x0-14,y1+5),(x0+43,y1-18)],fill=(0,0,0,55))
    sh=sh.filter(ImageFilter.GaussianBlur(7));base.alpha_composite(sh)
    d=ImageDraw.Draw(base,'RGBA')
    d.rounded_rectangle((x0,y0,x1,y1),radius=28,fill=(255,248,224,255),outline=(34,31,24,255),width=3)
    d.polygon([(x0+6,y1-48),(x0-20,y1),(x0+38,y1-24)],fill=(255,248,224,255))
    d.line((x0-20,y1,x0+7,y1-49),fill=(34,31,24,255),width=3)
    d.line((x0-20,y1,x0+38,y1-24),fill=(34,31,24,255),width=3)
    txt(d,(816,432),'남은 거리',25,(31,30,24,255))
    d.line((752,520,880,520),fill=(194,156,95,255),width=2)
    txt(d,(816,548),'핀까지',23,(31,30,24,255))

def target(base):
    # Restore full target button; central wipe must never leave a clipped left edge.
    d=ImageDraw.Draw(base,'RGBA');x0,y0,x1,y1=638,1261,908,1388
    sh=Image.new('RGBA',base.size,(0,0,0,0));sd=ImageDraw.Draw(sh,'RGBA')
    sd.rounded_rectangle((x0+6,y0+7,x1+6,y1+7),radius=48,fill=(55,34,15,75))
    sh=sh.filter(ImageFilter.GaussianBlur(7));base.alpha_composite(sh)
    d=ImageDraw.Draw(base,'RGBA')
    d.rounded_rectangle((x0,y0,x1,y1),radius=48,fill=(246,216,166,255),outline=(142,94,48,255),width=3)
    d.arc((x0+8,y0+5,x1-8,y0+92),190,350,fill=(255,255,255,80),width=4)
    cx,cy=703,1324
    d.ellipse((cx-22,cy-22,cx+22,cy+22),outline=(20,20,15,255),width=5)
    d.ellipse((cx-7,cy-7,cx+7,cy+7),outline=(20,20,15,255),width=5)
    d.line((cx-34,cy,cx-20,cy),fill=(20,20,15,255),width=5);d.line((cx+20,cy,cx+34,cy),fill=(20,20,15,255),width=5)
    d.line((cx,cy-34,cx,cy-20),fill=(20,20,15,255),width=5);d.line((cx,cy+20,cx,cy+34),fill=(20,20,15,255),width=5)
    txt(d,(804,1324),'타겟',34,(25,23,17,255))

for hole in (1,2,3):
    fp=RES/f'furano_king_h{hole}_base_v1152.webp'
    base=Image.open(fp).convert('RGBA')
    bubble(base);target(base)
    base.save(fp,'WEBP',lossless=True,method=6)
    print('V1153 CHROME RESTORED',hole,fp)
