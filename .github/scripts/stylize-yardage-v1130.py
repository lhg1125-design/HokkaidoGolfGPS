from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont, ImageChops
import random

ROOT=Path('app/src/main/res/drawable-nodpi')
TMP=Path('.github/tmp/v1130')
TMP.mkdir(parents=True,exist_ok=True)
FILES=sorted(ROOT.glob('yardage_*.jpg'))
if len(FILES)!=135:
    raise SystemExit(f'V1.14.1 expects 135 full-hole JPGs including Naepo 9, got {len(FILES)}')

CREAM=(249,249,231)
MEADOW=(226,240,194)
MEADOW2=(213,233,174)
INK=(48,72,45)
GREEN=(76,157,91)
TREE1=(80,151,69)
TREE2=(103,176,72)
FLOWER=(245,185,72)


def is_matte_pixel(rgb):
    hi=max(rgb);lo=min(rgb);sat=hi-lo
    return (sat<48 and (lo>190 or hi<175)) or hi<24


def clean_border_matte(im):
    src=im.convert('RGB');w,h=src.size
    step=max(18,min(w,h)//28);seeds=[]
    for x in range(0,w,step):seeds.extend([(x,0),(x,h-1)])
    for y in range(0,h,step):seeds.extend([(0,y),(w-1,y)])
    seeds.extend([(0,0),(w-1,0),(0,h-1),(w-1,h-1)])
    for xy in seeds:
        try:
            if is_matte_pixel(src.getpixel(xy)):
                ImageDraw.floodfill(src,xy,CREAM,thresh=48)
        except Exception:
            pass
    return src


def strip_outside_course(im,strong=False):
    src=im.convert('RGB');hsv=src.convert('HSV');_,sat,val=hsv.split()
    sm=sat.point(lambda v:255 if v>(20 if strong else 24) else 0)
    vm=val.point(lambda v:255 if v>22 else 0)
    sig=ImageChops.multiply(sm,vm)
    w,h=src.size;k=max(7,min(35,int(min(w,h)*.045)))
    if k%2==0:k+=1
    keep=sig.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(3))
    return Image.composite(src,Image.new('RGB',src.size,CREAM),keep)


def crop_to_full_hole(im):
    bg=Image.new('RGB',im.size,CREAM);diff=ImageChops.difference(im,bg).convert('L')
    mask=diff.point(lambda v:255 if v>18 else 0);bbox=mask.getbbox()
    if not bbox:return im
    l,t,r,b=bbox;pad=max(8,round(max(im.size)*.012))
    return im.crop((max(0,l-pad),max(0,t-pad),min(im.width,r+pad),min(im.height,b+pad)))


def meadow_gradient(size):
    w,h=size;strip=Image.new('RGB',(1,h));pix=strip.load()
    for y in range(h):
        t=y/max(1,h-1);pix[0,y]=(round(MEADOW[0]*(1-t)+MEADOW2[0]*t),round(MEADOW[1]*(1-t)+MEADOW2[1]*t),round(MEADOW[2]*(1-t)+MEADOW2[2]*t))
    return strip.resize((w,h),Image.Resampling.BILINEAR)


