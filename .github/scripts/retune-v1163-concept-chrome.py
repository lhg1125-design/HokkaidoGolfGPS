from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, hashlib

# V1.16.3 CONCEPT REFERENCE LOCK
# Retunes the approved layout to the user-supplied H2/H3 concept while keeping
# every layout coordinate and course geometry unchanged.
RES=Path('app/src/main/res/drawable-nodpi')
ARES=Path('app/src/main/assets')
fp=RES/'master_golden_chrome_v1162.webp'
if not fp.exists(): raise SystemExit('V1.16.3 requires master_golden_chrome_v1162.webp')
im=Image.open(fp).convert('RGBA')
a=np.asarray(im).astype(np.float32)
H,W=a.shape[:2]
Y,X=np.indices((H,W)); r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]

# Exact control silhouettes. The uploaded concept has no rectangular color blocks
# around either control; only the rounded/tail shapes are tinted.
shape=Image.new('L',(W,H),0); sd=ImageDraw.Draw(shape)
sd.rounded_rectangle((714,397,918,575),radius=28,fill=255)
sd.polygon([(720,527),(694,575),(752,551)],fill=255)
bubble_shape=np.asarray(shape)>0
shape=Image.new('L',(W,H),0); sd=ImageDraw.Draw(shape)
sd.rounded_rectangle((638,1261,908,1388),radius=48,fill=255)
target_shape=np.asarray(shape)>0

# Header: deeper royal/navy blue, preserving bright icons/text.
m=(Y<156)&(b>105)&(b>g*1.28)&(b>r*2.2)
a[m,0]=np.clip(a[m,0]*1.05,0,255)
a[m,1]=np.clip(a[m,1]*0.79,0,255)
a[m,2]=np.clip(a[m,2]*0.93,0,255)

# Dark walnut board from the uploaded concept.
m=(Y>=156)&(Y<350)&(r>62)&(r>g*1.10)&(g>b*1.10)&~((g>r*1.15)&(g>b*1.35))
a[m,0]*=.64; a[m,1]*=.56; a[m,2]*=.52
# Bright synthetic grain was the main reason the board still looked unlike the
# reference. Subdue only the tan grain lines; leave white labels and green leaves.
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]\mgrain=(Y>=156)&(Y<350)&(r>108)&(g>62)&(b>32)&~((r>205)&(g>195)&(b>180))&~((g>r*1.10)&(g>b*1.20))
a[grain,0]*=.68; a[grain,1]*=.60; a[grain,2]*=.54

# Deep green score panel. Player chips and white text are excluded by color.
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
m=(X>=18)&(X<238)&(Y>=477)&(Y<1328)&(g>r*1.35)&(g>b*1.45)&(g<190)
a[m,0]=np.clip(a[m,0]*.98+3,0,255); a[m,1]*=.64; a[m,2]*=.42

# Warm cream paper. Exclude only the actual bubble/target silhouettes, not their
# rectangular bounding boxes. This removes the visible square patches.
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
m=(Y>=350)&(Y<1458)&(r>205)&(g>188)&(b>145)&((r-g)<48)&((g-b)<72)
m &= ~bubble_shape
m &= ~target_shape
a[m,0]*=.975; a[m,1]*=.945; a[m,2]*=.885

# Parchment bubble itself: target ~240/222/190 from the uploaded concept.
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
m=bubble_shape&(r>220)&(g>205)&(b>175)
a[m,0]*=.945; a[m,1]*=.900; a[m,2]*=.850

# Amber-gold target itself: target ~217/169/83 from the uploaded concept.
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
m=target_shape&(r>190)&(g>165)&(b>115)
a[m,0]*=.890; a[m,1]*=.790; a[m,2]*=.515

out=Image.fromarray(np.clip(a,0,255).astype(np.uint8),'RGBA')
out.save(fp,'WEBP',lossless=True,method=6)
sha=hashlib.sha256(fp.read_bytes()).hexdigest()
lock=ARES/'master_golden_v1162.lock'
text=lock.read_text() if lock.exists() else ''
if 'V1.16.3 CONCEPT REFERENCE LOCK' not in text:
    text += ('V1.16.3 CONCEPT REFERENCE LOCK\n'
             'reference=user-supplied Furano H2/H3 concept 2026-08-16\n'
             'palette=deep-blue+dark-walnut+deep-green+warm-paper+amber-target\n'
             'geometry=unchanged\n')
text += 'control_tint=shape-only-no-rectangular-blocks\n'
text += 'v1163_chrome_sha256='+sha+'\n'
lock.write_text(text)
print('V1.16.3 CONCEPT CHROME RETUNED SHAPE-ONLY',fp,sha)
