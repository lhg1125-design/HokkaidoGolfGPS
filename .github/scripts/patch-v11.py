from pathlib import Path

path = Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s = path.read_text()


def replace_block(start_marker, end_marker, new_block, label):
    global s
    a = s.find(start_marker)
    if a < 0:
        raise SystemExit(f'v1.1 patch missing start: {label}')
    b = s.find(end_marker, a)
    if b < 0:
        raise SystemExit(f'v1.1 patch missing end: {label}')
    s = s[:a] + new_block + '\n\n' + s[b:]


home = r'''        private void home(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;

            // Concept-art sky: bright, playful Hokkaido trip cover.
            gradient(c,new RectF(0,0,w,h*.455f),Color.rgb(48,177,239),Color.rgb(128,215,246),0);
            drawHomeMountains(c,w,h);
            drawCloud(c,w*.08f,h*.085f,18); drawCloud(c,w*.67f,h*.072f,23); drawCloud(c,w*.83f,h*.155f,14);
            drawSun(c,w*.90f,h*.085f,26);
            drawTripFlag(c,m,h*.042f,w*.25f,h*.145f);

            mascot(c,w*.81f,h*.335f,42,true);
            speech(c,w*.58f,h*.292f,"북해도 라운드 출발!",DEEP);

            outlinedText(c,"北海道ゴルフ",w*.50f,h*.165f,31,Color.WHITE,Color.rgb(54,42,30));
            outlinedText(c,"GPSキャディ",w*.50f,h*.225f,40,Color.rgb(92,166,69),Color.rgb(54,42,30));
            pill(c,new RectF(w*.28f,h*.248f,w*.72f,h*.286f),Color.argb(235,255,255,255),"GPS × 코스맵 × 스코어 · 오프라인 OK",GREEN,8.8f);

            text(c,"오늘 어디서 칠까요?",m,h*.455f,17,INK,true);
            text(c,"사전 검토 컨셉아트 UI 적용 · 모든 거리 m",m,h*.481f,9.2f,Color.GRAY,false);

            float top=h*.505f,ch=h*.090f,gap=h*.011f;
            int[] accents={Color.rgb(88,170,82),Color.rgb(142,104,195),Color.rgb(67,141,94)};
            for(int i=0;i<3;i++){
                float y=top+i*(ch+gap); cards[i].set(m,y,w-m,y+ch);
                woodSign(c,cards[i],"DAY "+(i+1),ko[i],variants[i][0]+(i<2?" / "+variants[i][1]:""),accents[i],selected==i);
                if(location!=null){
                    int dm=(int)Math.round(distanceToCourse(location,i));
                    String ds=dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km";
                    pill(c,new RectF(w-m-98,y+13,w-m-10,y+42),Color.argb(235,255,255,255),ds,selected==i?GREEN:Color.GRAY,7.8f);
                }
            }

            float vy=h*.820f; text(c,"코스 선택",m,vy,9.5f,Color.GRAY,true);
            varA.set(m,vy+10,w*.48f,vy+52); varB.set(w*.52f,vy+10,w-m,vy+52);
            pillButton(c,varA,variant==0?GREEN:CARD,selected<0?"A COURSE":variants[selected][0],variant==0?Color.WHITE:INK);
            pillButton(c,varB,variant==1?GREEN:CARD,selected<0?"B COURSE":variants[selected][1],variant==1?Color.WHITE:INK);

            start.set(m,h*.885f,w-m,h*.947f);
            gradient(c,start,selected>=0?Color.rgb(242,151,55):Color.LTGRAY,selected>=0?Color.rgb(255,193,67):Color.GRAY,30);
            if(selected>=0) sheen(c,start,30);
            text(c,selected>=0?"라운드 시작  →":"골프장을 먼저 선택해주세요",w/2,h*.924f,14,selected>=0?Color.WHITE:Color.DKGRAY,true,Paint.Align.CENTER);
            pill(c,new RectF(m,h*.959f,w*.47f,h*.987f),Color.rgb(229,244,218),"COURSES OFFLINE ✓",GREEN,7.6f);
            pill(c,new RectF(w*.51f,h*.959f,w-m,h*.987f),location==null?Color.rgb(255,238,229):Color.rgb(229,244,218),location==null?"GPS 준비 중…":"GPS READY ✓",location==null?CORAL:GREEN,7.6f);
        }'''

