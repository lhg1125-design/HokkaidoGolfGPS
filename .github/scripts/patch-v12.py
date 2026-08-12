from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit('v1.2 missing '+label)
    s=s.replace(old,new,1)

def block(start,end,new,label):
    global s
    a=s.find(start)
    if a<0: raise SystemExit('v1.2 start '+label)
    b=s.find(end,a)
    if b<0: raise SystemExit('v1.2 end '+label)
    s=s[:a]+new+'\n\n'+s[b:]

rep('import android.graphics.Canvas;','import android.graphics.Bitmap;\nimport android.graphics.BitmapFactory;\nimport android.graphics.Canvas;','bitmap imports')
rep('private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);','private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);\n        private final Bitmap v12Home,v12Course,v12Score;','bitmap fields')
rep('p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL));','p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL));\n            p.setFilterBitmap(true);\n            v12Home=BitmapFactory.decodeResource(getResources(),R.drawable.v12_home_ui);\n            v12Course=BitmapFactory.decodeResource(getResources(),R.drawable.v12_course_ui);\n            v12Score=BitmapFactory.decodeResource(getResources(),R.drawable.v12_score_ui);','decode')

home=r'''        private void home(Canvas c){
            float w=getWidth(),h=getHeight();
            c.drawBitmap(v12Home,null,new RectF(0,0,w,h),p);
            float m=w*.055f;
            float[] ys={h*.315f,h*.421f,h*.527f};
            for(int i=0;i<3;i++){
                cards[i].set(w*.095f,ys[i],w*.91f,ys[i]+h*.086f);
                if(selected==i){
                    p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(7);p.setColor(YELLOW);c.drawRoundRect(cards[i],32,32,p);p.setStyle(Paint.Style.FILL);
                    pill(c,new RectF(w*.82f,ys[i]+12,w*.90f,ys[i]+50),GREEN,"✓",Color.WHITE,10);
                }
                if(location!=null){int dm=(int)Math.round(distanceToCourse(location,i));String ds=dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km";pill(c,new RectF(w*.69f,ys[i]+h*.055f,w*.895f,ys[i]+h*.079f),Color.argb(235,255,255,255),ds,selected==i?GREEN:Color.GRAY,7.5f);}
            }
            float vy=h*.628f;
            varA.set(w*.095f,vy+w*.010f,w*.48f,vy+h*.030f);varB.set(w*.52f,vy+w*.010f,w*.905f,vy+h*.030f);
            if(selected>=0){
                text(c,variants[selected][0],varA.centerX(),varA.centerY()+7,10,variant==0?Color.WHITE:INK,true,Paint.Align.CENTER);
                text(c,variants[selected][1],varB.centerX(),varB.centerY()+7,10,variant==1?Color.WHITE:INK,true,Paint.Align.CENTER);
            }
            start.set(w*.065f,h*.733f,w*.935f,h*.805f);
            String gs=location==null?"GPS 준비 중…":"GPS READY ✓"; int gc=location==null?CORAL:GREEN;
            pill(c,new RectF(w*.55f,h*.829f,w*.91f,h*.864f),location==null?Color.rgb(255,238,229):Color.rgb(226,244,212),gs,gc,7.4f);
        }'''

