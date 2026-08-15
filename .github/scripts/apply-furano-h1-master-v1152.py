from pathlib import Path
from PIL import Image
import base64, hashlib, io

ASSET=Path('.github/assets/furano-v1152')
RES=Path('app/src/main/res/drawable-nodpi')
PARTS=[ASSET/f'king01_master_q85.part{i}' for i in range(1,9)]
for p in PARTS:
    if not p.exists(): raise SystemExit(f'missing H1 golden master part: {p}')

text=''.join(p.read_text().strip() for p in PARTS)
raw=base64.b64decode(text,validate=True)
sha=hashlib.sha256(raw).hexdigest()
EXPECTED='e0a3e18b07a6b10f32ef04d9751afc3c300c1417bfac9955d585a5c2b9c12254'
if sha!=EXPECTED:
    raise SystemExit(f'Furano KING H1 golden texture hash mismatch: {sha} != {EXPECTED}')
master=Image.open(io.BytesIO(raw)).convert('RGBA')
if master.size!=(365,1062):
    raise SystemExit(f'Furano KING H1 golden texture size mismatch: {master.size}')

base_path=RES/'furano_king_h1_base_v1152.webp'
if not base_path.exists(): raise SystemExit('H1 base must be generated first')
base=Image.open(base_path).convert('RGBA')
if base.size!=(941,1672): raise SystemExit(f'unexpected H1 base size: {base.size}')

# Preserve the approved target button before replacing the central course sprite.
target_box=(625,1245,920,1410)
target=base.crop(target_box)

# V1.15.5 normalization: erase only the exact H1 course slot. The previous
# x=690 erase boundary cut the left 44px of the approved 200m badge (x=646..777).
# The generated H1 course never extends beyond x=625, so x=632 is sufficient to
# clean the old sprite while preserving the complete ruler/badge chrome.
pix=base.load()
for y in range(350,1458):
    t=max(0.0,min(1.0,(y-350)/(1458-350)))
    r=round(247*(1-t)+234*t); g=round(239*(1-t)+220*t); b=round(214*(1-t)+184*t)
    for x in range(250,632): pix[x,y]=(r,g,b,255)

# Exact approved H1 course pixels at the locked app coordinates.
base.alpha_composite(master,(260,390))
base.alpha_composite(target,target_box[:2])
base.save(base_path,'WEBP',lossless=True,method=6)
print(f'FURANO KING H1 GOLDEN LOCK: sha256={sha} size={master.size} position=(260,390)-(625,1452); 200m badge preserved')