round_method = r'''        private void round(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f; int par=currentPar(); int officialM=(int)Math.round(currentYards()*.9144);
            float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/320.0));

            // Dark-green header like the approved concept-art phone mockup.
            RectF head=new RectF(0,0,w,h*.112f); gradient(c,head,Color.rgb(8,93,58),Color.rgb(25,132,76),0);
            text(c,ko[selected],m,h*.041f,12,Color.WHITE,true);
            text(c,variants[selected][variant]+" · H"+hole,m,h*.073f,10,Color.rgb(218,243,225),false);
            text(c,"PAR "+par,w-m,h*.072f,14,Color.WHITE,true,Paint.Align.RIGHT);
            pill(c,new RectF(w-m-142,h*.019f,w-m,h*.052f),gpsBg(),gpsLabel(),gpsColor(),7.8f);

            GeoRef green=greenCenterRef(hole); GeoRef greenFront=getRef("gf",hole), greenBack=getRef("gb",hole); Distances ds=distances3(greenFront,green,greenBack);
            RectF range=new RectF(m,h*.126f,w-m,h*.214f); gradient(c,range,DEEP,GREEN,25); sheen(c,range,25);
            metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.151f);
            metric(c,"CENTER",ds.center<0?"--":ds.center+"m",w*.50f,h*.151f);
            metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.151f);

            int gc=savedGreenCenters(),tc=savedCount("t");
            pill(c,new RectF(m,h*.222f,w*.27f,h*.252f),gpsBg(),gpsStatusShort(),gpsColor(),7.4f);
            pill(c,new RectF(w*.285f,h*.222f,w*.70f,h*.252f),CARD,"GREEN "+gc+"/18 · TEE "+tc+"/18",gc>0?GREEN:Color.GRAY,7.4f);
            autoBtn.set(w*.715f,h*.222f,w-m,h*.252f); pill(c,autoBtn,autoHole?Color.rgb(229,244,218):CARD,autoHole?"AUTO ON":"AUTO OFF",autoHole?GREEN:Color.GRAY,7.4f);

            courseRect.set(m,h*.266f,w-m,h*.622f);
            softShadow(c,courseRect,32); drawCourse(c,courseRect,par,officialM,green,ds,pulse);
            pill(c,new RectF(courseRect.left+12,courseRect.top+12,courseRect.left+110,courseRect.top+40),Color.argb(235,255,255,255),"LIVE COURSE",GREEN,7.2f);

            RectF strategy=new RectF(m,h*.636f,w-m,h*.683f); softShadow(c,strategy,20); box(c,strategy,Color.rgb(255,252,235),20);
            p.setColor(YELLOW); c.drawCircle(m+17,h*.659f,5,p);
            text(c,"공략 포인트",m+31,h*.655f,8.4f,GREEN,true);
            textFit(c,strategyNote(),m+31,h*.674f,w-m-12,8.1f,INK,true);

            greenSave.set(m,h*.698f,w*.41f,h*.744f); teeSave.set(w*.43f,h*.698f,w*.68f,h*.744f); mapLaunch.set(w*.70f,h*.698f,w-m,h*.744f);
            pillButton(c,greenSave,green==null?CORAL:DEEP,greenSaveLabel(),Color.WHITE);
            pillButton(c,teeSave,getRef("t",hole)==null?Color.rgb(67,145,105):DEEP,confirmKind==2&&SystemClock.uptimeMillis()<confirmUntil?"다시 탭":"TEE 저장",Color.WHITE);
            pillButton(c,mapLaunch,CARD,"외부 지도",INK);

            drawPlayerTabs(c,h*.762f);
            RectF panel=new RectF(m,h*.800f,w-m,h*.890f); softShadow(c,panel,24); box(c,panel,CARD,24);
            int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);
            text(c,"타수",m+18,h*.827f,9.5f,Color.GRAY,true); text(c,""+stroke,w*.28f,h*.869f,27,INK,true,Paint.Align.CENTER);
            minus.set(m+10,h*.838f,m+52,h*.884f); plus.set(w*.38f,h*.838f,w*.47f,h*.884f);
            roundButton(c,minus,"−",SOFT,Color.GRAY); roundButton(c,plus,"+",Color.rgb(229,244,218),GREEN);
            text(c,"퍼트",w*.56f,h*.827f,9.5f,Color.GRAY,true); text(c,""+putt,w*.70f,h*.869f,26,INK,true,Paint.Align.CENTER);
            pm.set(w*.53f,h*.838f,w*.61f,h*.884f); pp.set(w*.82f,h*.838f,w*.90f,h*.884f);
            roundButton(c,pm,"−",SOFT,Color.GRAY); roundButton(c,pp,"+",Color.rgb(226,245,250),SKY);
            drawTapBurst(c,h); nav(c);
        }'''

