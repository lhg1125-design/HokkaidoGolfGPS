from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont, ImageChops

ROOT=Path('app/src/main/res/drawable-nodpi')
TMP=Path('.github/tmp/v1130')
TMP.mkdir(parents=True,exist_ok=True)
FILES=sorted(ROOT.glob('yardage_*.jpg'))
if len(FILES)!=135:
    raise SystemExit(f'V1.13.2 expects 135 full-hole JPGs including Naepo 9, got {len(FILES)}')

CREAM=(249,249,231)
INK=(54,80,54)
GREEN=(76,157,91)

def is_matte_pixel(rgb):
    hi=max(rgb);lo=min(rgb);sat=hi-lo
    return (sat<42 and (hi<190 or lo>205)) or hi<28

def clean_border_matte(im):
    src=im.convert('RGB');w,h=src.size
    step=max(18,min(w,h)//28);seeds=[]
    for x in range(0,w,step):seeds.extend([(x,0),(x,h-1)])
    for y in range(0,h,step):seeds.extend([(0,y),(w-1,y)])
    seeds.extend([(w-1,0),(0,h-1),(w-1,h-1)])
    for xy in seeds:
        try:
            if is_matte_pixel(src.getpixel(xy)):ImageDraw.floodfill(src,xy,CREAM,thresh=42)
        except Exception:pass
    return src

def strip_outside_course(im):
    src=im.convert('RGB');w,h=src.size
    hsv=src.convert('HSV');_,sat,val=hsv.split()
    sm=sat.point(lambda v:255 if v>24 else 0)
    vm=val.point(lambda v:255 if v>24 else 0)
    sig=ImageChops.multiply(sm,vm)
    k=max(7,min(31,int(min(w,h)*.04)))
    if k%2==0:k+=1
    keep=sig.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(3))
    return Image.composite(src,Image.new('RGB',(w,h),CREAM),keep)

def strip_sahoro_publisher_matte(im):
    src=im.convert('RGB');w,h=src.size
    pix=src.load();mask=Image.new('L',(w,h),0);md=ImageDraw.Draw(mask)
    spans=[]
    for y in range(h):
        xs=[]
        for x in range(w):
            r,g,b=pix[x,y];hi=max(r,g,b);lo=min(r,g,b);sat=hi-lo
            greenish=(g>r+9 and g>b+5 and g>55)
            blueish=(b>r+10 and b>g-2 and b>70)
            warm=(r>105 and g>85 and b<95 and sat>26)
            if sat>30 and (greenish or blueish or warm):xs.append(x)
        spans.append((min(xs),max(xs)) if xs else None)
    last=None
    for y in range(h):
        if spans[y] is not None:last=spans[y]
        elif last is not None:spans[y]=last
    last=None
    for y in range(h-1,-1,-1):
        if spans[y] is not None:last=spans[y]
        elif last is not None:spans[y]=last
    pad=max(2,round(w*.025))
    for y,sp in enumerate(spans):
        if sp is None:continue
        l=max(0,sp[0]-pad);r=min(w-1,sp[1]+pad);md.line((l,y,r,y),fill=255,width=1)
    mask=mask.filter(ImageFilter.MaxFilter(3))
    return Image.composite(src,Image.new('RGB',(w,h),CREAM),mask)

def crop_to_full_hole(im):
    bg=Image.new('RGB',im.size,CREAM)
    diff=ImageChops.difference(im,bg).convert('L')
    mask=diff.point(lambda v:255 if v>18 else 0);bbox=mask.getbbox()
    if not bbox:return im
    l,t,r,b=bbox;pad=max(10,round(max(im.size)*.018))
    return im.crop((max(0,l-pad),max(0,t-pad),min(im.width,r+pad),min(im.height,b+pad)))

