from pathlib import Path
from PIL import Image

src=Path('.github/assets/app_icon_source.jpg')
out=Path('app/src/main/res/drawable-nodpi/ic_hokkaido_launcher.jpg')
out.parent.mkdir(parents=True,exist_ok=True)
with Image.open(src) as im:
    im=im.convert('RGB').resize((256,256),Image.Resampling.LANCZOS)
    im.save(out,'JPEG',quality=92,optimize=True,subsampling=0)
with Image.open(out) as check:
    check.verify()
print('launcher icon generated and verified:',out)
