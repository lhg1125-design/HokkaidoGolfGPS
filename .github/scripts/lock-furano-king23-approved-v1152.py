from pathlib import Path
from PIL import Image
import base64, hashlib, io

ASSET=Path('.github/assets/furano-v1152')
RES=Path('app/src/main/res/drawable-nodpi')

EXPECTED={
    2:('f3b5e0aa30f8293b58640c915d584f975b942bb1f958727578f62c9c59987456',(127,400)),
    3:('9ac4a1259140064168f1c2e122240e0463b4ac118e1f935af0f819beeb8fa171',(99,400)),
}

def decoded_h2():
    text=''.join((ASSET/f'king02.part{i}').read_text().strip() for i in (1,2,3))
    return base64.b64decode(text)

def decoded_h3():
    return base64.b64decode((ASSET/'king03.b64').read_text().strip())

def lock(h, raw):
    sha=hashlib.sha256(raw).hexdigest()
    exp_sha,exp_size=EXPECTED[h]
    if sha!=exp_sha:
        raise SystemExit(f'Furano KING H{h} approved source hash mismatch: {sha} != {exp_sha}')
    im=Image.open(io.BytesIO(raw)).convert('RGBA')
    if im.size!=exp_size:
        raise SystemExit(f'Furano KING H{h} approved source size mismatch: {im.size} != {exp_size}')
    alpha=im.getchannel('A')
    lo,hi=alpha.getextrema()
    if lo>=255:
        raise SystemExit(f'Furano KING H{h} approved source lost transparency')
    # Existing golden-base generator reads the yardage JPG path and removes only
    # edge-connected neutral page background.  Materialize the USER-APPROVED
    # Rakuten GORA WebP on that neutral canvas without changing map coordinates,
    # orientation, aspect ratio or internal pixels.
    page=Image.new('RGBA',im.size,(247,244,232,255))
    page.alpha_composite(im)
    dst=RES/f'yardage_furano_king{h:02d}.jpg'
    page.convert('RGB').save(dst,format='PNG',optimize=True)
    # PNG bytes under the legacy .jpg resource name are intentional: Pillow and
    # Android identify image data by content, while the old 135-file resource
    # naming/count contract remains unchanged.
    print(f'LOCKED Furano KING H{h}: approved 408_{h}.webp sha256={sha} size={im.size} -> {dst}')

lock(2,decoded_h2())
lock(3,decoded_h3())
