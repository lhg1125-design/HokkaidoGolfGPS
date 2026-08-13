from pathlib import Path

p=Path('.github/scripts/patch-v1135.py')
t=p.read_text()

# V1.13.5 must replace only the target Java method itself. Earlier helper
# methods (hole-step controls, saveGreenPoint, etc.) intentionally live between
# target methods in the accumulated patch chain and must not be swallowed.
def harden(start_sig, old_end_line, old_guard, label):
    global t
    old=f"""a=s.find('{start_sig}')\n{old_end_line}\n{old_guard}"""
    new=f"""a=s.find('{start_sig}')\nif a<0: raise SystemExit('{label} method start missing')\nbrace=s.find('{{',a);depth=0;b=-1\nfor ii in range(brace,len(s)):\n    ch=s[ii]\n    if ch=='{{': depth+=1\n    elif ch=='}}':\n        depth-=1\n        if depth==0:\n            b=ii+1\n            while b<len(s) and s[b]=='\\n': b+=1\n            break\nif b<0: raise SystemExit('{label} method end missing')"""
    if old not in t:
        raise SystemExit(f'V1.13.5 fixer could not find {label} boundary block')
    t=t.replace(old,new,1)

harden(
    '        private float navProgressV1110(){',
    "b=s.find('        private int navRemainV1110(',a)",
    "if a<0 or b<0: raise SystemExit('v1.13.5 nav progress boundary missing')",
    'v1.13.5 nav progress'
)
harden(
    '        private void drawFieldNavV1110(Canvas c,RectF stage,int totalM){',
    "b=s.find('        private String fieldReadyLabelV1114(){',a)",
    "if a<0 or b<0: raise SystemExit('v1.13.5 field nav boundary missing')",
    'v1.13.5 field nav'
)
harden(
    '        private String fieldReadyLabelV1114(){',
    "b=s.find('        private int fieldReadyBgV1114(){',a)",
    "if a<0 or b<0: raise SystemExit('v1.13.5 field-ready label boundary missing')",
    'v1.13.5 field-ready label'
)
harden(
    '        private void saveRef(int kind){',
    "b=s.find('        private GeoRef getRef(String type,int h){',a)",
    "if a<0 or b<0: raise SystemExit('v1.13.5 saveRef boundary missing')",
    'v1.13.5 saveRef'
)

p.write_text(t)
print('hardened V1.13.5 replacements to preserve interstitial helper methods')
