from pathlib import Path
p=Path('.github/scripts/patch-v1133.py')
t=p.read_text()

# 1) Make preview touch replacement robust against whitespace/body drift.
old="""if old not in s: raise SystemExit('v1.13.3 preview touch anchor missing')
s=s.replace(old,new,1)"""
new=r'''if old in s:
    s=s.replace(old,new,1)
else:
    hdr='if(screen==1 && previewMode && courseRect.contains(x,y)){'
    ha=s.find(hdr)
    if ha<0: raise SystemExit('v1.13.3 preview touch header missing')
    line_start=s.rfind('\n',0,ha)+1
    indent=s[line_start:ha]
    brace=s.find('{',ha);depth=0;end=-1
    for ii in range(brace,len(s)):
        ch=s[ii]
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:
                end=ii+1;break
    if end<0: raise SystemExit('v1.13.3 preview touch block end missing')
    new_touch=(indent+'if(screen==1 && previewMode && courseRect.contains(x,y)){\n'
        +indent+'    float nt=courseRect.top+42f,nb=courseRect.bottom-30f;simProgressV1112=Math.max(0f,Math.min(1f,(nb-y)/Math.max(1f,nb-nt)));\n'
        +indent+'    simCrossTrackV1133=Math.max(-42f,Math.min(42f,(x-courseRect.centerX())/Math.max(1f,courseRect.width()*.36f)*35f));\n'
        +indent+'    navSmoothXV1133=Float.NaN;navSmoothYV1133=Float.NaN;invalidate();return true;\n'
        +indent+'}')
    s=s[:line_start]+new_touch+s[end:]'''
if old not in t:
    raise SystemExit('patch-v1133 touch fixer anchor missing')
t=t.replace(old,new,1)

# 2) Replace ONLY drawFieldNavV1110 itself. The old V1.13.3 code used
# fieldReadyLabelV1114 as the end marker, which also swallowed V1.12.4's
# drawHoleStepButtons/stepHole helper methods sitting between those methods.
old_boundary="""b=s.find('        private String fieldReadyLabelV1114(){',a)
if a<0 or b<0: raise SystemExit('v1.13.3 field nav method boundary missing')"""
new_boundary=r'''if a<0: raise SystemExit('v1.13.3 field nav method start missing')
brace=s.find('{',a);depth=0;b=-1
for ii in range(brace,len(s)):
    ch=s[ii]
    if ch=='{': depth+=1
    elif ch=='}':
        depth-=1
        if depth==0:
            b=ii+1
            while b<len(s) and s[b]=='\n': b+=1
            break
if b<0: raise SystemExit('v1.13.3 field nav method end missing')'''
if old_boundary not in t:
    raise SystemExit('patch-v1133 field-nav boundary fixer anchor missing')
t=t.replace(old_boundary,new_boundary,1)

p.write_text(t)
print('hardened patch-v1133 touch replacement + preserved hole-step helpers')
