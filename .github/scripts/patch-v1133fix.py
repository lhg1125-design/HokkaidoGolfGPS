from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.13.3 · NAEPO 2D GEO PIN' not in s:
    raise SystemExit('v1.13.3 fix requires V1.13.3')
if 'private void drawHoleStepButtonsV1124(' in s and 'private void stepHoleV1124(' in s:
    print('V1.13.3 hole-step helpers already present'); raise SystemExit(0)
anchor='        private String fieldReadyLabelV1114(){'
idx=s.find(anchor)
if idx<0: raise SystemExit('V1.13.3 fix anchor missing')
method=r'''        private void drawHoleStepButtonsV1124(Canvas c,RectF bar){
            float w=getWidth(),cy=bar.centerY();
            float rad=Math.min(bar.height()*.35f,w*.038f);
            float lx=bar.left+rad+8f,rx=bar.right-rad-8f;
            holePrevTopV1124.set(lx-rad,cy-rad,lx+rad,cy+rad);
            holeNextTopV1124.set(rx-rad,cy-rad,rx+rad,cy+rad);
            drawHoleStepButtonV1124(c,lx,cy,rad,-1,hole>1);
            drawHoleStepButtonV1124(c,rx,cy,rad,1,hole<18);
        }
        private void drawHoleStepButtonV1124(Canvas c,float x,float y,float r,int dir,boolean enabled){
            int a=enabled?244:92;
            p.setStyle(Paint.Style.FILL);p.setColor(Color.argb(enabled?26:10,0,45,28));c.drawCircle(x,y+3f,r+2f,p);
            p.setColor(Color.argb(a,255,255,255));c.drawCircle(x,y,r,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);
            p.setStrokeWidth(Math.max(3f,r*.115f));p.setColor(Color.argb(enabled?238:90,8,79,52));c.drawCircle(x,y,r-1.5f,p);
            float shaft=r*.42f,head=r*.24f;float from=x-dir*shaft*.40f,to=x+dir*shaft*.52f;
            c.drawLine(from,y,to,y,p);c.drawLine(to,y,to-dir*head,y-head,p);c.drawLine(to,y,to-dir*head,y+head,p);
            p.setStrokeCap(Paint.Cap.BUTT);p.setStrokeJoin(Paint.Join.MITER);p.setStyle(Paint.Style.FILL);
        }
        private void stepHoleV1124(int delta){
            int nh=Math.max(1,Math.min(18,hole+delta));if(nh==hole)return;
            holeDirection=delta>0?1:-1;hole=nh;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;
            navSmoothXV1133=Float.NaN;navSmoothYV1133=Float.NaN;saveState();invalidate();
        }

'''
s=s[:idx]+method+s[idx:]
p.write_text(s)
print('restored V1.12.4 circular hole-step helpers after V1.13.3 nav replacement')
