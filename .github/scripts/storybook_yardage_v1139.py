from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont

ROOT=Path('app/src/main/res/drawable-nodpi')
OUT=Path('.github/tmp/v1139-storybook')
OUT.mkdir(parents=True,exist_ok=True)
files=sorted(ROOT.glob('yardage_*.jpg'))
if len(files)!=135:
    raise SystemExit(f'storybook yardage expects 135 JPGs, got {len(files)}')
INK=(48,78,52);CREAM=(250,248,224)

def storybook(im):
    src=im.convert('RGB')
    soft=src.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.SMOOTH_MORE)
    base=Image.blend(src,soft,.58)
    base=ImageEnhance.Color(base).enhance(1.20)
    base=ImageEnhance.Contrast(base).enhance(1.07)
    base=ImageEnhance.Brightness(base).enhance(1.035)
    poster=base.quantize(colors=44,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB')
    base=Image.blend(base,poster,.67)
    edges=base.convert('L').filter(ImageFilter.FIND_EDGES);edges=ImageOps.autocontrast(edges)
    alpha=edges.point(lambda v:0 if v<78 else min(72,int((v-78)*.48)))
    contour=Image.new('RGBA',base.size,INK+(0,));contour.putalpha(alpha)
    out=Image.alpha_composite(base.convert('RGBA'),contour).convert('RGB')
    glow=out.filter(ImageFilter.GaussianBlur(radius=1.1));out=Image.blend(out,glow,.10)
    return out.filter(ImageFilter.UnsharpMask(radius=.8,percent=58,threshold=4))

samples=[]
sample_names={'yardage_kamishihoro_c11.jpg','yardage_furano_palmer15.jpg','yardage_sahoro_07.jpg','yardage_royallinks_queens07.jpg','yardage_royallinks_kings10.jpg','yardage_naepo_06.jpg'}
for fp in files:
    with Image.open(fp) as im: out=storybook(im)
    out.save(fp,'JPEG',quality=96,subsampling=0,optimize=True,progressive=True)
    if fp.name in sample_names:samples.append((fp.name,out.copy()))

if samples:
    tile_w,tile_h=330,600;W=1090;H=1420
    sheet=Image.new('RGB',(W,H),CREAM);d=ImageDraw.Draw(sheet)
    try:font=ImageFont.truetype('/tmp/Jua-Regular.ttf',27);sf=ImageFont.truetype('/tmp/Jua-Regular.ttf',18)
    except Exception:font=sf=None
    d.text((30,24),'STORYBOOK YARDAGE PROOF',fill=INK,font=font)
    for i,(name,im) in enumerate(samples[:6]):
        col=i%3;row=i//3;x=30+col*350;y=78+row*665;sc=min(tile_w/im.width,tile_h/im.height);th=im.resize((round(im.width*sc),round(im.height*sc)),Image.Resampling.LANCZOS);sheet.paste(th,(x+(tile_w-th.width)//2,y+(tile_h-th.height)//2));d.rounded_rectangle((x,y,x+tile_w,y+tile_h),radius=25,outline=(75,147,79),width=4);d.text((x+8,y+612),name.replace('yardage_','').replace('.jpg',''),fill=INK,font=sf)
    sheet.save(OUT/'storybook-yardage-proof.jpg','JPEG',quality=94,subsampling=0)
(OUT/'README.txt').write_text('storybook visual-only filter; no crop, resize or warp; GPS geometry unchanged\n')
print('storybook yardage finish applied:',len(files))
