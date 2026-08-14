from pathlib import Path
import base64
import atexit
import sys

# CI launcher hotfix: materialize the selected Hokkaido Golf GPS icon from the
# text-safe Base64 asset before any build helper tries to open the JPEG.
root = Path(__file__).resolve().parents[2]
asset_dir = root / '.github' / 'assets'
out = asset_dir / 'app_icon_source.jpg'

if not out.exists():
    candidates = sorted(asset_dir.glob('*icon*.b64')) + sorted(asset_dir.glob('*launcher*.b64'))
    if candidates:
        raw = ''.join(candidates[0].read_text(encoding='utf-8').split())
        out.write_bytes(base64.b64decode(raw, validate=True))

# patch-v1138 imports the Storybook UI as its final layer. Apply the small
# navigation compatibility correction immediately after that script finishes,
# without changing the established workflow chain.
def _storybook_nav_compat_fix():
    if not sys.argv or not sys.argv[0].endswith('patch-v1138.py'):
        return
    java = root / 'app' / 'src' / 'main' / 'java' / 'com' / 'hokkaidogolf' / 'trip' / 'FieldGpsV09Activity.java'
    if not java.exists():
        return
    s = java.read_text()
    old = 'speech(c,w*.19f,h*.777f,"한눈에 보고, 한 번에 입력!",DEEP);nav(c);'
    new = 'speech(c,w*.19f,h*.777f,"한눈에 보고, 한 번에 입력!",DEEP);setFourNav(w,h);drawGoldenNav(c);'
    if old in s:
        java.write_text(s.replace(old, new, 1))
        print('storybook navigation compatibility fix applied')

atexit.register(_storybook_nav_compat_fix)