score = r'''        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.05f;
            RectF head=new RectF(0,0,w,h*.125f); gradient(c,head,Color.rgb(10,95,59),Color.rgb(31,137,77),0);
            text(c,"스코어카드",m,h*.057f,25,Color.WHITE,true);
            text(c,ko[selected]+" · "+variants[selected][variant],m,h*.090f,9.5f,Color.rgb(218,243,225),false);
            mascot(c,w*.88f,h*.067f,21,true);

            RectF th=new RectF(m,h*.145f,w-m,h*.185f); box(c,th,DEEP,15);
            String[] hh={"HOLE","PAR","P1","P2","P3","P4"}; float[] hx={m+12,w*.27f,w*.45f,w*.59f,w*.73f,w*.87f};
            for(int i=0;i<hh.length;i++) text(c,hh[i],hx[i],h*.171f,8.1f,Color.WHITE,true,i==0?Paint.Align.LEFT:Paint.Align.CENTER);

            float y=h*.206f; int[] totals={0,0,0,0}; int[] totalPutts={0,0,0,0};
            for(int i=1;i<=18;i++){
                int pa=parForHole(i); RectF row=new RectF(m,y-15,w-m,y+17); box(c,row,i==hole?Color.rgb(238,249,222):(i%2==0?Color.rgb(255,252,238):CARD),12);
                text(c,""+i,m+15,y+5,8.6f,INK,true); text(c,""+pa,w*.27f,y+5,8.2f,Color.GRAY,false,Paint.Align.CENTER);
                for(int pl=0;pl<4;pl++){
                    int sv=getStroke(pl,i,pa); totals[pl]+=sv; totalPutts[pl]+=getPutt(pl,i);
                    int col=sv>pa?CORAL:(sv<pa?GREEN:INK); text(c,""+sv,w*(.45f+pl*.14f),y+5,9.2f,col,true,Paint.Align.CENTER);
                }
                y+=h*.0285f;
            }

            RectF total=new RectF(m,h*.744f,w-m,h*.855f); gradient(c,total,DEEP,GREEN,24); sheen(c,total,24);
            text(c,"ROUND TOTAL",m+16,h*.775f,8.5f,Color.rgb(218,243,225),true);
            for(int pl=0;pl<4;pl++){
                text(c,"P"+(pl+1),w*(.31f+pl*.17f),h*.790f,7.3f,Color.rgb(218,243,225),true,Paint.Align.CENTER);
                text(c,""+totals[pl],w*(.31f+pl*.17f),h*.822f,16,Color.WHITE,true,Paint.Align.CENTER);
                text(c,"퍼트 "+totalPutts[pl],w*(.31f+pl*.17f),h*.844f,6.8f,Color.rgb(218,243,225),false,Paint.Align.CENTER);
            }
            speech(c,m,h*.867f,"나이스 라운드!",GREEN); mascot(c,w*.23f,h*.879f,18,true);
            nav(c);
        }'''

replace_block('        private void home(Canvas c){','        private void round(Canvas c){',home,'home')
replace_block('        private void round(Canvas c){','        private void drawCourse(',round_method,'round')
replace_block('        private void score(Canvas c){','        private void saveRef(',score,'score')

# Replace bottom navigation with concept-art rounded tab bar while retaining hole navigation.
nav = r'''        private void nav(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;
            RectF bar=new RectF(m,h*.914f,w-m,h*.980f); softShadow(c,bar,26); box(c,bar,CARD,26);
            float gap=5,ww=(bar.width()-gap*3)/4;
            prev.set(bar.left,bar.top,bar.left+ww,bar.bottom);
            mapTab.set(prev.right+gap,bar.top,prev.right+gap+ww,bar.bottom);
            scoreTab.set(mapTab.right+gap,bar.top,mapTab.right+gap+ww,bar.bottom);
            next.set(scoreTab.right+gap,bar.top,bar.right,bar.bottom);
            navCell(c,prev,"‹","이전",false,CORAL);
            navCell(c,mapTab,"●","코스",screen==1,GREEN);
            navCell(c,scoreTab,"✎","스코어",screen==2,SKY);
            navCell(c,next,"›","다음",false,YELLOW);
        }'''
replace_block('        private void nav(Canvas c){','        private int currentPar()',nav,'nav')

