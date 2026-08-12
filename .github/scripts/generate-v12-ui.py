from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H=1080,2400
ROOT=Path('app/src/main/res/drawable-nodpi')
ROOT.mkdir(parents=True,exist_ok=True)
hero=Image.open(ROOT/'concept_hero_exact.webp').convert('RGB')
course=Image.open(ROOT/'concept_course_exact.webp').convert('RGB')

JUA='/tmp/Jua-Regular.ttf'
JP='/tmp/MPLUSRounded1c-ExtraBold.ttf'
def font(sz,jp=False):
    p=JP if jp else JUA
    return ImageFont.truetype(p,sz)

def rr(d,box,r,fill,outline=None,width=1):
    d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)

def shadow(im,box,r=28,alpha=35,off=8):
    lay=Image.new('RGBA',im.size,(0,0,0,0));ld=ImageDraw.Draw(lay)
    x1,y1,x2,y2=box;ld.rounded_rectangle((x1,y1+off,x2,y2+off),radius=r,fill=(20,60,35,alpha))
    lay=lay.filter(ImageFilter.GaussianBlur(10));im.alpha_composite(lay)

def centered(d,xy,text,f,fill,stroke=0,stroke_fill=None):
    d.text(xy,text,font=f,fill=fill,anchor='mm',stroke_width=stroke,stroke_fill=stroke_fill)

def fit_cover(src,size):
    sw,sh=src.size;tw,th=size;scale=max(tw/sw,th/sh)
    nw,nh=round(sw*scale),round(sh*scale)
    x=src.resize((nw,nh),Image.Resampling.LANCZOS)
    l=(nw-tw)//2;t=(nh-th)//2
    return x.crop((l,t,l+tw,t+th))

