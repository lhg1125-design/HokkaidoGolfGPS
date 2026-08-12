from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit('v1.4 missing '+label)
    s=s.replace(old,new,count)

# Extra drawing / interaction state for 5-screen flow.
rep('import android.graphics.RectF;','import android.graphics.Rect;\nimport android.graphics.RectF;','Rect import')
rep('private boolean autoHole=true, hasTarget=false;\n        private float targetX,targetY;','private boolean autoHole=true, hasTarget=false;\n        private float targetX,targetY;\n        private GeoRef targetRef;','target geo ref')
rep('private final RectF prev=new RectF(),next=new RectF(),mapTab=new RectF(),scoreTab=new RectF();','private final RectF prev=new RectF(),next=new RectF(),mapTab=new RectF(),scoreTab=new RectF();\n        private final RectF holePrevBtn=new RectF(),holeNextBtn=new RectF();\n        private final RectF[] inputStrokeMinus={new RectF(),new RectF(),new RectF(),new RectF()};\n        private final RectF[] inputStrokePlus={new RectF(),new RectF(),new RectF(),new RectF()};\n        private final RectF[] inputPuttMinus={new RectF(),new RectF(),new RectF(),new RectF()};\n        private final RectF[] inputPuttPlus={new RectF(),new RectF(),new RectF(),new RectF()};','input rects')

rep('if(screen==0) home(c); else if(screen==1) round(c); else score(c);','if(screen==0) home(c); else if(screen==1) round(c); else if(screen==2) scoreInput(c); else if(screen==3) score(c); else summary(c);','5 screen draw')

# Add a calibrated GPS target overlay and compact hole pager to live course.
old_target='''            if(hasTarget){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);p.setColor(CORAL);c.drawCircle(targetX,targetY,15+5*pulse,p);p.setStyle(Paint.Style.FILL);p.setColor(CORAL);c.drawCircle(targetX,targetY,6,p);int est=estimateTargetM(courseRect,officialM);speech(c,Math.max(courseRect.left+8,Math.min(targetX-75,courseRect.right-160)),Math.max(courseRect.top+8,targetY-55),"공략 약 "+est+"m",CORAL);}'''
new_target='''            if(hasTarget){
                p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);p.setColor(CORAL);c.drawCircle(targetX,targetY,15+5*pulse,p);p.setStyle(Paint.Style.FILL);p.setColor(CORAL);c.drawCircle(targetX,targetY,6,p);
                TargetInfo ti=targetInfo(courseRect,officialM);
                String tl=ti.gps?("GPS "+ti.toTarget+"m / G "+ti.targetToGreen+"m"):("공략 약 "+ti.toTarget+"m");
                speech(c,Math.max(courseRect.left+8,Math.min(targetX-92,courseRect.right-190)),Math.max(courseRect.top+8,targetY-55),tl,ti.gps?DEEP:CORAL);
            }
            drawHoleHazards(c,courseRect);
            drawHolePager(c,h*.126f);'''
rep(old_target,new_target,'GPS target overlay')

# Replace 4-tab nav semantics with Course/Input/Card/Summary.
old_nav='''        private void drawGoldenNav(Canvas c){
            float w=getWidth(),h=getHeight();RectF bar=new RectF(w*.045f,h*.918f,w*.955f,h*.985f);
            softShadow(c,bar,bar.height()*.382f);box(c,bar,CARD,bar.height()*.382f);
            goldText(c,"‹ 이전",prev.centerX(),bar.centerY(),18.5f,INK);
            goldText(c,"코스",mapTab.centerX(),bar.centerY(),18.5f,screen==1?GREEN:INK);
            goldText(c,"스코어",scoreTab.centerX(),bar.centerY(),18.5f,screen==2?GREEN:INK);
            goldText(c,"다음 ›",next.centerX(),bar.centerY(),18.5f,INK);
        }'''
