from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.13.6 APPROVED UI HOTFIX' not in s:
    raise SystemExit('approved compat requires approved UI hotfix')

# V1.13.4/1.13.5 geo rewrites replace the interval that originally contained
# the V1.12.4 circular hole-step helpers. Restore their original implementation.
if 'private void drawHoleStepButtonsV1124(' not in s:
    anchor='        private String fieldReadyLabelV1114(){'
    idx=s.find(anchor)
    if idx<0:
        raise SystemExit('fieldReady helper anchor missing')
    helpers=r'''        private void drawHoleStepButtonsV1124(Canvas c,RectF bar){
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
            p.setStyle(Paint.Style.FILL);
            p.setColor(Color.argb(enabled?26:10,0,45,28));
            c.drawCircle(x,y+3f,r+2f,p);
            p.setColor(Color.argb(a,255,255,255));
            c.drawCircle(x,y,r,p);
            p.setStyle(Paint.Style.STROKE);
            p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);
            p.setStrokeWidth(Math.max(3f,r*.115f));p.setColor(Color.argb(enabled?238:90,8,79,52));
            c.drawCircle(x,y,r-1.5f,p);
            float shaft=r*.42f,head=r*.24f;
            float from=x-dir*shaft*.40f,to=x+dir*shaft*.52f;
            c.drawLine(from,y,to,y,p);c.drawLine(to,y,to-dir*head,y-head,p);c.drawLine(to,y,to-dir*head,y+head,p);
            p.setStrokeCap(Paint.Cap.BUTT);p.setStrokeJoin(Paint.Join.MITER);p.setStyle(Paint.Style.FILL);
        }

        private void stepHoleV1124(int delta){
            int nh=Math.max(1,Math.min(18,hole+delta));if(nh==hole)return;
            holeDirection=delta>0?1:-1;hole=nh;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;
            navSmoothXV1133=Float.NaN;navSmoothYV1133=Float.NaN;
            saveState();invalidate();
        }

'''
    s=s[:idx]+helpers+s[idx:]

# V1.13.5 removes the old three-point GREEN wrapper. The locked UI's
# GREEN CENTER action must keep the canonical V1.13.6 saveRef(1) path.
s=s.replace('if(greenSave.contains(x,y)){saveGreenPoint();return true;}',
            'if(greenSave.contains(x,y)){saveRef(1);return true;}')

# The approved course screen is applied after V1.0, where distances() was
# replaced by the three-point green engine. Bind DIST to that real engine.
s=s.replace('Distances ds=distances(green);',
            'Distances ds=distances3(getRef("gf",hole),green,getRef("gb",hole));')

# TOTAL is the official full-hole distance. DIST must never duplicate TOTAL.
# DIST is strictly the live player -> calibrated GREEN CENTER remaining distance.
s=s.replace('int distM=ds.center>=0?ds.center:totalM;',
            'String distText=(green!=null && gpsUsable() && ds.center>=0)?(ds.center+"m"):"--";')
s=s.replace('drawApprovedMetricV1136(c,"DIST",distM+"m",w*.515f,h*.072f,h*.091f);',
            'drawApprovedMetricV1136(c,"DIST",distText,w*.515f,h*.072f,h*.091f);')

# PASS UI must preserve the proven live 2D field marker. Only show the circular
# player marker when both TEE + GREEN CENTER calibration exist and GPS is valid.
marker='''            courseRect.set(imgInner);\n            drawApprovedRulerV1136(c,w,h,imgFrame,totalM);'''
repl='''            courseRect.set(imgInner);\n            if(getRef("t",hole)!=null && green!=null && gpsUsable()) drawFieldNavV1110(c,imgInner,totalM);\n            drawApprovedRulerV1136(c,w,h,imgFrame,totalM);'''
if marker in s:
    s=s.replace(marker,repl,1)
elif 'drawFieldNavV1110(c,imgInner,totalM);' in s:
    s=s.replace('drawFieldNavV1110(c,imgInner,totalM);',
                'if(getRef("t",hole)!=null && green!=null && gpsUsable()) drawFieldNavV1110(c,imgInner,totalM);',1)
else:
    raise SystemExit('approved live-marker anchor missing')

p.write_text(s)
print('locked PASS UI: TOTAL=official full distance, DIST=live remaining to calibrated green center, circular marker requires TEE+GREEN+GPS')
