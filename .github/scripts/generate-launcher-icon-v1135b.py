from pathlib import Path
from io import BytesIO
import base64
from PIL import Image

src=Path('.github/assets/app_icon_source.jpg.b64')
out=Path('app/src/main/res/drawable-nodpi/ic_hokkaido_launcher.jpg')
raw=base64.b64decode(''.join(src.read_text().split()), validate=True)
with Image.open(BytesIO(raw)) as im:
    im.load()
    im=im.convert('RGB').resize((256,256),Image.Resampling.LANCZOS)
    out.parent.mkdir(parents=True,exist_ok=True)
    im.save(out,'JPEG',quality=92,optimize=True,subsampling=0)
with Image.open(out) as check:
    check.verify()
print('launcher icon verified', out, out.stat().st_size)