new_nav='''        private void drawGoldenNav(Canvas c){
            float w=getWidth(),h=getHeight();RectF bar=new RectF(w*.045f,h*.918f,w*.955f,h*.985f);
            softShadow(c,bar,bar.height()*.382f);box(c,bar,CARD,bar.height()*.382f);
            goldText(c,"코스",mapTab.centerX(),bar.centerY(),16.8f,screen==1?GREEN:INK);
            goldText(c,"입력",prev.centerX(),bar.centerY(),16.8f,screen==2?GREEN:INK);
            goldText(c,"카드",scoreTab.centerX(),bar.centerY(),16.8f,screen==3?GREEN:INK);
            goldText(c,"요약",next.centerX(),bar.centerY(),16.8f,screen==4?GREEN:INK);
        }
        private void setFourNav(float w,float h){
            mapTab.set(w*.055f,h*.925f,w*.27f,h*.981f);
            prev.set(w*.28f,h*.925f,w*.49f,h*.981f);
            scoreTab.set(w*.51f,h*.925f,w*.73f,h*.981f);
            next.set(w*.74f,h*.925f,w*.945f,h*.981f);
        }
        private void drawHolePager(Canvas c,float cy){
            float w=getWidth(),h=getHeight();
            holePrevBtn.set(w*.055f,cy-h*.021f,w*.125f,cy+h*.021f);
            holeNextBtn.set(w*.875f,cy-h*.021f,w*.945f,cy+h*.021f);
            goldButton(c,holePrevBtn,CARD,"‹",INK,21f);goldButton(c,holeNextBtn,CARD,"›",INK,21f);
        }'''
rep(old_nav,new_nav,'five screen nav')

# Every existing course/card nav block uses the new semantic coordinates.
rep('''            prev.set(w*.055f,h*.925f,w*.27f,h*.981f);mapTab.set(w*.28f,h*.925f,w*.49f,h*.981f);scoreTab.set(w*.51f,h*.925f,w*.73f,h*.981f);next.set(w*.74f,h*.925f,w*.945f,h*.981f);
            drawGoldenNav(c);''','''            setFourNav(w,h);drawGoldenNav(c);''','round nav coords',1)
rep('''            prev.set(w*.055f,h*.925f,w*.27f,h*.981f);
            mapTab.set(w*.28f,h*.925f,w*.49f,h*.981f);
            scoreTab.set(w*.51f,h*.925f,w*.73f,h*.981f);
            next.set(w*.74f,h*.925f,w*.945f,h*.981f);
            drawGoldenNav(c);''','''            setFourNav(w,h);drawGoldenNav(c);''','card nav coords',1)

# Clean the scorecard header so the baked small title is no longer visible behind the XL title.
rep('''            c.drawBitmap(v12Score,null,new RectF(0,0,w,h),p);

            // Cover the baked small table and rebuild it as two 9-hole cards.
            RectF clean=new RectF(w*.025f,h*.118f,w*.975f,h*.905f);
            box(c,clean,Color.rgb(249,250,240),34);
            text(c,"스코어카드",m,h*.083f,29,Color.WHITE,true);
            text(c,ko[selected]+" / "+variants[selected][variant],m,h*.112f,14,Color.rgb(218,242,222),true);''','''            c.drawBitmap(v12Score,null,new RectF(0,0,w,h),p);
            RectF header=new RectF(0,h*.035f,w,h*.128f);gradient(c,header,DEEP,GREEN,0);
            text(c,"스코어카드",m,h*.082f,29,Color.WHITE,true);
            text(c,ko[selected]+" / "+variants[selected][variant],m,h*.112f,14,Color.rgb(218,242,222),true);
            // Cover the baked table and rebuild it as two 9-hole cards.
            RectF clean=new RectF(w*.025f,h*.128f,w*.975f,h*.905f);
            box(c,clean,Color.rgb(249,250,240),34);''','score header cleanup')

