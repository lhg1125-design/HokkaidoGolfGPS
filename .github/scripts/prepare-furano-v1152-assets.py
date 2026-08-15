from pathlib import Path
from urllib.parse import urljoin
from PIL import Image, ImageDraw, ImageFilter
import requests,re,base64,io,random

A=Path('.github/assets/furano-v1152');A.mkdir(parents=True,exist_ok=True)
PAGE='https://booking.gora.golf.rakuten.co.jp/guide/course_info/layout/disp/c_id/10164'
S=requests.Session();S.headers.update({'User-Agent':'Mozilla/5.0'})
html=S.get(PAGE,timeout=25).text

def official(name,expected):
    pats=[
      rf'''["']([^"']*{re.escape(name)})["']''',
      rf'''(https?://[^\s"']*{re.escape(name)})'''
    ]
    urls=[]
    for pat in pats:
        for m in re.finditer(pat,html,re.I): urls.append(urljoin(PAGE,m.group(1)))
    # Rakuten's current full-hole asset convention; only used if page markup is lazy-loaded.
    urls += [
      f'https://image.gora.golf.rakuten.co.jp/img/golf/10164/new_hole_info/{name}',
      f'https://image.gora.golf.rakuten.co.jp/img/golf/10164/course/{name}',
      f'https://image.gora.golf.rakuten.co.jp/img/golf/10164/{name}',
    ]
    seen=set();err=[]
    for u in urls:
        if u in seen: continue
        seen.add(u)
        try:
            r=S.get(u,timeout=25);r.raise_for_status();im=Image.open(io.BytesIO(r.content)).convert('RGBA')
            if im.size!=expected: raise ValueError(f'{im.size} != {expected}')
            if im.getchannel('A').getextrema()[0]==255: raise ValueError('source has no transparent exterior')
            print('OFFICIAL',name,u,im.size)
            return r.content
        except Exception as e: err.append(f'{u}: {e}')
    raise SystemExit('Could not fetch exact official '+name+'\n'+'\n'.join(err))

for name,expected,out in [('408_2.webp',(127,400),'king02.b64'),('408_3.webp',(99,400),'king03.b64')]:
    raw=official(name,expected);(A/out).write_text(base64.b64encode(raw).decode())

# Approved master wood grammar: dark warm wood, 3D inset/shadow, grain, dividers, corner leaves.
w,h=905,194
im=Image.new('RGBA',(w,h),(0,0,0,0))
sh=Image.new('RGBA',(w,h),(0,0,0,0));sd=ImageDraw.Draw(sh);sd.rounded_rectangle((5,11,w-5,h-3),radius=26,fill=(25,14,7,120));sh=sh.filter(ImageFilter.GaussianBlur(8));im.alpha_composite(sh)
d=ImageDraw.Draw(im,'RGBA')
# vertical wood gradient
for y in range(5,h-13):
    t=(y-5)/(h-18);c=(int(139-41*t),int(82-31*t),int(34-17*t),255);d.line((5,y,w-5,y),fill=c,width=1)
d.rounded_rectangle((5,5,w-5,h-13),radius=25,outline=(70,38,16,255),width=4)
# top sheen / lower depth
d.arc((9,8,w-9,80),188,352,fill=(255,205,130,72),width=4)
rnd=random.Random(1152)
for k in range(11):
    y=23+k*13+rnd.randint(-3,3);pts=[]
    for x in range(20,w-20,40): pts.append((x,y+rnd.randint(-3,3)))
    d.line(pts,fill=(220,154,87,44),width=2)
for x in (299,600):
    d.line((x,14,x,h-28),fill=(47,26,12,150),width=3);d.line((x+3,14,x+3,h-28),fill=(210,143,74,40),width=1)
# same leafy corner accent language as approved master
for cx,cy,flip in [(20,19,1),(878,19,-1),(20,154,1),(878,154,-1)]:
    for j in range(4):
        ox=(j%2)*12*flip;oy=(j//2)*12
        box=(cx+ox-8,cy+oy-5,cx+ox+9,cy+oy+8)
        d.ellipse(box,fill=(67+10*j,145+8*j,24,255),outline=(24,77,12,255),width=2)
        d.line((cx+ox-5*flip,cy+oy+1,cx+ox+6*flip,cy+oy-1),fill=(190,225,75,150),width=1)
b=io.BytesIO();im.save(b,'WEBP',lossless=True,method=6);(A/'wood.b64').write_text(base64.b64encode(b.getvalue()).decode())
print('prepared',A/'wood.b64')
