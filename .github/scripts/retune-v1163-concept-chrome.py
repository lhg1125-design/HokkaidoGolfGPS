from pathlib import Path
from PIL import Image
import numpy as np, hashlib

# V1.16.3 CONCEPT REFERENCE LOCK
# Retunes the existing approved layout to the user-supplied H2/H3 concept:
# deeper blue header, darker walnut board, deep green score panel, warmer paper,
# parchment bubble, richer gold target. Geometry/layout remains unchanged.
RES=Path('app/src/main/res/drawable-nodpi')
ARES=Path('app/src/main/assets')
fp=RES/'master_golden_chrome_v1162.webp'
if not fp.exists(): raise SystemExit('V1.16.3 requires master_golden_chrome_v1162.webp')
im=Image.open(fp).convert('RGBA')
a=np.asarray(im).astype(np.float32)
Y,X=np.indices(a.shape[:2]); r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]

# Header: user concept is deeper royal/navy blue. Preserve white icons/text pixels.
m=(Y<156)&(b>105)&(b>g*1.28)&(b>r*2.2)
a[m,0]=np.clip(a[m,0]*1.05,0,255)
a[m,1]=np.clip(a[m,1]*0.79,0,255)
a[m,2]=np.clip(a[m,2]*0.93,0,255)

# Walnut board: concept is substantially darker/richer than the washed runtime master.
m=(Y>=156)&(Y<350)&(r>62)&(r>g*1.10)&(g>b*1.10)&~((g>r*1.15)&(g>b*1.35))
a[m,0]*=.64; a[m,1]*=.56; a[m,2]*=.52

# Deep score panel. Keep player chips/white text untouched by restricting to green-dominant pixels.
m=(X>=18)&(X<238)&(Y>=477)&(Y<1328)&(g>r*1.35)&(g>b*1.45)&(g<190)
a[m,0]=np.clip(a[m,0]*.98+3,0,255); a[m,1]*=.64; a[m,2]*=.42

# Warm cream paper: closer to the uploaded concept, without touching controls/nav/header.
m=(Y>=350)&(Y<1458)&(r>205)&(g>188)&(b>145)&((r-g)<48)&((g-b)<72)
# Exclude bubble/target so each can be tuned independently.
m &= ~((X>=700)&(X<930)&(Y>=380)&(Y<595))
m &= ~((X>=610)&(X<930)&(Y>=1225)&(Y<1415))
a[m,0]*=.975; a[m,1]*=.945; a[m,2]*=.885

# Parchment remaining-distance bubble.
m=(X>=700)&(X<930)&(Y>=380)&(Y<595)&(r>190)&(g>175)&(b>135)
a[m,0]*=.88; a[m,1]*=.84; a[m,2]*=.78

# Rich amber-gold target control from the concept (not pale beige).
m=(X>=610)&(X<930)&(Y>=1225)&(Y<1415)&(r>170)&(g>130)&(b>75)
a[m,0]*=.86; a[m,1]*=.72; a[m,2]*=.48

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
text += 'v1163_chrome_sha256='+sha+'\n'
lock.write_text(text)
print('V1.16.3 CONCEPT CHROME RETUNED',fp,sha)
