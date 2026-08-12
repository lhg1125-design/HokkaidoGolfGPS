from pathlib import Path
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

oldtouch='''            if(screen==1 && courseRect.contains(x,y)){targetX=x;targetY=y;hasTarget=true;showToast("공략 지점 선택 · 도식 추정거리");invalidate();return true;}'''
newtouch='''            if(screen==1 && previewMode && courseRect.contains(x,y) && x>courseRect.right-92f){\n                float nt=courseRect.top+96f,nb=courseRect.bottom-92f;\n                simProgressV1112=Math.max(0f,Math.min(1f,(nb-y)/Math.max(1f,nb-nt)));\n                showToast("SIM WALK · "+Math.round(simProgressV1112*100f)+"% · 잔여거리 갱신");invalidate();return true;\n            }\n            if(screen==1 && courseRect.contains(x,y)){targetX=x;targetY=y;hasTarget=true;showToast("공략 지점 선택 · 도식 추정거리");invalidate();return true;}'''
if oldtouch not in s:
    raise SystemExit('v1.11.2 course touch anchor missing')
s=s.replace(oldtouch,newtouch,1)

# Give an always-visible hint only in simulator mode, without adding layout height.
oldmsg='''            String msg=previewMode?(mode+" · "+(remain>=0?remain+"m":"--")):(mode+" · "+(remain>=0?remain+"m":"--")+" · "+navAccuracyV1110());'''
newmsg='''            String msg=previewMode?(mode+" · "+(remain>=0?remain+"m":"--")+" · TAP"):(mode+" · "+(remain>=0?remain+"m":"--")+" · "+navAccuracyV1110());'''
if oldmsg not in s:
    raise SystemExit('v1.11.2 compact nav message anchor missing')
s=s.replace(oldmsg,newmsg,1)

p.write_text(s)
print('applied v1.11.2 tappable beta SIM walk axis')
