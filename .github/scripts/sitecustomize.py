from pathlib import Path
import base64

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
