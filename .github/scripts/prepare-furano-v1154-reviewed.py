from pathlib import Path

p=Path('.github/scripts/generate-furano-king123-v1152.py')
s=p.read_text()

# V1.15.5 normalization rules:
# 1) H2/H3 are generated only from the exact user-approved 408_2/408_3 sources.
# 2) Approved app chrome is created in the frozen base itself.
# 3) Course geometry is never warped/rotated/redrawn. Only alpha-tight crop,
#    high-quality scale and mild display color/contrast/sharpening are allowed.
# 4) One ruler only; no runtime duplicate ruler/200m marker in preview.

repls={
    "top=max(150,int(math.ceil(total/50))*50)":"top={1:250,2:250,3:400}[hole]",
    "if total>=200:":"if top>=200:",
    "build(1,4,(274,286,298));build(2,3,(142,154,166));build(3,4,(355,367,379))":"build(1,4,(393,412,430));build(2,3,(142,154,166));build(3,4,(355,367,379))",
}
for old,new in repls.items():
    if old in s:
        s=s.replace(old,new,1)
    elif new not in s:
        raise SystemExit(f'V1.15.5 reviewed generator anchor missing: {old}')

# Add ImageEnhance for display-only color/contrast recovery on approved H2/H3.
old='from PIL import Image, ImageDraw, ImageFont, ImageFilter'
new='from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance'
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('V1.15.5 PIL import anchor missing')

# Alpha-tight crop removes only transparent/neutral exterior.
old="    return Image.fromarray(np.dstack([a,alpha]),'RGBA')"
new="    out=Image.fromarray(np.dstack([a,alpha]),'RGBA')\n    bbox=out.getbbox()\n    return out.crop(bbox) if bbox else out"
if old in s:
    s=s.replace(old,new,1)
elif "return out.crop(bbox) if bbox else out" not in s:
    raise SystemExit('V1.15.5 alpha-tight crop anchor missing')

# Keep the visible course entirely below the wood board and above app nav.
old="SAFE=(260,365,680,1422)\ndef contain(im):\n    x0,y0,x1,y1=SAFE;sc=min((x1-x0)/im.width,(y1-y0)/im.height);ww=im.width*sc;hh=im.height*sc\n    return x0+(x1-x0-ww)/2,y0+(y1-y0-hh)/2,ww,hh"
new="SAFE_BY_HOLE={1:(260,390,625,1452),2:(275,340,675,1445),3:(315,340,645,1445)}\ndef contain(im,hole):\n    x0,y0,x1,y1=SAFE_BY_HOLE[hole];sc=min((x1-x0)/im.width,(y1-y0)/im.height);ww=im.width*sc;hh=im.height*sc\n    return x0+(x1-x0-ww)/2,y0+(y1-y0-hh)/2,ww,hh"
if old in s:
    s=s.replace(old,new,1)
elif 'SAFE_BY_HOLE=' not in s:
    raise SystemExit('V1.15.5 safe-slot anchor missing')
s=s.replace('x,y,ww,hh=contain(ci);','x,y,ww,hh=contain(ci,hole);',1)

# Recover the richer approved preview appearance without changing shape/alpha.
old="cr=ci.resize((round(ww),round(hh)),Image.Resampling.LANCZOS);sh=Image.new('RGBA',cr.size,(0,0,0,0))"
new="cr=ci.resize((round(ww),round(hh)),Image.Resampling.LANCZOS);cr=ImageEnhance.Color(cr).enhance(1.08);cr=ImageEnhance.Contrast(cr).enhance(1.06);cr=cr.filter(ImageFilter.UnsharpMask(radius=.85,percent=145,threshold=2));sh=Image.new('RGBA',cr.size,(0,0,0,0))"
if old in s:
    s=s.replace(old,new,1)
elif 'ImageEnhance.Color(cr).enhance(1.08)' not in s:
    # replace the first V1.15.5 sharpening variant if present
    old2="cr=ci.resize((round(ww),round(hh)),Image.Resampling.LANCZOS);cr=cr.filter(ImageFilter.UnsharpMask(radius=1.0,percent=115,threshold=2));sh=Image.new('RGBA',cr.size,(0,0,0,0))"
    if old2 in s:s=s.replace(old2,new,1)
    else:raise SystemExit('V1.15.5 resize anchor missing')

# Full approved blue header directly in frozen base.
anchor="HEADER=Image.fromarray(ha,'RGBA');HEADER.alpha_composite(HEADER_SOURCE.crop((25,87,100,150)),(25,87))"
header_patch=r'''HEADER=Image.fromarray(ha,'RGBA');HEADER.alpha_composite(HEADER_SOURCE.crop((25,87,100,150)),(25,87))
# V1.15.5 full-screen approved header chrome.
hd=ImageDraw.Draw(HEADER,'RGBA')
hd.line((59,30,34,53,59,76),fill=(255,255,255,255),width=7,joint='curve');hd.line((36,53,78,53),fill=(255,255,255,255),width=7)
txt(hd,(94,54),'후라노 골프코스',39,(255,255,255,255),anchor='lm',stroke=1,sf=(0,48,125,180))
# stable car/course icon before KING label
hd.rounded_rectangle((35,99,70,124),radius=6,outline=(255,255,255,255),width=4);hd.line((43,99,49,90,62,90,68,99),fill=(255,255,255,255),width=4);hd.ellipse((40,119,49,128),fill=(255,255,255,255));hd.ellipse((58,119,67,128),fill=(255,255,255,255))
# fixed sunny-cloud weather artwork
hd.ellipse((758,27,792,61),fill=(255,193,0,255))
for x0,y0,x1,y1 in [(775,12,775,22),(775,66,775,76),(741,44,751,44),(799,44,809,44),(751,20,758,27),(792,61,799,68),(751,68,758,61),(792,27,799,20)]: hd.line((x0,y0,x1,y1),fill=(255,193,0,255),width=4)
hd.ellipse((744,48,777,75),fill=(255,255,255,255));hd.ellipse((764,40,804,76),fill=(255,255,255,255));hd.rounded_rectangle((741,57,811,79),radius=10,fill=(255,255,255,255))
txt(hd,(895,54),'22°C',31,(255,255,255,255),anchor='rm',stroke=1,sf=(0,48,125,180),jp=True)'''
if anchor in s:
    s=s.replace(anchor,header_patch,1)
elif 'V1.15.5 full-screen approved header chrome' not in s:
    raise SystemExit('V1.15.5 header anchor missing')

p.write_text(s)
print('V1.15.5 NORMALIZE: exact 408 H2/H3 + full header + no clipping + restored display texture')