def replace_flat_matte_with_meadow(im):
    src=im.convert('RGB');hsv=src.convert('HSV');_,sat,val=hsv.split()
    low_sat=sat.point(lambda v:255 if v<40 else 0);hi_val=val.point(lambda v:255 if v>188 else 0)
    mask=ImageChops.multiply(low_sat,hi_val).filter(ImageFilter.GaussianBlur(max(1,min(src.size)//220)))
    return Image.composite(meadow_gradient(src.size),src,mask)


def add_storybook_edge_details(im,seed):
    out=im.convert('RGB');w,h=out.size;d=ImageDraw.Draw(out,'RGBA');rnd=random.Random(seed)
    for side in (0,1):
        for i in range(16):
            y=int(h*(.07+i/17*.86)+rnd.randint(-14,14));x=int(w*(.055 if side==0 else .945)+rnd.randint(-10,10));rad=rnd.randint(max(7,w//100),max(10,w//64));col=TREE1 if i%2==0 else TREE2
            d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=col+(108,));d.ellipse((x-rad*.55,y-rad*.72,x+rad*.45,y+rad*.22),fill=(138,196,85,92))
    for i in range(10):
        side=0 if i%2==0 else 1;x=int(w*(.09 if side==0 else .91)+rnd.randint(-8,8));y=rnd.randint(int(h*.13),int(h*.85));rr=max(2,w//220)
        d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=FLOWER+(170,))
    return out


def toon_grade(im,strong=False,naepo=False,name=''):
    im=clean_border_matte(im);im=strip_outside_course(im,strong);im=crop_to_full_hole(im)
    longest=max(im.size);target=1900 if naepo else 1800
    if longest<target:
        sc=target/float(longest);im=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.LANCZOS)
    med=5 if (strong or naepo) else 3
    smooth=im.filter(ImageFilter.MedianFilter(med)).filter(ImageFilter.SMOOTH_MORE).filter(ImageFilter.SMOOTH_MORE)
    base=Image.blend(im,smooth,.70 if strong else .63);base=ImageEnhance.Color(base).enhance(1.44 if not naepo else 1.38);base=ImageEnhance.Contrast(base).enhance(1.10);base=ImageEnhance.Brightness(base).enhance(1.05)
    colors=22 if strong else (26 if naepo else 28);cell=base.quantize(colors=colors,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB');base=Image.blend(base,cell,.87 if strong else .81)
    edges=base.convert('L').filter(ImageFilter.FIND_EDGES);edges=ImageOps.autocontrast(edges);alpha=edges.point(lambda v:0 if v<64 else min(128,int((v-64)*1.05))).filter(ImageFilter.MaxFilter(3))
    contour=Image.new('RGBA',base.size,INK+(0,));contour.putalpha(alpha);out=Image.alpha_composite(base.convert('RGBA'),contour).convert('RGB')
    out=replace_flat_matte_with_meadow(out);out=add_storybook_edge_details(out,hash(name)&0xffffffff)
    stretch=1.90 if not naepo else 1.75;out=out.resize((round(out.width*stretch),out.height),Image.Resampling.LANCZOS);return out.filter(ImageFilter.UnsharpMask(radius=.75,percent=62,threshold=3))

manifest=[];samples=[]
for p in FILES:
    naepo=p.name.startswith('yardage_naepo_');strong=p.name.startswith('yardage_sahoro_')
    with Image.open(p) as src:before=src.size;out=toon_grade(src,strong,naepo,p.name)
    out.save(p,'JPEG',quality=95,subsampling=0,optimize=True,progressive=True);manifest.append(f'{p.name}\t{before[0]}x{before[1]} -> {out.width}x{out.height}')
    if p.name in {'yardage_kamishihoro_c01.jpg','yardage_furano_palmer15.jpg','yardage_sahoro_07.jpg','yardage_royallinks_queens07.jpg','yardage_naepo_01.jpg'}:samples.append((p.name,out.copy()))

(TMP/'manifest.txt').write_text('\n'.join(manifest)+'\n')
if samples:
    cols=5;tile_w=300;tile_h=610;W=cols*312+30;H=700;sheet=Image.new('RGB',(W,H),CREAM);d=ImageDraw.Draw(sheet)
    try:f=ImageFont.truetype('/tmp/Jua-Regular.ttf',25);sf=ImageFont.truetype('/tmp/Jua-Regular.ttf',17)
    except Exception:f=sf=None
    d.text((28,22),'V1.14.1 · APPROVED STORYBOOK YARDAGE',fill=INK,font=f)
    for idx,(name,im) in enumerate(samples):
        x=20+idx*312;y=66;sc=min(tile_w/im.width,tile_h/im.height);thumb=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.LANCZOS);bx=x+(tile_w-thumb.width)//2;by=y+(tile_h-thumb.height)//2
        sheet.paste(thumb,(bx,by));d.rounded_rectangle((x,y,x+tile_w,y+tile_h),radius=24,outline=GREEN,width=4);d.text((x+8,y+625),name.replace('yardage_','').replace('.jpg',''),fill=INK,font=sf)
    sheet.save(TMP/'yardage-concept-samples.jpg','JPEG',quality=94,subsampling=0)

print('V1.14.1 135 yardages converted to wider high-contrast storybook illustration style')
print('sample sheet:',TMP/'yardage-concept-samples.jpg')