helpers = r'''
        private void drawHomeMountains(Canvas c,float w,float h){
            Path p1=new Path(); p1.moveTo(0,h*.455f); p1.lineTo(w*.25f,h*.285f); p1.lineTo(w*.43f,h*.455f); p1.close();
            p.setColor(Color.rgb(91,170,113)); c.drawPath(p1,p);
            Path p2=new Path(); p2.moveTo(w*.20f,h*.455f); p2.lineTo(w*.50f,h*.255f); p2.lineTo(w*.78f,h*.455f); p2.close();
            p.setColor(Color.rgb(73,151,103)); c.drawPath(p2,p);
            Path snow=new Path(); snow.moveTo(w*.43f,h*.305f); snow.lineTo(w*.50f,h*.255f); snow.lineTo(w*.57f,h*.305f); snow.lineTo(w*.54f,h*.297f); snow.lineTo(w*.50f,h*.315f); snow.lineTo(w*.47f,h*.295f); snow.close();
            p.setColor(Color.WHITE); c.drawPath(snow,p);
            RectF grass=new RectF(0,h*.405f,w,h*.475f); gradient(c,grass,Color.rgb(96,190,78),Color.rgb(65,151,64),0);
            p.setColor(Color.rgb(255,222,74)); c.drawCircle(w*.14f,h*.432f,4,p); c.drawCircle(w*.69f,h*.438f,4,p);
            p.setColor(Color.WHITE); c.drawCircle(w*.14f-5,h*.432f,3,p); c.drawCircle(w*.14f+5,h*.432f,3,p); c.drawCircle(w*.69f-5,h*.438f,3,p); c.drawCircle(w*.69f+5,h*.438f,3,p);
        }

        private void drawSun(Canvas c,float x,float y,float r){
            p.setColor(Color.rgb(255,215,63)); c.drawCircle(x,y,r,p);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(3); p.setColor(Color.rgb(255,215,63));
            for(int i=0;i<8;i++){double a=i*Math.PI/4; c.drawLine(x+(float)Math.cos(a)*r*1.25f,y+(float)Math.sin(a)*r*1.25f,x+(float)Math.cos(a)*r*1.65f,y+(float)Math.sin(a)*r*1.65f,p);} p.setStyle(Paint.Style.FILL);
            p.setColor(INK); c.drawCircle(x-r*.28f,y-r*.08f,2.6f,p); c.drawCircle(x+r*.28f,y-r*.08f,2.6f,p);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(2); c.drawArc(new RectF(x-r*.30f,y-r*.05f,x+r*.30f,y+r*.35f),15,150,false,p); p.setStyle(Paint.Style.FILL);
        }

        private void drawTripFlag(Canvas c,float x,float y,float ww,float hh){
            p.setStrokeWidth(5); p.setColor(Color.rgb(82,57,35)); c.drawLine(x+7,y,x+7,y+hh,p);
            Path fl=new Path(); fl.moveTo(x+8,y+4); fl.lineTo(x+ww,y+10); fl.lineTo(x+ww*.88f,y+hh*.52f); fl.lineTo(x+8,y+hh*.46f); fl.close();
            p.setColor(Color.rgb(239,98,103)); c.drawPath(fl,p);
            text(c,"24~26 AUG",x+ww*.48f,y+hh*.20f,8.4f,Color.WHITE,true,Paint.Align.CENTER);
            text(c,"HOKKAIDO TRIP",x+ww*.45f,y+hh*.36f,6.2f,Color.WHITE,true,Paint.Align.CENTER);
        }

        private void outlinedText(Canvas c,String s,float x,float y,float z,int fill,int stroke){
            p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity); p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD)); p.setTextAlign(Paint.Align.CENTER);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(7); p.setColor(stroke); c.drawText(s,x,y,p);
            p.setStyle(Paint.Style.FILL); p.setColor(fill); c.drawText(s,x,y,p);
        }

        private void woodSign(Canvas c,RectF r,String day,String name,String sub,int accent,boolean selectedCard){
            softShadow(c,r,20); box(c,r,Color.rgb(255,239,191),20);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(selectedCard?4:2); p.setColor(selectedCard?GREEN:Color.rgb(174,132,76)); c.drawRoundRect(r,20,20,p); p.setStyle(Paint.Style.FILL);
            p.setColor(Color.argb(34,140,93,48)); c.drawRoundRect(new RectF(r.left+18,r.top+16,r.right-18,r.top+19),2,2,p); c.drawRoundRect(new RectF(r.left+28,r.bottom-19,r.right-25,r.bottom-16),2,2,p);
            p.setColor(accent); c.drawCircle(r.left+24,r.centerY(),11,p);
            text(c,day,r.left+45,r.top+25,7.3f,GREEN,true); text(c,name,r.left+45,r.centerY()+8,14.8f,INK,true); text(c,sub,r.left+45,r.bottom-15,7.3f,Color.GRAY,false);
        }

        private void navCell(Canvas c,RectF r,String icon,String label,boolean active,int accent){
            if(active) box(c,new RectF(r.left+4,r.top+4,r.right-4,r.bottom-4),Color.rgb(232,247,222),20);
            p.setColor(accent); c.drawCircle(r.centerX(),r.top+18,5,p);
            text(c,icon,r.centerX(),r.top+25,10,active?GREEN:INK,true,Paint.Align.CENTER);
            text(c,label,r.centerX(),r.bottom-9,7.2f,active?GREEN:Color.GRAY,true,Paint.Align.CENTER);
        }
'''

marker='        private void home(Canvas c){'
idx=s.find(marker)
if idx<0: raise SystemExit('v1.1 helper insertion marker missing')
s=s[:idx]+helpers+'\n'+s[idx:]

path.write_text(s)
print('Applied V1.1 Concept Art UI patch')