# Insert Score Input + Summary + calibrated target/hazard helpers before scorecard method.
marker='        private void score(Canvas c){'
idx=s.find(marker)
if idx<0: raise SystemExit('v1.4 score marker missing')
insert=r'''        private void scoreInput(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;int par=currentPar();
            c.drawBitmap(v12Course,null,new RectF(0,0,w,h),p);
            RectF cover=new RectF(0,h*.105f,w,h*.915f);box(c,cover,BG,0);
            RectF head=new RectF(0,h*.035f,w,h*.145f);gradient(c,head,DEEP,GREEN,0);
            text(c,"스코어 입력",m,h*.078f,29,Color.WHITE,true);
            text(c,ko[selected]+" / H"+hole+" / PAR "+par,m,h*.112f,14,Color.rgb(218,242,222),true);
            drawHolePager(c,h*.150f);

            float top=h*.190f,rowH=h*.157f,gap=h*.018f;
            int[] dots={GREEN,SKY,CORAL,YELLOW};
            for(int pl=0;pl<4;pl++){
                float y=top+pl*(rowH+gap);RectF card=new RectF(m,y,w-m,y+rowH);
                softShadow(c,card,28);box(c,card,CARD,28);
                RectF tag=new RectF(card.left+14,card.top+14,card.left+98,card.top+54);box(c,tag,dots[pl],18);
                goldText(c,"P"+(pl+1),tag.centerX(),tag.centerY(),18f,Color.WHITE);
                int st=getStroke(pl,hole,par),pu=getPutt(pl,hole),delta=st-par;
                String rel=delta==0?"E":(delta>0?"+"+delta:""+delta);
                goldText(c,rel,card.left+136,card.top+34,16.5f,delta>0?CORAL:(delta<0?GREEN:INK));
                text(c,"타수",card.left+115,card.top+78,13,Color.GRAY,true);
                goldText(c,""+st,card.left+226,card.top+92,34f,INK);
                text(c,"퍼트",card.left+420,card.top+78,13,Color.GRAY,true);
                goldText(c,""+pu,card.left+535,card.top+92,34f,INK);

                inputStrokeMinus[pl].set(card.left+96,card.bottom-58,card.left+164,card.bottom-10);
                inputStrokePlus[pl].set(card.left+282,card.bottom-58,card.left+350,card.bottom-10);
                inputPuttMinus[pl].set(card.left+408,card.bottom-58,card.left+476,card.bottom-10);
                inputPuttPlus[pl].set(card.right-92,card.bottom-58,card.right-24,card.bottom-10);
                goldButton(c,inputStrokeMinus[pl],SOFT,"−",INK,23f);goldButton(c,inputStrokePlus[pl],Color.rgb(229,244,218),"+",GREEN,23f);
                goldButton(c,inputPuttMinus[pl],SOFT,"−",INK,23f);goldButton(c,inputPuttPlus[pl],Color.rgb(226,245,250),"+",BLUE,23f);
            }
            setFourNav(w,h);drawGoldenNav(c);
        }

        private void summary(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;
            c.drawColor(DEEP);
            // exact concept-art crop: golf cart bear from approved home artwork.
            Rect src=new Rect((int)(v12Home.getWidth()*.50f),(int)(v12Home.getHeight()*.11f),(int)(v12Home.getWidth()*.83f),(int)(v12Home.getHeight()*.28f));
            RectF dst=new RectF(w*.58f,h*.055f,w*.96f,h*.245f);c.drawBitmap(v12Home,src,dst,p);
            text(c,"라운드 요약",m,h*.076f,28,Color.WHITE,true);
            text(c,ko[selected],m,h*.110f,13,Color.rgb(216,242,222),true);
            text(c,variants[selected][variant]+" · 2026.08."+(24+selected),m,h*.137f,11,Color.rgb(216,242,222),false);

            int parTotal=0,total=0,putts=0,bird=0,parc=0,bog=0;
            for(int i=1;i<=18;i++){int pa=parForHole(i),sv=getStroke(0,i,pa);parTotal+=pa;total+=sv;putts+=getPutt(0,i);int d=sv-pa;if(d<0)bird++;else if(d==0)parc++;else bog++;}
            int delta=total-parTotal;String rel=delta==0?"E":(delta>0?"+"+delta:""+delta);
            RectF totalCard=new RectF(m,h*.275f,w-m,h*.515f);gradient(c,totalCard,Color.rgb(15,104,66),Color.rgb(28,134,75),34);sheen(c,totalCard,34);
            goldText(c,"TOTAL",totalCard.centerX(),h*.315f,18f,Color.rgb(216,242,222));
            goldText(c,rel+"  ("+total+")",totalCard.centerX(),h*.385f,48f,Color.WHITE);
            goldText(c,"퍼트 "+putts,totalCard.centerX(),h*.442f,20f,Color.WHITE);
            goldText(c,"버디 "+bird+"   ·   파 "+parc+"   ·   보기+ "+bog,totalCard.centerX(),h*.485f,16f,Color.rgb(225,245,229));

            RectF cheer=new RectF(m,h*.555f,w*.70f,h*.625f);box(c,cheer,Color.rgb(218,244,190),28);goldText(c,delta<=0?"나이스 라운드!":"다음 라운드는 더 가볍게!",cheer.centerX(),cheer.centerY(),18f,DEEP);
            RectF listBtn=new RectF(m,h*.675f,w-m,h*.748f);goldButton(c,listBtn,Color.rgb(245,143,39),"라운드 목록 보기",Color.WHITE,20f);
            RectF shareBtn=new RectF(m,h*.765f,w-m,h*.838f);goldButton(c,shareBtn,Color.rgb(50,146,214),"공유하기",Color.WHITE,20f);
            setFourNav(w,h);drawGoldenNav(c);
        }

        private GeoRef calibratedMapRef(RectF r,float x,float y){
            GeoRef tee=getRef("t",hole),green=greenCenterRef(hole);if(tee==null||green==null)return null;
            double lat0=Math.toRadians(tee.lat),mx=111320.0*Math.cos(lat0),my=110540.0;
            double ex=(green.lon-tee.lon)*mx,ny=(green.lat-tee.lat)*my,total=Math.sqrt(ex*ex+ny*ny);if(total<30)return null;
            double ux=ex/total,uy=ny/total,px=-uy,py=ux;
            double along=Math.max(0,Math.min(1,(r.bottom-y)/r.height()))*total;
            double cross=((x-r.centerX())/(r.width()/2.0))*Math.min(70,total*.18);
            double tx=ux*along+px*cross,ty=uy*along+py*cross;
            return new GeoRef(tee.lat+ty/my,tee.lon+tx/mx,false);
        }

        private TargetInfo targetInfo(RectF r,int officialM){
            if(targetRef==null)targetRef=calibratedMapRef(r,targetX,targetY);
            if(targetRef!=null&&gpsUsable()){
                int a=Math.round(distance(location,targetRef.lat,targetRef.lon));GeoRef g=greenCenterRef(hole);
                int b=g==null?-1:Math.round(distanceBetween(targetRef,g));return new TargetInfo(true,a,Math.max(0,b));
            }
            return new TargetInfo(false,estimateTargetM(r,officialM),-1);
        }
        private float distanceBetween(GeoRef a,GeoRef b){float[] o=new float[1];Location.distanceBetween(a.lat,a.lon,b.lat,b.lon,o);return o[0];}

        private void drawHoleHazards(Canvas c,RectF r){
            Hazard[] hs=hazardsForHole();
            for(Hazard hz:hs){
                float x=r.left+r.width()*hz.x,y=r.top+r.height()*hz.y;
                int col=hz.type.equals("WATER")?BLUE:YELLOW;
                p.setColor(Color.argb(220,255,255,255));c.drawCircle(x,y,27,p);p.setColor(col);c.drawCircle(x,y,19,p);
                goldText(c,hz.type.equals("WATER")?"W":"B",x,y,12.5f,hz.type.equals("WATER")?Color.WHITE:INK);
                GeoRef gr=calibratedMapRef(r,x,y);
                if(gr!=null&&gpsUsable()){
                    int d=Math.round(distance(location,gr.lat,gr.lon));pill(c,new RectF(x-42,y+24,x+42,y+51),Color.argb(228,255,255,255),d+"m",INK,7.2f);
                }
            }
        }
        private Hazard[] hazardsForHole(){
            if(selected==0&&variant==0&&hole==11)return new Hazard[]{new Hazard("BUNKER",.43f,.22f)};
            if(selected==0&&variant==0&&hole==7)return new Hazard[]{new Hazard("BUNKER",.32f,.48f)};
            if(selected==0&&variant==0&&hole==18)return new Hazard[]{new Hazard("BUNKER",.62f,.56f),new Hazard("BUNKER",.43f,.20f)};
            if(selected==0&&variant==1&&hole==13)return new Hazard[]{new Hazard("WATER",.48f,.53f)};
            if(selected==0&&variant==1&&hole==15)return new Hazard[]{new Hazard("WATER",.55f,.28f),new Hazard("BUNKER",.39f,.20f)};
            if(selected==1&&variant==0&&hole==15)return new Hazard[]{new Hazard("WATER",.60f,.26f)};
            if(selected==2&&(hole==8||hole==15))return new Hazard[]{new Hazard("BUNKER",.40f,.23f)};
            int seed=(hole*37+selected*11+variant*7)%5;
            if(seed==0)return new Hazard[]{new Hazard("BUNKER",.35f,.42f)};
            if(seed==1)return new Hazard[]{new Hazard("WATER",.66f,.52f)};
            return new Hazard[0];
        }

'''
s=s[:idx]+insert+s[idx:]

