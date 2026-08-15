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

# Preserve the approved target button before removing the old tiny H1 course.
target_box=(625,1245,920,1410)
target=base.crop(target_box)

# Erase ONLY the central course slot. This cannot touch the left score panel,
# remaining-distance bubble, wood board or bottom nav. Background matches the
# V1.15.2 base generator exactly.
pix=base.load()
for y in range(350,1458):
    t=max(0.0,min(1.0,(y-350)/(1458-350)))
    r=round(247*(1-t)+234*t); g=round(239*(1-t)+220*t); b=round(214*(1-t)+184*t)
    for x in range(250,690): pix[x,y]=(r,g,b,255)

# Exact PASS master pixels, fixed at the approved app coordinates.
# No resizing, crop, warp, redraw, texture synthesis or geometry inference.
base.alpha_composite(master,(260,390))
base.alpha_composite(target,target_box[:2])
base.save(base_path,'WEBP',lossless=True,method=6)
print(f'FURANO KING H1 GOLDEN LOCK: sha256={sha} size={master.size} position=(260,390)-(625,1452)')
