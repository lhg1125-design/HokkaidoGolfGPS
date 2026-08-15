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
    # The user-approved 408_2.webp is 21,048 Base64 chars and is intentionally
    # split into four equal 5,262-char repository parts.  All four are required.
    text=''.join((ASSET/f'king02.part{i}').read_text().strip() for i in (1,2,3,4))
    return base64.b64decode(text,validate=True)

def decoded_h3():
    return base64.b64decode((ASSET/'king03.b64').read_text().strip(),validate=True)

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
    # Materialize the exact user-approved GORA geometry onto a neutral page for
    # the existing golden-base extractor.  No crop, warp, rotation or redraw.
    page=Image.new('RGBA',im.size,(247,244,232,255))
    page.alpha_composite(im)
    dst=RES/f'yardage_furano_king{h:02d}.jpg'
    page.convert('RGB').save(dst,format='PNG',optimize=True)
    print(f'LOCKED Furano KING H{h}: approved 408_{h}.webp sha256={sha} size={im.size} -> {dst}')

lock(2,decoded_h2())
lock(3,decoded_h3())
