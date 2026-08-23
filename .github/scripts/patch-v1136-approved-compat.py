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

# Keep the existing three-point GREEN engine available for the accurate mode.
s=s.replace('Distances ds=distances(green);',
            'Distances ds=distances3(getRef("gf",hole),green,getRef("gb",hole));')

# TOTAL is always the official full-hole length.
# DIST starts as soon as TEE is calibrated:
# - TEE only: TOTAL - travelled distance from the saved TEE anchor.
# - GREEN CENTER available: current GPS -> GREEN CENTER actual distance.
s=s.replace('int distM=ds.center>=0?ds.center:totalM;',
            'int distM=approvedRemainingV1136(totalM,green);')
s=s.replace('String distText=(green!=null && gpsUsable() && ds.center>=0)?(ds.center+"m"):"--";',
            'int distM=approvedRemainingV1136(totalM,green);')
s=s.replace('drawApprovedMetricV1136(c,"DIST",distM+"m",w*.515f,h*.072f,h*.091f);',
            'drawApprovedMetricV1136(c,"DIST",distM>=0?distM+"m":"--",w*.515f,h*.072f,h*.091f);')
s=s.replace('drawApprovedMetricV1136(c,"DIST",distText,w*.515f,h*.072f,h*.091f);',
            'drawApprovedMetricV1136(c,"DIST",distM>=0?distM+"m":"--",w*.515f,h*.072f,h*.091f);')

helper_marker='        private void drawApprovedWeatherGpsV1136(Canvas c,float w,float h){'
if 'private int approvedRemainingV1136(' not in s:
    idx=s.find(helper_marker)
    if idx<0:
        raise SystemExit('approved remaining helper anchor missing')
    helper=r'''        private int approvedRemainingV1136(int totalM,GeoRef green){
            if(location==null || !navGpsUsableV1133())return -1;
            if(green!=null)return Math.max(0,Math.round(distance(location,green.lat,green.lon)));
            GeoRef tee=getRef("t",hole);
            if(tee==null || totalM<=0)return -1;
            int travelled=Math.max(0,Math.round(distance(location,tee.lat,tee.lon)));
            return Math.max(0,Math.min(totalM,totalM-travelled));
        }

'''
    s=s[:idx]+helper+s[idx:]

# Re-link the proven V1.13.5 live marker to the PASS UI. That engine already
# supports TEE-only progress when official hole length exists, so the circular
# player marker appears immediately after TEE calibration. Once GREEN CENTER is
# calibrated it automatically upgrades to the full geographic TEE->GREEN mode.
marker='''            courseRect.set(imgInner);\n            drawApprovedRulerV1136(c,w,h,imgFrame,totalM);'''
repl='''            courseRect.set(imgInner);\n            if(getRef("t",hole)!=null && navGpsUsableV1133()) drawFieldNavV1110(c,imgInner,totalM);\n            drawApprovedRulerV1136(c,w,h,imgFrame,totalM);'''
if marker in s:
    s=s.replace(marker,repl,1)
elif 'if(getRef("t",hole)!=null && green!=null && gpsUsable()) drawFieldNavV1110(c,imgInner,totalM);' in s:
    s=s.replace('if(getRef("t",hole)!=null && green!=null && gpsUsable()) drawFieldNavV1110(c,imgInner,totalM);',
                'if(getRef("t",hole)!=null && navGpsUsableV1133()) drawFieldNavV1110(c,imgInner,totalM);',1)
elif 'drawFieldNavV1110(c,imgInner,totalM);' not in s:
    raise SystemExit('approved live-marker anchor missing')

p.write_text(s)
print('locked PASS UI: TEE-first circular marker + estimated live DIST, upgraded to true GREEN CENTER remaining distance')

# Apply the trip-specific one-shot field behavior after all approved UI/GPS
# compatibility work. This removes any dependency on a future second round.
one_shot=Path('.github/scripts/patch-v1136-one-shot-field.py')
if not one_shot.exists():
    raise SystemExit('missing one-shot field patch')
exec(compile(one_shot.read_text(),str(one_shot),'exec'))

# Auto detection must never switch holes silently. Overlay the storybook
# confirmation flow after one-shot detection so the user can inspect the actual
# candidate mini yardage, adjust with arrows, then explicitly commit the hole.
hole_popup=Path('.github/scripts/patch-v1136-hole-confirm-popup.py')
if not hole_popup.exists():
    raise SystemExit('missing hole-confirm popup patch')
exec(compile(hole_popup.read_text(),str(hole_popup),'exec'))
