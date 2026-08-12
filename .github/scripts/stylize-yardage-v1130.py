from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont, ImageChops

ROOT=Path('app/src/main/res/drawable-nodpi')
TMP=Path('.github/tmp/v1130')
TMP.mkdir(parents=True,exist_ok=True)
FILES=sorted(ROOT.glob('yardage_*.jpg'))
if len(FILES)!=126:
    raise SystemExit(f'V1.13.0 expects 126 full-hole JPGs, got {len(FILES)}')

CREAM=(249,249,231)
INK=(54,80,54)
GREEN=(76,157,91)

def is_matte_pixel(rgb):
    hi=max(rgb); lo=min(rgb); sat=hi-lo
    return (sat<42 and (hi<190 or lo>205)) or hi<28

def clean_border_matte(im):
    src=im.convert('RGB');w,h=src.size
    step=max(18,min(w,h)//28);seeds=[]
    for x in range(0,w,step): seeds.extend([(x,0),(x,h-1)])
    for y in range(0,h,step): seeds.extend([(0,y),(w-1,y)])
    seeds.extend([(w-1,0),(0,h-1),(w-1,h-1)])
    for xy in seeds:
        try:
            if is_matte_pixel(src.getpixel(xy)):
                ImageDraw.floodfill(src,xy,CREAM,thresh=42)
        except Exception: pass
    return src

def strip_outside_course(im):
    """Keep the verified hole and its local rough, replace source canvas outside.

    A saturation/value signal finds the coloured course body row by row. Everything
    between the left/right course edges is preserved verbatim, including white
    bunkers and grey cart paths; only exterior matte is converted to cream.
    """
    src=im.convert('RGB');w,h=src.size
    hsv=src.convert('HSV');_,sat,val=hsv.split()
    sm=sat.point(lambda v:255 if v>28 else 0)
    vm=val.point(lambda v:255 if v>28 else 0)
    sig=ImageChops.multiply(sm,vm)
    keep=Image.new('L',(w,h),0);kd=ImageDraw.Draw(keep)
    pad=max(8,round(w*.018))
    for y in range(h):
        bb=sig.crop((0,y,w,y+1)).getbbox()
        if bb:
            l=max(0,bb[0]-pad);r=min(w-1,bb[2]-1+pad)
            kd.line((l,y,r,y),fill=255,width=1)
    # Small vertical expansion prevents isolated low-saturation course edge loss.
    keep=keep.filter(ImageFilter.MaxFilter(5))
    bg=Image.new('RGB',(w,h),CREAM)
    return Image.composite(src,bg,keep)

def crop_to_full_hole(im):
    bg=Image.new('RGB',im.size,CREAM)
    diff=ImageChops.difference(im,bg).convert('L')
    mask=diff.point(lambda v:255 if v>18 else 0)
    bbox=mask.getbbox()
    if not bbox:return im
    l,t,r,b=bbox;pad=max(10,round(max(im.size)*.018))
    return im.crop((max(0,l-pad),max(0,t-pad),min(im.width,r+pad),min(im.height,b+pad)))

def toon_grade(im):
    # Geometry-preserving visual conversion only: no generated or invented layout.
    im=clean_border_matte(im)
    im=strip_outside_course(im)
    im=crop_to_full_hole(im)

    longest=max(im.size);target=1800
    if longest<target:
        scale=target/float(longest)
        im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)

    # Soft painted surface + limited animation-cell palette.
    smooth=im.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.SMOOTH_MORE)
    base=Image.blend(im,smooth,.55)
    base=ImageEnhance.Color(base).enhance(1.27)
    base=ImageEnhance.Contrast(base).enhance(1.10)
    base=ImageEnhance.Brightness(base).enhance(1.04)
    cell=base.quantize(colors=48,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
    base=Image.blend(base,cell,.64)

    # Concept-art dark-green ink edge, deliberately softer than a technical map.
    edges=base.convert('L').filter(ImageFilter.FIND_EDGES)
    edges=ImageOps.autocontrast(edges)
    alpha=edges.point(lambda v:0 if v<74 else min(94,int((v-74)*.80)))
    contour=Image.new('RGBA',base.size,INK+(0,));contour.putalpha(alpha)
    out=Image.alpha_composite(base.convert('RGBA'),contour).convert('RGB')
    out=out.filter(ImageFilter.UnsharpMask(radius=.9,percent=70,threshold=3))
    return out

manifest=[];samples=[]
for p in FILES:
    with Image.open(p) as src:
        before=src.size;out=toon_grade(src)
    out.save(p,'JPEG',quality=96,subsampling=0,optimize=True,progressive=True)
    manifest.append(f'{p.name}\t{before[0]}x{before[1]} -> {out.width}x{out.height}')
    if p.name in {'yardage_kamishihoro_c01.jpg','yardage_furano_palmer15.jpg','yardage_sahoro_13.jpg','yardage_royallinks_queens01.jpg'}:
        samples.append((p.name,out.copy()))

(TMP/'manifest.txt').write_text('\n'.join(manifest)+'\n')
if samples:
    W=1400;tile_w=330;tile_h=660
    sheet=Image.new('RGB',(W,760),CREAM);d=ImageDraw.Draw(sheet)
    try:
        f=ImageFont.truetype('/tmp/Jua-Regular.ttf',26);sf=ImageFont.truetype('/tmp/Jua-Regular.ttf',20)
    except Exception:f=sf=None
    d.text((35,25),'V1.13.0 · ANIMATION YARDAGE',fill=INK,font=f)
    for idx,(name,im) in enumerate(samples[:4]):
        x=30+idx*340;y=75;sc=min(tile_w/im.width,tile_h/im.height)
        thumb=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.LANCZOS)
        bx=x+(tile_w-thumb.width)//2;by=y+(tile_h-thumb.height)//2
        sheet.paste(thumb,(bx,by));d.rounded_rectangle((x,y,x+tile_w,y+tile_h),radius=26,outline=GREEN,width=4)
        d.text((x+10,705),name.replace('yardage_','').replace('.jpg',''),fill=INK,font=sf)
    sheet.save(TMP/'yardage-concept-samples.jpg','JPEG',quality=94,subsampling=0)

print('V1.13.0 126 yardages converted to high-res animation-cell style')
print('sample sheet:',TMP/'yardage-concept-samples.jpg')
