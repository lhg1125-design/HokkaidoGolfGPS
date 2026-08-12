from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont

ROOT=Path('app/src/main/res/drawable-nodpi')
TMP=Path('.github/tmp/v1130')
TMP.mkdir(parents=True,exist_ok=True)
FILES=sorted(ROOT.glob('yardage_*.jpg'))
if len(FILES)!=126:
    raise SystemExit(f'V1.13.0 expects 126 full-hole JPGs, got {len(FILES)}')

CREAM=(249,249,231)
INK=(54,80,54)
GREEN=(76,157,91)

def replace_dead_black(im):
    # Published maps sometimes carry a pure-black matte around the actual hole.
    # Replace only near-black pixels, not normal shaded course detail.
    src=im.convert('RGB')
    px=src.load(); w,h=src.size
    for y in range(h):
        for x in range(w):
            r,g,b=px[x,y]
            if r<24 and g<24 and b<24:
                px[x,y]=CREAM
    return src

def toon_grade(im):
    # Preserve geometry while converting photographic/published course art to
    # the bright, rounded illustration language of the approved concept art.
    im=replace_dead_black(im)
    longest=max(im.size)
    target=1800
    if longest<target:
        scale=target/float(longest)
        im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    # Gentle paint-like smoothing, blended back with the original to retain
    # bunkers, water edges and cart paths.
    smooth=im.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.SMOOTH_MORE)
    base=Image.blend(im,smooth,.55)
    base=ImageEnhance.Color(base).enhance(1.20)
    base=ImageEnhance.Contrast(base).enhance(1.08)
    base=ImageEnhance.Brightness(base).enhance(1.035)
    # Soft posterisation gives an animation-cell feel without moving geometry.
    post=ImageOps.posterize(base,6)
    base=Image.blend(base,post,.42)

    # Add restrained dark-green contouring only on strong edges.
    edges=base.convert('L').filter(ImageFilter.FIND_EDGES)
    edges=ImageOps.autocontrast(edges)
    alpha=edges.point(lambda v: 0 if v<72 else min(82,int((v-72)*0.75)))
    contour=Image.new('RGBA',base.size,INK+(0,))
    contour.putalpha(alpha)
    out=Image.alpha_composite(base.convert('RGBA'),contour).convert('RGB')
    out=out.filter(ImageFilter.UnsharpMask(radius=1.1,percent=82,threshold=3))
    return out

manifest=[]
samples=[]
for i,p in enumerate(FILES):
    with Image.open(p) as src:
        before=src.size
        out=toon_grade(src)
    out.save(p,'JPEG',quality=96,subsampling=0,optimize=True,progressive=True)
    manifest.append(f'{p.name}\t{before[0]}x{before[1]} -> {out.width}x{out.height}')
    if p.name in {
        'yardage_kamishihoro_c01.jpg','yardage_furano_palmer15.jpg',
        'yardage_sahoro_13.jpg','yardage_royallinks_queens01.jpg'}:
        samples.append((p.name,out.copy()))

(TMP/'manifest.txt').write_text('\n'.join(manifest)+'\n')

# CI contact sheet for quick visual gating.
if samples:
    W=1400; tile_w=330; tile_h=660
    sheet=Image.new('RGB',(W,760),CREAM)
    d=ImageDraw.Draw(sheet)
    try:
        f=ImageFont.truetype('/tmp/Jua-Regular.ttf',26)
        sf=ImageFont.truetype('/tmp/Jua-Regular.ttf',20)
    except Exception:
        f=sf=None
    d.text((35,25),'V1.13.0 · CONCEPT ART YARDAGE',fill=INK,font=f)
    for idx,(name,im) in enumerate(samples[:4]):
        x=30+idx*340; y=75
        sc=min(tile_w/im.width,tile_h/im.height)
        thumb=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.LANCZOS)
        bx=x+(tile_w-thumb.width)//2
        sheet.paste(thumb,(bx,y))
        d.rounded_rectangle((x,y,x+tile_w,y+tile_h),radius=26,outline=GREEN,width=4)
        label=name.replace('yardage_','').replace('.jpg','')
        d.text((x+10,705),label,fill=INK,font=sf)
    sheet.save(TMP/'yardage-concept-samples.jpg','JPEG',quality=94,subsampling=0)

print('V1.13.0 stylized yardage assets:',len(FILES))
print('sample sheet:',TMP/'yardage-concept-samples.jpg')
