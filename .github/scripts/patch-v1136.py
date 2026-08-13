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

p.write_text(s)
print('applied V1.13.6 5-second GPS ROUND LOG + TEE/GREEN events + one-tap JSONL share')