# Rewrite touch handler for five-screen navigation and per-player input buttons.
start=s.find('        @Override public boolean onTouchEvent(MotionEvent e){')
end=s.find('        static final class GeoRef',start)
if start<0 or end<0: raise SystemExit('v1.4 touch block markers missing')
touch=r'''        @Override public boolean onTouchEvent(MotionEvent e){
            if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();
            if(screen==0){
                for(int i=0;i<3;i++)if(cards[i].contains(x,y)){selected=i;if(i==2)variant=0;saveState();invalidate();return true;}
                if(varA.contains(x,y)){variant=0;saveState();invalidate();return true;}
                if(varB.contains(x,y)){variant=selected==2?0:1;saveState();invalidate();return true;}
                if(selected>=0&&start.contains(x,y)){screen=1;saveState();invalidate();return true;}
                return true;
            }

            if(holePrevBtn.contains(x,y)){if(hole>1){hole--;holeDirection=-1;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;targetRef=null;saveState();invalidate();}return true;}
            if(holeNextBtn.contains(x,y)){if(hole<18){hole++;holeDirection=1;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;targetRef=null;saveState();invalidate();}return true;}

            if(screen==1){
                if(courseRect.contains(x,y)){targetX=x;targetY=y;hasTarget=true;targetRef=calibratedMapRef(courseRect,x,y);showToast(targetRef!=null?"GPS 타깃 설정":"타깃 설정 · TEE/GREEN 저장 시 GPS 거리");invalidate();return true;}
                if(greenSave.contains(x,y)){saveGreenPoint();return true;}
                if(teeSave.contains(x,y)){saveRef(2);return true;}
                if(mapLaunch.contains(x,y)){launchExternalMap();return true;}
                if(autoBtn.contains(x,y)){autoHole=!autoHole;saveState();invalidate();return true;}
                for(int i=0;i<4;i++)if(playerTabs[i].contains(x,y)){player=i;saveState();invalidate();return true;}
            }
            if(screen==2){
                int par=currentPar();
                for(int pl=0;pl<4;pl++){
                    if(inputStrokeMinus[pl].contains(x,y)){setStroke(pl,hole,Math.max(1,getStroke(pl,hole,par)-1));invalidate();return true;}
                    if(inputStrokePlus[pl].contains(x,y)){setStroke(pl,hole,getStroke(pl,hole,par)+1);invalidate();return true;}
                    if(inputPuttMinus[pl].contains(x,y)){setPutt(pl,hole,Math.max(0,getPutt(pl,hole)-1));invalidate();return true;}
                    if(inputPuttPlus[pl].contains(x,y)){setPutt(pl,hole,getPutt(pl,hole)+1);invalidate();return true;}
                }
            }

            if(mapTab.contains(x,y)){screen=1;invalidate();return true;}
            if(prev.contains(x,y)){screen=2;invalidate();return true;}
            if(scoreTab.contains(x,y)){screen=3;invalidate();return true;}
            if(next.contains(x,y)){screen=4;invalidate();return true;}
            return true;
        }

'''
s=s[:start]+touch+s[end:]

# Add helper classes before GeoRef.
rep('        static final class GeoRef{', '        static final class Hazard{final String type;final float x,y;Hazard(String t,float a,float b){type=t;x=a;y=b;}}\n        static final class TargetInfo{final boolean gps;final int toTarget,targetToGreen;TargetInfo(boolean g,int a,int b){gps=g;toTarget=a;targetToGreen=b;}}\n        static final class GeoRef{','helper classes')

s=s.replace('V1.3 · SCORECARD XL','V1.4 · FIVE SCREEN GPS')
p.write_text(s)
print('applied v1.4: five-screen UI, calibrated GPS target, hole hazards, score input, round summary')
