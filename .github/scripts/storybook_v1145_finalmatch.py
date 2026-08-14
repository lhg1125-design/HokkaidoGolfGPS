from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np

ROOT=Path('app/src/main/res/drawable-nodpi')

# Final visual pass on the already geometry-derived storybook maps.
# 1) use more of the phone width (reference composition),
# 2) remove thin beige publisher/cart-guide remnants that can look like bunkers.
for fp in sorted(ROOT.glob('yardage_*.jpg')):
    with Image.open(fp) as src:
        im=src.convert('RGB')
    w,h=im.size
    # Center crop 8% each side then return to the fixed 1200x1800 canvas.
    # Vertical TEE->GREEN mapping is untouched; centerline remains centered.
    cut=round(w*.08)
    im=im.crop((cut,0,w-cut,h)).resize((w,h),Image.Resampling.LANCZOS)

    a=np.asarray(im).astype(np.int16)
    cream=np.array([250,226,158],dtype=np.int16)
    edge=np.array([203,166,96],dtype=np.int16)
    d1=np.sqrt(((a-cream)**2).sum(axis=2))
    d2=np.sqrt(((a-edge)**2).sum(axis=2))
    raw=((d1<52)|(d2<42)).astype(np.uint8)*255
    mask=Image.fromarray(raw,'L').resize((w//2,h//2),Image.Resampling.NEAREST)
    # Erode then regrow: thin label/guide strips disappear; bunker-sized islands survive.
    mask=mask.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(13))
    mask=mask.resize((w,h),Image.Resampling.BILINEAR)

    # Remove all old beige/border pixels first, then paint only the cleaned organic islands.
    old=Image.fromarray(raw,'L')
    fair=Image.new('RGB',(w,h),(127,205,75))
    base=Image.composite(fair,im,old)
    bunker=Image.new('RGB',(w,h),(250,226,158))
    out=Image.composite(bunker,base,mask)
    out.save(fp,'JPEG',quality=95,subsampling=0,optimize=True,progressive=True)

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

# Ensure every yardage/play footer uses the same dark-green storybook navigation.
# This is deliberately applied after all legacy patches, so old cream/golden footers cannot win.
s=s.replace('drawGoldenNav(c);','drawStorybookBottomNavV1140(c);')

# Friendlier visible calibration controls while preserving their exact touch functions.
s=s.replace('"GREEN CENTER"','"그린 저장"')
s=s.replace('"TEE OK"','"티 위치"')
s=s.replace('"외부 지도"','"타겟 지도"')

# Raise the course-strategy copy to a readable floor on 720/768px-wide phones.
s=s.replace('text(c,"공략",strategy.left+10,h*.870f,8.6f,GREEN,true);','text(c,"공략",strategy.left+10,h*.870f,9.6f,GREEN,true);')
s=s.replace('textFit(c,fieldGuideV1100(),strategy.left+52,h*.870f,strategy.right-8,8.0f,INK,true);','textFit(c,fieldGuideV1100(),strategy.left+56,h*.870f,strategy.right-8,9.1f,INK,true);')

p.write_text(s)
print('V1.14.5 FINAL MATCH: wider storybook maps + thin false-bunker cleanup + dark readable yardage nav')
