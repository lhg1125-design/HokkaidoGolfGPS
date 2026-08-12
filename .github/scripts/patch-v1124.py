from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.12.3 · MAX MAP' not in s:
    raise SystemExit('v1.12.4 requires v1.12.3 max map')
s=s.replace('V1.12.3 · MAX MAP','V1.12.4 · HOLE STEP',1)

# Dedicated top-row hole controls. Do not reuse prev/next because nav() also
# owns those rectangles on the score screen.
field_anchor='''        private final RectF prev=new RectF(),next=new RectF(),mapTab=new RectF(),scoreTab=new RectF();'''
field_new=field_anchor+'\n        private final RectF holePrevTopV1124=new RectF(),holeNextTopV1124=new RectF();'
if field_anchor not in s:
    raise SystemExit('v1.12.4 top hole control field anchor missing')
s=s.replace(field_anchor,field_new,1)

# Draw the circular previous/next controls exactly in the left/right free space
# of the compact TOTAL / REMAIN / PAR strip requested by the field UI review.
range_anchor='''            RectF range=new RectF(m,h*.073f,w-m,h*.126f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),18);sheen(c,range,18);'''
range_new=range_anchor+'\n            drawHoleStepButtonsV1124(c,range);'
if range_anchor not in s:
    raise SystemExit('v1.12.4 metric range anchor missing')
s=s.replace(range_anchor,range_new,1)

# Vector-only circular arrow buttons: crisp on every resolution, no font glyph
# dependency. Edge holes remain visible but softly disabled.
nav_anchor='''        private void nav(Canvas c){'''
idx=s.find(nav_anchor)
if idx<0:
    raise SystemExit('v1.12.4 nav method anchor missing')
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
            p.setStyle(Paint.Style.FILL);
            p.setColor(Color.argb(enabled?26:10,0,45,28));
            c.drawCircle(x,y+3f,r+2f,p);
            p.setColor(Color.argb(a,255,255,255));
            c.drawCircle(x,y,r,p);
            p.setStyle(Paint.Style.STROKE);
            p.setStrokeCap(Paint.Cap.ROUND);
            p.setStrokeJoin(Paint.Join.ROUND);
            p.setStrokeWidth(Math.max(3f,r*.115f));
            p.setColor(Color.argb(enabled?238:90,8,79,52));
            c.drawCircle(x,y,r-1.5f,p);

            float shaft=r*.42f,head=r*.24f;
            float from=x-dir*shaft*.40f,to=x+dir*shaft*.52f;
            c.drawLine(from,y,to,y,p);
            c.drawLine(to,y,to-dir*head,y-head,p);
            c.drawLine(to,y,to-dir*head,y+head,p);
            p.setStrokeCap(Paint.Cap.BUTT);
            p.setStrokeJoin(Paint.Join.MITER);
            p.setStyle(Paint.Style.FILL);
        }

        private void stepHoleV1124(int delta){
            int nh=Math.max(1,Math.min(18,hole+delta));
            if(nh==hole)return;
            holeDirection=delta>0?1:-1;
            hole=nh;
            lastHoleChange=SystemClock.uptimeMillis();
            hasTarget=false;
            saveState();
            invalidate();
        }

'''
s=s[:idx]+method+s[idx:]

# On the yardage screen the top circular arrows become the sole previous/next
# hole controls. Bottom navigation keeps only MAP / SCORE, preventing duplicate
# controls and preserving the compact hierarchy.
old_nav='''        private void nav(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;prev.set(m,h*.905f,w*.23f,h*.965f);mapTab.set(w*.27f,h*.905f,w*.49f,h*.965f);scoreTab.set(w*.53f,h*.905f,w*.75f,h*.965f);next.set(w*.79f,h*.905f,w-m,h*.965f);
            pillButton(c,prev,CARD,"‹ 이전",INK);pillButton(c,mapTab,screen==1?GREEN:CARD,"지도",screen==1?Color.WHITE:INK);pillButton(c,scoreTab,screen==2?GREEN:CARD,"스코어",screen==2?Color.WHITE:INK);pillButton(c,next,CARD,"다음 ›",INK);
        }'''
new_nav='''        private void nav(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;
            if(screen==1){
                prev.set(-1,-1,-1,-1);next.set(-1,-1,-1,-1);
                mapTab.set(m,h*.918f,w*.49f,h*.965f);scoreTab.set(w*.51f,h*.918f,w-m,h*.965f);
                pillButton(c,mapTab,GREEN,"지도",Color.WHITE);pillButton(c,scoreTab,CARD,"스코어",INK);
                return;
            }
            prev.set(m,h*.905f,w*.23f,h*.965f);mapTab.set(w*.27f,h*.905f,w*.49f,h*.965f);scoreTab.set(w*.53f,h*.905f,w*.75f,h*.965f);next.set(w*.79f,h*.905f,w-m,h*.965f);
            pillButton(c,prev,CARD,"‹ 이전",INK);pillButton(c,mapTab,CARD,"지도",INK);pillButton(c,scoreTab,GREEN,"스코어",Color.WHITE);pillButton(c,next,CARD,"다음 ›",INK);
        }'''
if old_nav not in s:
    raise SystemExit('v1.12.4 existing nav body anchor missing')
s=s.replace(old_nav,new_nav,1)

# Install the top tap zones before map interactions.
touch_anchor='''            if(screen==1 && previewMode && courseRect.contains(x,y)){'''
if touch_anchor not in s:
    raise SystemExit('v1.12.4 top touch insertion anchor missing')
touch_new='''            if(screen==1 && holePrevTopV1124.contains(x,y)){stepHoleV1124(-1);return true;}
            if(screen==1 && holeNextTopV1124.contains(x,y)){stepHoleV1124(1);return true;}
'''+touch_anchor
s=s.replace(touch_anchor,touch_new,1)

p.write_text(s)
print('applied v1.12.4 circular top hole-step buttons + map-only compact bottom nav')