round=r'''        private void round(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;int par=currentPar();int officialM=(int)Math.round(currentYards()*.9144);
            c.drawBitmap(v12Course,null,new RectF(0,0,w,h),p);
            GeoRef green=greenCenterRef(hole);GeoRef gf=getRef("gf",hole),gb=getRef("gb",hole);Distances ds=distances3(gf,green,gb);
            text(c,ko[selected],m,h*.061f,15,Color.WHITE,true);text(c,variants[selected][variant]+" · H"+hole,m,h*.088f,10,Color.rgb(216,242,222),false);
            text(c,"PAR "+par,w-m,h*.087f,15,Color.WHITE,true,Paint.Align.RIGHT);
            pill(c,new RectF(w*.72f,h*.024f,w*.94f,h*.053f),gpsBg(),gpsLabel(),gpsColor(),7.4f);
            text(c,ds.front<0?"--":ds.front+"m",w*.19f,h*.194f,25,Color.WHITE,true,Paint.Align.CENTER);
            text(c,ds.center<0?"--":ds.center+"m",w*.50f,h*.194f,25,Color.WHITE,true,Paint.Align.CENTER);
            text(c,ds.back<0?"--":ds.back+"m",w*.81f,h*.194f,25,Color.WHITE,true,Paint.Align.CENTER);
            courseRect.set(w*.07f,h*.258f,w*.93f,h*.669f);
            float prog=playerProgress();float yy=courseRect.bottom-55-prog*(courseRect.height()-145);float xx=courseRect.centerX()+((float)Math.sin(prog*3.0)-.15f)*courseRect.width()*.12f;
            float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/300.0));p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4);p.setColor(Color.argb(110+(int)(90*pulse),255,255,255));c.drawCircle(xx,yy,18+10*pulse,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.WHITE);c.drawCircle(xx,yy,12,p);p.setColor(GREEN);c.drawCircle(xx,yy,5,p);text(c,"YOU",xx,yy+34,8,Color.WHITE,true,Paint.Align.CENTER);
            if(prog>.02f)pill(c,new RectF(courseRect.left+16,courseRect.top+18,courseRect.left+135,courseRect.top+55),Color.argb(230,255,255,255),"진행 "+Math.round(prog*100)+"%",GREEN,7.4f);
            if(hasTarget){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);p.setColor(CORAL);c.drawCircle(targetX,targetY,15+5*pulse,p);p.setStyle(Paint.Style.FILL);p.setColor(CORAL);c.drawCircle(targetX,targetY,6,p);int est=estimateTargetM(courseRect,officialM);speech(c,Math.max(courseRect.left+8,Math.min(targetX-75,courseRect.right-160)),Math.max(courseRect.top+8,targetY-55),"공략 약 "+est+"m",CORAL);}
            textFit(c,strategyNote(),w*.08f,h*.729f,w*.92f,8.5f,INK,true);
            greenSave.set(w*.055f,h*.752f,w*.38f,h*.794f);teeSave.set(w*.403f,h*.752f,w*.65f,h*.794f);mapLaunch.set(w*.67f,h*.752f,w*.945f,h*.794f);
            text(c,greenSaveLabel(),greenSave.centerX(),greenSave.centerY()+6,8.2f,Color.WHITE,true,Paint.Align.CENTER);
            text(c,getRef("t",hole)==null?"TEE 저장":"TEE ✓",teeSave.centerX(),teeSave.centerY()+6,8.2f,Color.WHITE,true,Paint.Align.CENTER);
            drawPlayerTabs(c,h*.815f);
            int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);
            text(c,""+stroke,w*.30f,h*.883f,31,INK,true,Paint.Align.CENTER);text(c,""+putt,w*.72f,h*.883f,31,INK,true,Paint.Align.CENTER);
            minus.set(w*.085f,h*.856f,w*.145f,h*.900f);plus.set(w*.39f,h*.856f,w*.46f,h*.900f);pm.set(w*.54f,h*.856f,w*.61f,h*.900f);pp.set(w*.83f,h*.856f,w*.90f,h*.900f);
            prev.set(w*.055f,h*.933f,w*.27f,h*.979f);mapTab.set(w*.28f,h*.933f,w*.49f,h*.979f);scoreTab.set(w*.51f,h*.933f,w*.73f,h*.979f);next.set(w*.74f,h*.933f,w*.945f,h*.979f);
            autoBtn.set(w*.75f,h*.215f,w*.94f,h*.25f);
        }'''

score=r'''        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;c.drawBitmap(v12Score,null,new RectF(0,0,w,h),p);
            text(c,ko[selected]+" · "+variants[selected][variant],m,h*.086f,10,Color.rgb(214,242,222),false);
            int[] totals={0,0,0,0},puts={0,0,0,0};float sy=h*.186f,step=h*.0304f;
            for(int i=1;i<=18;i++){
                int pa=parForHole(i);float y=sy+(i-1)*step;text(c,""+i,w*.095f,y+6,8.4f,INK,true,Paint.Align.CENTER);text(c,""+pa,w*.245f,y+6,8.4f,Color.GRAY,false,Paint.Align.CENTER);
                for(int pl=0;pl<4;pl++){int sv=getStroke(pl,i,pa);totals[pl]+=sv;puts[pl]+=getPutt(pl,i);int col=sv>pa?CORAL:(sv<pa?GREEN:INK);text(c,""+sv,w*(.41f+pl*.153f),y+6,9.2f,col,true,Paint.Align.CENTER);}
            }
            for(int pl=0;pl<4;pl++){float x=w*(.31f+pl*.17f);text(c,"P"+(pl+1),x,h*.797f,8,Color.rgb(214,242,222),true,Paint.Align.CENTER);text(c,""+totals[pl],x,h*.836f,18,Color.WHITE,true,Paint.Align.CENTER);text(c,"퍼트 "+puts[pl],x,h*.866f,7,Color.rgb(214,242,222),false,Paint.Align.CENTER);}
            prev.set(w*.055f,h*.933f,w*.27f,h*.979f);mapTab.set(w*.28f,h*.933f,w*.49f,h*.979f);scoreTab.set(w*.51f,h*.933f,w*.73f,h*.979f);next.set(w*.74f,h*.933f,w*.945f,h*.979f);
        }'''

block('        private void home(Canvas c){','        private void round(Canvas c){',home,'home')
block('        private void round(Canvas c){','        private void drawCourse(',round,'round')
block('        private void score(Canvas c){','        private void saveRef(',score,'score')
s=s.replace('V1.0 · COURSE MAP','V1.2 · ARTWORK FIDELITY').replace('V1.1 · CONCEPT UI','V1.2 · ARTWORK FIDELITY')
p.write_text(s)
print('applied v1.2 artwork fidelity patch')
