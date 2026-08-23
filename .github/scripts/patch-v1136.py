from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.13.5 · ALL COURSES LIVE GEO' not in s:
    raise SystemExit('v1.13.6 requires V1.13.5 all-course live geo')
s=s.replace('V1.13.5 · ALL COURSES LIVE GEO','V1.13.6 · ROUND LOG',1)

field='''        private int liveFixCountV1135=0,liveFixIndexV1135=0;'''
if field not in s:
    raise SystemExit('v1.13.6 live-fix field anchor missing')
s=s.replace(field,field+'''\n        private long lastRoundLogElapsedV1136=0L;\n        private final RectF roundLogShareBtnV1136=new RectF();''',1)

# 5-second persistent GPS stream. Insert after auto-hole handling so each sample
# carries the active course/hole state that the golfer actually sees.
a=s.find('        void setLocation(Location l) {')
b=s.find('        private void saveState(){',a)
if a<0 or b<0:
    raise SystemExit('v1.13.6 setLocation boundary missing')
block=s[a:b]
needle='maybeAutoHole(); invalidate();'
if needle not in block:
    raise SystemExit('v1.13.6 setLocation tail missing')
block=block.replace(needle,'maybeAutoHole(); recordRoundLogV1136(l); invalidate();',1)
s=s[:a]+block+s[b:]

anchor='        private void saveState(){'
idx=s.find(anchor)
if idx<0:
    raise SystemExit('v1.13.6 helper anchor missing')
helpers=r'''        private void recordRoundLogV1136(Location l){
            if(l==null || selected<0)return;
            long now=SystemClock.elapsedRealtime();
            if(lastRoundLogElapsedV1136>0 && now-lastRoundLogElapsedV1136<5000L)return;
            lastRoundLogElapsedV1136=now;
            int total=verifiedMetersV190();
            int remain=navRemainV1110(total);
            float progress=navProgressV1110();
            float cross=navCrossTrackMetersV1133();
            RoundLogV1134.sample(ctx,selected,variant,hole,currentPar(),total,remain,progress,cross,l,previewMode);
        }

        private void drawRoundLogShareV1136(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;
            roundLogShareBtnV1136.set(m,h*.765f,w-m,h*.838f);
            gradient(c,roundLogShareBtnV1136,Color.rgb(241,139,45),Color.rgb(255,177,62),26);
            sheen(c,roundLogShareBtnV1136,26);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3f);p.setColor(Color.rgb(169,93,25));c.drawRoundRect(roundLogShareBtnV1136,26,26,p);p.setStyle(Paint.Style.FILL);
            text(c,"ROUND LOG 공유",roundLogShareBtnV1136.centerX(),roundLogShareBtnV1136.centerY()+6,15.5f,Color.WHITE,true,Paint.Align.CENTER);
        }

        private void shareRoundLogV1136(){
            RoundLogV1134.event(ctx,"ROUND_LOG_SHARE",selected,variant,hole,location,"score+calibration snapshot appended");
            showToast("ROUND LOG 파일 준비 완료");
            RoundLogV1134.share(ctx);
        }

'''
s=s[:idx]+helpers+s[idx:]

# Draw the dedicated export button over the old generic summary share control.
on_draw='''            drawToast(c); postInvalidateDelayed(screen==1?50:120);'''
if on_draw not in s:
    raise SystemExit('v1.13.6 onDraw anchor missing')
s=s.replace(on_draw,'''            if(screen==4)drawRoundLogShareV1136(c);\n            drawToast(c); postInvalidateDelayed(screen==1?50:120);''',1)

# One tap from round summary opens Android share sheet with a .jsonl attachment.
touch='''            if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();'''
if touch not in s:
    raise SystemExit('v1.13.6 touch anchor missing')
s=s.replace(touch,touch+'''\n            if(screen==4 && roundLogShareBtnV1136.contains(x,y)){shareRoundLogV1136();return true;}''',1)

# Add explicit TEE/GREEN capture events to the continuous GPS stream.
save_line='''            confirmKind=0;confirmUntil=0;String mode=n>=3?(" · "+n+"FIX σ"+Math.round(sp)+"m"):(" · ±"+Math.round(rawAcc)+"m");showToast("H"+hole+" "+(kind==1?"GREEN CENTER":"TEE")+" 저장"+mode);navSmoothXV1133=Float.NaN;navSmoothYV1133=Float.NaN;maybeAutoHole();invalidate();'''
if save_line not in s:
    raise SystemExit('v1.13.6 V1.13.5 saveRef anchor missing')
save_new='''            confirmKind=0;confirmUntil=0;String mode=n>=3?(" · "+n+"FIX σ"+Math.round(sp)+"m"):(" · ±"+Math.round(rawAcc)+"m");showToast("H"+hole+" "+(kind==1?"GREEN CENTER":"TEE")+" 저장"+mode);RoundLogV1134.event(ctx,kind==1?"GREEN_CENTER_SAVE":"TEE_SAVE",selected,variant,hole,location,"accuracyM="+Math.round(rawAcc)+";fixes="+n+";spreadM="+Math.round(sp));navSmoothXV1133=Float.NaN;navSmoothYV1133=Float.NaN;maybeAutoHole();invalidate();'''
s=s.replace(save_line,save_new,1)

# Compatibility restoration for the approved V1.13.6 UI. The V1.13.4/1.13.5
# geo rewrite removed old helper bodies while later UI/touch code still calls
# them. Restore the original behavior instead of stubbing or removing controls.
compat_anchor='        private void saveState(){'
compat_idx=s.find(compat_anchor)
if compat_idx<0:
    raise SystemExit('v1.13.6 compatibility anchor missing')
compat=''
if 'private void drawHoleStepButtonsV1124(' not in s:
    compat += r'''        private void drawHoleStepButtonsV1124(Canvas c,RectF bar){
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
if 'private Distances distances(GeoRef ' not in s:
    compat += r'''        private Distances distances(GeoRef center){
            return distances3(getRef("gf",hole),center,getRef("gb",hole));
        }

'''
if 'private void saveGreenPoint(' not in s:
    compat += r'''        private void saveGreenPoint(){
            saveRef(1);
        }

'''
if compat:
    s=s[:compat_idx]+compat+s[compat_idx:]

p.write_text(s)
print('applied V1.13.6 ROUND LOG + restored approved-UI compatibility helpers')