def toon_grade(im,strong=False,naepo=False):
    im=clean_border_matte(im)
    im=strip_sahoro_publisher_matte(im) if strong else strip_outside_course(im)
    im=crop_to_full_hole(im)
    longest=max(im.size);target=1900 if naepo else 1800
    if longest<target:
        scale=target/float(longest);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    med=3 if naepo else (5 if strong else 3)
    smooth=im.filter(ImageFilter.MedianFilter(med)).filter(ImageFilter.SMOOTH_MORE)
    base=Image.blend(im,smooth,.48 if naepo else (.66 if strong else .54))
    base=ImageEnhance.Color(base).enhance(1.34 if naepo else (1.30 if strong else 1.25))
    base=ImageEnhance.Contrast(base).enhance(1.13 if naepo else 1.11)
    base=ImageEnhance.Brightness(base).enhance(1.04)
    colors=64 if naepo else (30 if strong else 48)
    cell=base.quantize(colors=colors,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
    base=Image.blend(base,cell,.56 if naepo else (.80 if strong else .64))
    edges=base.convert('L').filter(ImageFilter.FIND_EDGES);edges=ImageOps.autocontrast(edges)
    alpha=edges.point(lambda v:0 if v<(80 if naepo else 72) else min(96,int((v-(80 if naepo else 72))*.78)))
    contour=Image.new('RGBA',base.size,INK+(0,));contour.putalpha(alpha)
    out=Image.alpha_composite(base.convert('RGBA'),contour).convert('RGB')
    out=out.filter(ImageFilter.UnsharpMask(radius=.9,percent=72 if naepo else 68,threshold=3))
    return out

manifest=[];samples=[]
for p in FILES:
    naepo=p.name.startswith('yardage_naepo_')
    with Image.open(p) as src:
        before=src.size;out=toon_grade(src,p.name.startswith('yardage_sahoro_'),naepo)
    out.save(p,'JPEG',quality=96,subsampling=0,optimize=True,progressive=True)
    manifest.append(f'{p.name}\t{before[0]}x{before[1]} -> {out.width}x{out.height}')
    if p.name in {'yardage_kamishihoro_c01.jpg','yardage_furano_palmer15.jpg','yardage_sahoro_13.jpg','yardage_royallinks_queens01.jpg','yardage_naepo_01.jpg','yardage_naepo_02.jpg','yardage_naepo_06.jpg','yardage_naepo_09.jpg'}:
        samples.append((p.name,out.copy()))

(TMP/'manifest.txt').write_text('\n'.join(manifest)+'\n')
if samples:
    cols=4;tile_w=330;tile_h=620;rows=(len(samples)+cols-1)//cols
    W=cols*340+40;H=80+rows*690
    sheet=Image.new('RGB',(W,H),CREAM);d=ImageDraw.Draw(sheet)
    try:f=ImageFont.truetype('/tmp/Jua-Regular.ttf',26);sf=ImageFont.truetype('/tmp/Jua-Regular.ttf',18)
    except Exception:f=sf=None
    d.text((35,25),'V1.13.2 · REAL + ANIMATION YARDAGE',fill=INK,font=f)
    for idx,(name,im) in enumerate(samples):
        col=idx%cols;row=idx//cols;x=30+col*340;y=75+row*690
        sc=min(tile_w/im.width,tile_h/im.height);thumb=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.LANCZOS)
        bx=x+(tile_w-thumb.width)//2;by=y+(tile_h-thumb.height)//2
        sheet.paste(thumb,(bx,by));d.rounded_rectangle((x,y,x+tile_w,y+tile_h),radius=26,outline=GREEN,width=4)
        d.text((x+8,y+632),name.replace('yardage_','').replace('.jpg',''),fill=INK,font=sf)
    sheet.save(TMP/'yardage-concept-samples.jpg','JPEG',quality=94,subsampling=0)

print('V1.13.2 135 yardages converted to clean high-res animation style')
print('Naepo styled maps:',len(list(ROOT.glob('yardage_naepo_*.jpg'))))
print('sample sheet:',TMP/'yardage-concept-samples.jpg')
