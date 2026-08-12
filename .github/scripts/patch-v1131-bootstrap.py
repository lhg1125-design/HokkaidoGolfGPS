from pathlib import Path

p=Path('.github/scripts/patch-v1131.py')
s=p.read_text()
old="""if 'V1.13.0 · CONCEPT ART SKIN' not in s:\n    raise SystemExit('v1.13.1 requires v1.13.0 concept-art skin')\ns=s.replace('V1.13.0 · CONCEPT ART SKIN','V1.13.1 · NAEPO FIELD TEST',1)"""
new="""build_anchor='        private final boolean previewMode;'\nif build_anchor not in s:\n    raise SystemExit('v1.13.1 stable GolfView anchor missing')\ns=s.replace(build_anchor,build_anchor+'\\n        private static final String BUILD_V1131=\"V1.13.1 · NAEPO FIELD TEST\";',1)"""
if old not in s:
    raise SystemExit('v1.13.1 bootstrap could not find strict version precondition')
p.write_text(s.replace(old,new,1))
print('bootstrapped v1.13.1 patch to stable source anchor')
