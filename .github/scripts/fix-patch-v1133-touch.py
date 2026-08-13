from pathlib import Path
p=Path('.github/scripts/patch-v1133.py')
t=p.read_text()
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
    raise SystemExit('patch-v1133 fixer anchor missing')
t=t.replace(old,new,1)
p.write_text(t)
print('hardened patch-v1133 preview touch replacement')
