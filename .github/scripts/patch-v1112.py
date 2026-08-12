from pathlib import Path
import re
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.11.1 · FIELD NAV SAFE' not in s:
    raise SystemExit('v1.11.2 requires v1.11.1 field nav safe')
s=s.replace('V1.11.1 · FIELD NAV SAFE','V1.11.2 · SIM WALK BETA',1)

field='        private float targetX,targetY;'
if field not in s:
    raise SystemExit('v1.11.2 target field anchor missing')
s=s.replace(field,field+'\n        private float simProgressV1112=.42f;',1)

old='''        private float navProgressV1110(){\n            if(previewMode)return .42f;'''
new='''        private float navProgressV1110(){\n            if(previewMode)return simProgressV1112;'''
if old not in s:
    raise SystemExit('v1.11.2 preview progress anchor missing')
s=s.replace(old,new,1)

# Previous UI patches can alter the wording/action of the ordinary course-map
# touch line. Anchor only on courseRect.contains(x,y) and insert the simulator
# rail handler immediately before it instead of replacing the whole line.
m=re.search(r'courseRect\.contains\(\s*x\s*,\s*y\s*\)',s)
if not m:
    raise SystemExit('v1.11.2 course touch anchor missing')
line_start=s.rfind('\n',0,m.start())+1
line=s[line_start:s.find('\n',line_start)]
indent=line[:len(line)-len(line.lstrip())]
block=(
    indent+'if(screen==1 && previewMode && courseRect.contains(x,y) && x>courseRect.right-92f){\n'
    +indent+'    float nt=courseRect.top+96f,nb=courseRect.bottom-92f;\n'
    +indent+'    simProgressV1112=Math.max(0f,Math.min(1f,(nb-y)/Math.max(1f,nb-nt)));\n'
    +indent+'    showToast("SIM WALK · "+Math.round(simProgressV1112*100f)+"% · 잔여거리 갱신");invalidate();return true;\n'
    +indent+'}\n'
)
s=s[:line_start]+block+s[line_start:]

# Give an always-visible hint only in simulator mode, without adding layout height.
oldmsg='''            String msg=previewMode?(mode+" · "+(remain>=0?remain+"m":"--")):(mode+" · "+(remain>=0?remain+"m":"--")+" · "+navAccuracyV1110());'''
newmsg='''            String msg=previewMode?(mode+" · "+(remain>=0?remain+"m":"--")+" · TAP"):(mode+" · "+(remain>=0?remain+"m":"--")+" · "+navAccuracyV1110());'''
if oldmsg not in s:
    raise SystemExit('v1.11.2 compact nav message anchor missing')
s=s.replace(oldmsg,newmsg,1)

p.write_text(s)
print('applied v1.11.2 tappable beta SIM walk axis')