# HOME: use approved reference graphics literally as the hero + enlarged wood signs.
home=Image.new('RGBA',(W,H),(248,249,235,255));d=ImageDraw.Draw(home)
hero_full=fit_cover(hero,(W,575));home.paste(hero_full,(0,0))
rr(d,(0,555,W,610),0,(238,247,221,255))
centered(d,(W//2,648),'오늘 어디서 칠까요?',font(42),(34,68,41,255))
d.text((70,690),'컨셉아트 그래픽 그대로 · 모든 거리 m',font(23),fill=(112,116,103,255))

sign_boxes=[(535,173,719,235),(535,235,719,298),(535,298,719,361)]
card_ys=[755,1010,1265]
for i,(b,y) in enumerate(zip(sign_boxes,card_ys)):
    sign=hero.crop(b)
    sign=fit_cover(sign,(880,205))
    shadow(home,(100,y,980,y+205),34)
    mask=Image.new('L',(880,205),0);md=ImageDraw.Draw(mask);md.rounded_rectangle((0,0,879,204),radius=34,fill=255)
    home.paste(sign,(100,y),mask)
    badge=[(77,160,83,255),(131,89,180,255),(38,128,84,255)][i]
    rr(d,(55,y+54,133,y+132),39,badge)
    centered(d,(94,y+93),str(i+1),font(34),(255,255,255,255))

shadow(home,(70,1515,1010,1700),32);rr(d,(70,1515,1010,1700),32,(255,255,250,255))
d.text((105,1550),'코스 선택',font(28),fill=(54,82,58,255))
rr(d,(105,1600,515,1670),35,(29,121,70,255)); centered(d,(310,1635),'A COURSE',font(26),(255,255,255,255))
rr(d,(565,1600,975,1670),35,(241,244,235,255)); centered(d,(770,1635),'B COURSE',font(26),(50,69,54,255))

shadow(home,(70,1760,1010,1930),44);rr(d,(70,1760,1010,1930),44,(246,153,48,255),outline=(205,116,30,255),width=4)
centered(d,(540,1845),'라운드 시작  →',font(42),(255,255,255,255),stroke=2,stroke_fill=(180,95,25,255))
rr(d,(70,1990,500,2075),42,(226,244,212,255));centered(d,(285,2032),'COURSES OFFLINE ✓',font(24),(31,118,66,255))
rr(d,(580,1990,1010,2075),42,(226,244,212,255));centered(d,(795,2032),'GPS READY ✓',font(24),(31,118,66,255))
centered(d,(540,2170),'24~26 AUG · HOKKAIDO TRIP',font(28),(55,95,64,255))
centered(d,(540,2225),'GPS × 코스맵 × 스코어 관리',font(25),(65,116,78,255))
centered(d,(540,2280),'오프라인에서도 OK!',font(30),(239,111,77,255))
home.convert('RGB').save(ROOT/'v12_home_ui.webp','WEBP',quality=88,method=6)

# COURSE: approved phone-map graphic is the visual core; typography rendered, not Canvas approximated.
co=Image.new('RGBA',(W,H),(247,249,236,255));d=ImageDraw.Draw(co)
for y in range(0,300):
    t=y/300;c=(round(8+(20-8)*t),round(92+(132-92)*t),round(58+(77-58)*t),255);d.line((0,y,W,y),fill=c)
d.text((65,54),'LIVE COURSE',font(28),fill=(212,246,220,255))
d.text((65,105),'GPS 캐디',font(48),fill=(255,255,255,255))
rr(d,(775,55,1015,125),35,(229,245,219,255));centered(d,(895,90),'GPS READY',font(23),(28,112,66,255))
shadow(co,(55,330,1025,545),35);rr(d,(55,330,1025,545),35,(12,108,65,255))
for x,lab in [(205,'FRONT'),(540,'CENTER'),(875,'BACK')]:
    centered(d,(x,390),lab,font(25),(205,239,214,255))
map_box=(55,600,1025,1605);shadow(co,map_box,42)
rr(d,map_box,42,(214,241,199,255))
map_img=fit_cover(course,(930,965))
mask=Image.new('L',(930,965),0);md=ImageDraw.Draw(mask);md.rounded_rectangle((0,0,929,964),radius=35,fill=255)
co.paste(map_img,(75,620),mask)
rr(d,(82,645,285,705),30,(255,255,255,225));centered(d,(183,675),'LIVE MAP',font(22),(30,115,66,255))
shadow(co,(55,1645,1025,1770),28);rr(d,(55,1645,1025,1770),28,(255,252,232,255))
d.text((85,1683),'★  공략 포인트',font(26),fill=(28,115,66,255))
for box,label,col in [((55,1805,410,1900),'GREEN 3점',(18,103,63,255)),((435,1805,700,1900),'TEE 저장',(53,139,94,255)),((725,1805,1025,1900),'외부 지도',(255,255,255,255))]:
    shadow(co,box,28);rr(d,box,28,col,outline=(223,227,213,255) if col==(255,255,255,255) else None,width=2)
    centered(d,((box[0]+box[2])//2,(box[1]+box[3])//2),label,font(24),(255,255,255,255) if col!=(255,255,255,255) else (37,58,43,255))
shadow(co,(55,1950,1025,2200),32);rr(d,(55,1950,1025,2200),32,(255,255,255,255))
d.text((90,1988),'타수',font(26),fill=(120,123,113,255));d.text((600,1988),'퍼트',font(26),fill=(120,123,113,255))
rr(d,(55,2240,1025,2350),45,(255,255,255,255))
for x,lab in [(175,'이전'),(410,'코스'),(655,'스코어'),(900,'다음')]: centered(d,(x,2295),lab,font(22),(35,70,43,255))
co.convert('RGB').save(ROOT/'v12_course_ui.webp','WEBP',quality=88,method=6)

sc=Image.new('RGBA',(W,H),(247,249,236,255));d=ImageDraw.Draw(sc)
for y in range(0,290):
    t=y/290;c=(round(8+(20-8)*t),round(92+(132-92)*t),round(58+(77-58)*t),255);d.line((0,y,W,y),fill=c)
d.text((65,70),'스코어카드',font(50),fill=(255,255,255,255))
d.text((65,135),'4명 함께 · 자동 합계',font(25),fill=(211,243,220,255))
rr(d,(55,330,1025,410),22,(7,78,50,255))
cols=[(105,'HOLE'),(265,'PAR'),(445,'P1'),(610,'P2'),(775,'P3'),(940,'P4')]
for x,lab in cols:centered(d,(x,370),lab,font(22),(255,255,255,255))
sy=430
for i in range(18):
    y=sy+i*73; fill=(255,255,255,255) if i%2==0 else (255,253,240,255)
    rr(d,(55,y,1025,y+62),18,fill)
shadow(sc,(55,1805,1025,2115),34);rr(d,(55,1805,1025,2115),34,(10,103,62,255))
d.text((90,1855),'ROUND TOTAL',font(28),fill=(210,242,219,255))
rr(d,(65,2150,410,2225),38,(235,247,216,255));centered(d,(238,2188),'나이스 라운드!',font(24),(30,115,66,255))
rr(d,(55,2240,1025,2350),45,(255,255,255,255))
for x,lab in [(175,'이전'),(410,'코스'),(655,'스코어'),(900,'다음')]: centered(d,(x,2295),lab,font(22),(35,70,43,255))
sc.convert('RGB').save(ROOT/'v12_score_ui.webp','WEBP',quality=88,method=6)
print('generated v1.2 raster UI assets')
