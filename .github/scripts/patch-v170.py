from pathlib import Path
import re

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.6.3 · PLAYER SETUP' not in s:
    raise SystemExit('v1.7.0 base version not found')
s=s.replace('V1.6.3 · PLAYER SETUP','V1.7.0 · KOREA FIELD TEST',1)

# -----------------------------------------------------------------------------
# 1) Course pack: keep the 3 Hokkaido courses, add 2 Korea field-test courses.
# Royal Links source values are official WHITE-tee meters. The internal legacy
# array is yard-based, so we store yard-equivalents that round-trip exactly to
# the published meter values through the existing *.9144 display conversion.
# Naepo exact per-hole lengths are intentionally NOT fabricated; they are field
# calibrated from saved TEE/GREEN GPS points during the practice round.
# -----------------------------------------------------------------------------
a=s.find('        private final String[] ko=')
b=s.find('        private int selected=',a)
if a<0 or b<0:
    raise SystemExit('v1.7.0 course data block not found')
course_data=r'''        private final String[] ko={"가미시호로 골프장","후라노 골프코스","사호로 컨트리클럽","내포골프클럽","로얄링스CC"};
        private final String[][] variants={{"CHAMPIONS","MASTERS"},{"PALMER","KING"},{"OUT / IN","OUT / IN"},{"RED → YELLOW","YELLOW → RED"},{"QUEENS","KINGS"}};
        private final double[] courseLat={43.2570513,43.3351203,43.1551590,36.6743245,36.7224490956};
        private final double[] courseLon={143.2283621,142.4817967,142.8070984,126.6698247,126.3387438841};

        private final int[][][] yards={
            {{523,413,170,366,361,351,135,358,481,415,183,395,167,370,509,426,399,516},
             {454,516,416,155,331,369,373,150,367,393,351,132,455,328,167,469,356,370}},
            {{470,410,171,411,545,426,400,174,379,395,132,420,342,414,527,182,388,525},
             {313,168,401,523,386,335,175,359,489,350,312,535,346,151,360,170,422,506}},
            {{395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493},
             {395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493}},
            {{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
             {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}},
            {{514,383,344,131,350,377,563,159,355,372,558,383,137,344,339,541,131,334},
             {350,481,279,153,514,323,159,366,372,476,372,159,366,361,120,498,366,427}}
        };
        private final int[][][] pars={
            {{5,4,3,4,4,4,3,4,5,4,3,4,3,4,5,4,4,5},
             {5,5,4,3,4,4,4,3,4,4,4,3,5,4,3,5,4,5}},
            {{5,4,3,4,5,4,4,3,4,4,3,4,4,4,5,3,4,5},
             {4,3,4,5,4,4,3,4,5,4,4,5,4,3,4,3,4,5}},
            {{4,5,4,3,4,5,4,3,4,4,3,4,5,4,3,4,4,5},
             {4,5,4,3,4,5,4,3,4,4,3,4,5,4,3,4,4,5}},
            {{4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4},
             {4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4}},
            {{5,4,4,3,4,4,5,3,4,4,5,4,3,4,4,5,3,4},
             {4,5,4,3,5,4,3,4,4,5,4,3,4,4,3,5,4,4}}
        };

'''
s=s[:a]+course_data+s[b:]

# Five selectable cards instead of three.
s=re.sub(r'private final RectF\[\] cards=\{[^;]+\};',
         'private final RectF[] cards={new RectF(),new RectF(),new RectF(),new RectF(),new RectF()};',s,count=1)

# Extra hit target for Naepo PAR field calibration.
anchor='        private final RectF playerNamesBtn=new RectF();'
if anchor not in s:
    raise SystemExit('v1.7.0 player setup rect anchor missing')
s=s.replace(anchor,anchor+'\n        private final RectF parCycleBtn=new RectF();',1)

# -----------------------------------------------------------------------------
# 2) First screen: 3 JP courses + KOREA FIELD TEST section with Taegeukgi.
# Rebuild as vector UI so all 5 cards remain crisp at any Android resolution.
# -----------------------------------------------------------------------------
start=s.find('        private void home(Canvas c){')
end=s.find('        private void round(Canvas c){',start)
if start<0 or end<0:
    raise SystemExit('v1.7.0 home block not found')
home=r'''        private void home(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;
            c.drawColor(BG);
            RectF hero=new RectF(0,0,w,h*.192f);gradient(c,hero,Color.rgb(242,250,229),Color.rgb(224,244,213),0);
            text(c,"北海道ゴルフ",m,h*.060f,22,INK,true);
            text(c,"GPSキャディ",m,h*.108f,37,GREEN,true);
            pill(c,new RectF(m,h*.128f,m+w*.49f,h*.165f),Color.rgb(229,244,218),"V1.7 · KOREA FIELD TEST",GREEN,8.0f);
            mascot(c,w*.84f,h*.091f,28,true);
            drawKoreaFlag(c,new RectF(w*.705f,h*.130f,w*.925f,h*.178f));

            text(c,"HOKKAIDO · TRIP PACK",m,h*.224f,10,GREEN,true);
            float top=h*.244f,ch=h*.066f,gap=h*.009f;int[] ac={Color.rgb(174,222,92),YELLOW,SKY};
            for(int i=0;i<3;i++){
                float y=top+i*(ch+gap);cards[i].set(m,y,w-m,y+ch);
                softShadow(c,cards[i],24);box(c,cards[i],selected==i?Color.rgb(238,249,222):CARD,24);
                p.setColor(ac[i]);c.drawCircle(m+25,y+ch*.36f,10,p);
                text(c,"JP 0"+(i+1),m+44,y+ch*.32f,8,GREEN,true);
                text(c,ko[i],m+20,y+ch*.68f,15.5f,INK,true);
                text(c,variants[i][0]+(i<2?" / "+variants[i][1]:""),w*.58f,y+ch*.69f,8.2f,Color.GRAY,false);
                if(location!=null){int dm=(int)Math.round(distanceToCourse(location,i));String ds=dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km";pill(c,new RectF(w*.75f,y+10,w*.92f,y+42),SOFT,ds,selected==i?GREEN:Color.GRAY,6.7f);}
                if(selected==i){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(GREEN);c.drawRoundRect(cards[i],24,24,p);p.setStyle(Paint.Style.FILL);}
            }

            float ky=h*.494f;drawKoreaFlag(c,new RectF(m,ky-26,m+96,ky+24));
            text(c,"KOREA · PRACTICE TEST",m+112,ky+4,10,DEEP,true);
            String[] sub={"9H TWO-GREEN · FIELD GPS CAL","OFFICIAL WHITE · QUEENS / KINGS"};
            float ktop=h*.522f,kch=h*.073f,kgap=h*.010f;
            for(int j=0;j<2;j++){
                int i=3+j;float y=ktop+j*(kch+kgap);cards[i].set(m,y,w-m,y+kch);
                int bg=selected==i?Color.rgb(236,248,225):CARD;softShadow(c,cards[i],26);box(c,cards[i],bg,26);
                RectF badge=new RectF(m+16,y+14,m+108,y+48);box(c,badge,j==0?Color.rgb(255,238,229):Color.rgb(226,244,250),16);
                goldText(c,j==0?"TEST":"OFFICIAL",badge.centerX(),badge.centerY(),10.5f,j==0?CORAL:BLUE);
                text(c,ko[i],m+22,y+kch*.62f,18,INK,true);
                text(c,sub[j],w*.48f,y+kch*.63f,8.0f,Color.GRAY,false);
                if(location!=null){int dm=(int)Math.round(distanceToCourse(location,i));String ds=dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km";pill(c,new RectF(w*.75f,y+12,w*.92f,y+44),SOFT,ds,selected==i?GREEN:Color.GRAY,6.7f);}
                if(selected==i){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4);p.setColor(GREEN);c.drawRoundRect(cards[i],26,26,p);p.setStyle(Paint.Style.FILL);}
            }

            float vy=h*.704f;text(c,"코스 / 그린 순서",m,vy-10,9,Color.GRAY,true);
            varA.set(m,vy,w*.48f,vy+h*.050f);varB.set(w*.52f,vy,w-m,vy+h*.050f);
            if(selected>=0){
                goldButton(c,varA,variant==0?GREEN:SOFT,variants[selected][0],variant==0?Color.WHITE:INK,16.0f);
                goldButton(c,varB,variant==1?GREEN:SOFT,variants[selected][1],variant==1?Color.WHITE:INK,16.0f);
            }
            start.set(m,h*.790f,w-m,h*.858f);gradient(c,start,selected>=0?DEEP:Color.LTGRAY,selected>=0?GREEN:Color.GRAY,32);sheen(c,start,32);
            goldText(c,selected>=0?"라운드 시작  >":"골프장을 먼저 선택",start.centerX(),start.centerY(),20.0f,selected>=0?Color.WHITE:Color.DKGRAY);
            String gs=location==null?"GPS 준비 중":"GPS READY";int gc=location==null?CORAL:GREEN;
            pill(c,new RectF(m,h*.883f,w*.38f,h*.921f),location==null?Color.rgb(255,238,229):Color.rgb(226,244,212),gs,gc,7.2f);
            text(c,"한국 테스트: 현장 GPS 저장값 우선 · 인터넷 없이 라운드 가능",m,h*.955f,8.4f,Color.GRAY,false);
        }

        private void drawKoreaFlag(Canvas c,RectF r){
            float rad=Math.min(16,r.height()*.20f);softShadow(c,r,rad);box(c,r,Color.WHITE,rad);
            float cx=r.left+r.width()*.42f,cy=r.centerY(),rr=Math.min(r.height()*.27f,r.width()*.13f);
            p.setColor(Color.rgb(205,46,58));c.drawArc(new RectF(cx-rr,cy-rr,cx+rr,cy+rr),180,180,true,p);
            p.setColor(Color.rgb(0,71,160));c.drawArc(new RectF(cx-rr,cy-rr,cx+rr,cy+rr),0,180,true,p);
            p.setColor(Color.rgb(205,46,58));c.drawCircle(cx-rr*.50f,cy,rr*.50f,p);
            p.setColor(Color.rgb(0,71,160));c.drawCircle(cx+rr*.50f,cy,rr*.50f,p);
            float bx=r.left+r.width()*.12f,by=r.top+r.height()*.24f,bw=r.width()*.13f,bh=Math.max(2,r.height()*.055f);
            p.setColor(Color.rgb(25,25,25));for(int k=0;k<3;k++)c.drawRoundRect(new RectF(bx,by+k*bh*1.8f,bx+bw,by+k*bh*1.8f+bh),bh/2,bh/2,p);
            bx=r.right-r.width()*.25f;by=r.bottom-r.height()*.42f;for(int k=0;k<3;k++)c.drawRoundRect(new RectF(bx,by+k*bh*1.8f,bx+bw,by+k*bh*1.8f+bh),bh/2,bh/2,p);
            text(c,"KR",r.right-r.width()*.12f,r.centerY()+4,8.5f,DEEP,true,Paint.Align.CENTER);
        }

'''
s=s[:start]+home+s[end:]

# -----------------------------------------------------------------------------
# 3) Korea live-course view: high-resolution Canvas vector yardage.
# Naepo = field calibration mode; Royal Links = official WHITE-meter values.
# -----------------------------------------------------------------------------
round_marker='        private void round(Canvas c){'
if round_marker not in s:
    raise SystemExit('v1.7.0 round marker missing')
s=s.replace(round_marker,round_marker+'\n            if(selected>=3){roundKorea(c);return;}',1)

insert_at=s.find('        private void round(Canvas c){')
round_korea=r'''        private void roundKorea(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;int par=currentPar();int officialM=currentOfficialM();
            c.drawColor(BG);
            RectF head=new RectF(0,0,w,h*.133f);gradient(c,head,DEEP,GREEN,0);
            drawKoreaFlag(c,new RectF(w*.76f,h*.020f,w*.94f,h*.064f));
            text(c,ko[selected],m,h*.055f,21,Color.WHITE,true);
            text(c,variants[selected][variant]+" · "+koreaHoleLabel(),m,h*.090f,11,Color.rgb(218,242,222),true);
            parCycleBtn.set(w*.55f,h*.072f,w*.70f,h*.116f);
            goldButton(c,parCycleBtn,Color.argb(55,255,255,255),"PAR "+par+(selected==3?" ↻":""),Color.WHITE,13.0f);
            String len=selected==4?("WHITE "+officialM+"m"):(officialM>0?("FIELD "+officialM+"m"):"GPS CAL");
            pill(c,new RectF(w*.72f,h*.077f,w*.94f,h*.117f),Color.rgb(235,247,229),len,GREEN,7.6f);

            GeoRef green=greenCenterRef(hole),gf=getRef("gf",hole),gb=getRef("gb",hole);Distances ds=distances3(gf,green,gb);
            RectF range=new RectF(m,h*.145f,w-m,h*.230f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),26);sheen(c,range,26);
            if(selected==3){
                metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.163f);
                metric(c,"CENTER",ds.center<0?"--":ds.center+"m",w*.50f,h*.163f);
                metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.163f);
            }else{
                metric(c,"OFFICIAL",officialM+"m",w*.22f,h*.163f);
                metric(c,"PAR",""+par,w*.50f,h*.163f);
                metric(c,"TEE","WHITE",w*.78f,h*.163f);
            }
            pill(c,new RectF(m,h*.236f,w*.29f,h*.266f),gpsBg(),gpsStatusShort(),gpsColor(),7.0f);
            String src=selected==4?"OFFICIAL METER VECTOR":"FIELD GPS · TWO GREEN";
            pill(c,new RectF(w*.31f,h*.236f,w*.69f,h*.266f),CARD,src,selected==4?BLUE:GREEN,6.5f);
            autoBtn.set(w*.71f,h*.236f,w-m,h*.266f);pill(c,autoBtn,autoHole?Color.rgb(229,244,218):CARD,autoHole?"AUTO ON":"AUTO OFF",autoHole?GREEN:Color.GRAY,6.8f);

            courseRect.set(m,h*.278f,w-m,h*.600f);drawKoreaYardage(c,courseRect,par,officialM);
            drawCapturedHazardSummary(c,courseRect);drawHazardCaptureButtons(c,courseRect);drawHolePager(c,h*.286f);

            RectF strategy=new RectF(m,h*.616f,w-m,h*.675f);softShadow(c,strategy,20);box(c,strategy,CARD,20);
            text(c,"공략 / 테스트 포인트",m+14,h*.639f,8.8f,GREEN,true);
            textFit(c,koreaStrategyNote(),m+14,h*.662f,w-m-14,8.2f,INK,true);

            boolean capReady=previewMode || (location!=null && location.getAccuracy()<=12 && fixAgeSec()<=15);
            int gBg=capReady?(green==null?CORAL:DEEP):Color.rgb(150,160,150),tBg=capReady?(getRef("t",hole)==null?Color.rgb(53,139,94):DEEP):Color.rgb(150,160,150);
            greenSave.set(m,h*.692f,w*.38f,h*.752f);teeSave.set(w*.405f,h*.692f,w*.65f,h*.752f);mapLaunch.set(w*.675f,h*.692f,w-m,h*.752f);
            goldButton(c,greenSave,gBg,greenSaveLabel(),Color.WHITE,15.0f);goldButton(c,teeSave,tBg,getRef("t",hole)==null?"TEE 저장":"TEE OK",Color.WHITE,15.0f);goldButton(c,mapLaunch,CARD,"외부 지도",INK,15.0f);

            drawPlayerTabs(c,h*.772f);int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);
            RectF quick=new RectF(m,h*.825f,w-m,h*.902f);softShadow(c,quick,22);box(c,quick,CARD,22);
            text(c,"타수",m+18,h*.850f,9,Color.GRAY,true);goldText(c,""+stroke,w*.28f,h*.863f,25f,INK);
            minus.set(m+72,h*.840f,m+132,h*.892f);plus.set(w*.355f,h*.840f,w*.435f,h*.892f);
            goldButton(c,minus,SOFT,"−",INK,19f);goldButton(c,plus,Color.rgb(229,244,218),"+",GREEN,19f);
            text(c,"퍼트",w*.52f,h*.850f,9,Color.GRAY,true);goldText(c,""+putt,w*.69f,h*.863f,25f,INK);
            pm.set(w*.535f,h*.840f,w*.605f,h*.892f);pp.set(w*.82f,h*.840f,w*.90f,h*.892f);
            goldButton(c,pm,SOFT,"−",INK,19f);goldButton(c,pp,Color.rgb(226,245,250),"+",BLUE,19f);
            drawTapBurst(c,h);setFourNav(w,h);drawGoldenNav(c);
        }

        private int currentOfficialM(){int y=currentYards();return y<=0?0:(int)Math.round(y*.9144);}
        private int naepoPhysicalHole(int h){return ((h-1)%9)+1;}
        private String koreaHoleLabel(){
            if(selected!=3)return "H"+hole;
            int ph=naepoPhysicalHole(hole);boolean second=hole>9;String first=variant==0?"RED":"YELLOW",secondName=variant==0?"YELLOW":"RED";
            return "H"+ph+" · "+(second?secondName:first)+(second?" · 2ND":" · 1ST");
        }
        private void cycleNaepoPar(){
            if(selected!=3)return;int ph=naepoPhysicalHole(hole),v=statePrefs.getInt("naepo_par_"+ph,4);v=v>=5?3:v+1;statePrefs.edit().putInt("naepo_par_"+ph,v).apply();showToast("내포 H"+ph+" PAR "+v+" 저장");invalidate();
        }
        private String koreaStrategyNote(){
            if(selected==3){
                int m=currentOfficialM();
                return m>0?("FIELD CAL 완료 · TEE↔GREEN 직선 "+m+"m · 벙커/워터 GPS를 현장에서 추가 저장"):("내포 9H TWO-GREEN 테스트 · TEE와 GREEN을 저장하면 이 홀의 실제 GPS 거리로 전환");
            }
            if(variant==0){
                if(hole==1)return "QUEENS 1H · 좌 도그레그 · 첫 벙커 오른쪽 티샷, 세컨은 좌측 페어웨이로 그린 오픈";
                if(hole==17)return "QUEENS 17H · 우측 워터 + 그린 주변 벙커 · 바람까지 감안한 정교한 아이언";
                return "QUEENS · 공식 WHITE 거리 기반 벡터 야디지 · 링크스 바람과 페어웨이 벙커 위치에 주의";
            }
            if(hole==12)return "KINGS 12H · 긴 PAR3 · 맞바람 + 포트벙커를 감안해 넉넉한 클럽 선택";
            return "KINGS · 공식 WHITE 거리 기반 벡터 야디지 · 갈대습지/워터와 바람을 우선 체크";
        }

        private void drawKoreaYardage(Canvas c,RectF r,int par,int officialM){
            float w=r.width(),hh=r.height();gradient(c,r,Color.rgb(228,246,216),Color.rgb(193,231,187),30);c.save();c.clipRect(r);
            int seed=hole*31+variant*17+selected*7;float bend=((seed%7)-3)*w*.020f,cx=r.centerX();
            Path fw=new Path();fw.moveTo(cx-w*.075f,r.bottom-20);fw.cubicTo(cx+w*.03f+bend,r.top+hh*.72f,cx-w*.10f+bend,r.top+hh*.38f,cx-w*.055f+bend,r.top+65);fw.lineTo(cx+w*.060f+bend,r.top+65);fw.cubicTo(cx+w*.15f+bend,r.top+hh*.38f,cx+w*.11f+bend,r.top+hh*.72f,cx+w*.075f,r.bottom-20);fw.close();p.setColor(Color.rgb(83,171,84));c.drawPath(fw,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4);p.setColor(Color.argb(80,255,255,255));for(int k=1;k<5;k++){float y=r.bottom-k*hh*.16f;c.drawLine(r.left+20,y,r.right-20,y,p);}p.setStyle(Paint.Style.FILL);
            // Schematic water/bunker decoration only; factual distance is the large chip below.
            if(selected==4 && seed%2==0){p.setColor(Color.rgb(76,174,212));RectF wa=new RectF(r.left+18,r.top+hh*.43f,r.left+w*.23f,r.top+hh*.66f);c.drawOval(wa,p);}
            p.setColor(Color.rgb(238,219,153));for(int k=0;k<2;k++){float bx=cx+(k==0?-1:1)*(w*.15f+(seed%3)*5),by=r.top+hh*(.30f+k*.28f);c.drawOval(new RectF(bx-22,by-14,bx+22,by+14),p);}
            // Tee.
            p.setColor(DEEP);c.drawRoundRect(new RectF(cx-34,r.bottom-36,cx+34,r.bottom-18),8,8,p);text(c,"TEE",cx,r.bottom-48,7.5f,DEEP,true,Paint.Align.CENTER);
            if(selected==3){
                boolean second=hole>9;String active=(variant==0?(second?"Y":"R"):(second?"R":"Y"));
                p.setColor(Color.rgb(55,141,74));c.drawOval(new RectF(cx-90,r.top+34,cx-18,r.top+72),p);c.drawOval(new RectF(cx+18,r.top+34,cx+90,r.top+72),p);
                p.setColor(active.equals("R")?Color.rgb(215,48,55):Color.rgb(245,195,32));float gx=active.equals("R")?cx-54:cx+54;c.drawCircle(gx,r.top+50,8,p);
                pill(c,new RectF(r.left+18,r.top+18,r.left+w*.42f,r.top+56),Color.argb(235,255,255,255),"TWO-GREEN · "+(active.equals("R")?"RED":"YELLOW"),DEEP,7.2f);
                String cal=officialM>0?(officialM+"m · GPS FIELD CAL"):"SAVE TEE + GREEN";pill(c,new RectF(r.left+w*.46f,r.bottom-72,r.right-18,r.bottom-30),Color.argb(240,255,255,255),cal,officialM>0?GREEN:CORAL,8.0f);
            }else{
                p.setColor(Color.rgb(48,135,70));c.drawOval(new RectF(cx-56+bend,r.top+34,cx+56+bend,r.top+74),p);p.setColor(CORAL);c.drawRect(cx+bend,r.top+22,cx+bend+3,r.top+52,p);Path fl=new Path();fl.moveTo(cx+bend+3,r.top+22);fl.lineTo(cx+bend+30,r.top+31);fl.lineTo(cx+bend+3,r.top+38);fl.close();c.drawPath(fl,p);
                pill(c,new RectF(r.left+18,r.top+18,r.left+w*.43f,r.top+56),Color.argb(238,255,255,255),"OFFICIAL WHITE · PAR "+par,DEEP,7.0f);
                pill(c,new RectF(r.left+w*.54f,r.bottom-76,r.right-18,r.bottom-28),Color.argb(244,255,255,255),officialM+"m",GREEN,15.5f);
            }
            text(c,"VECTOR YARDAGE · CRISP AT DEVICE RESOLUTION",r.centerX(),r.bottom-6,6.5f,Color.argb(150,34,55,40),true,Paint.Align.CENTER);c.restore();
        }

'''
s=s[:insert_at]+round_korea+s[insert_at:]

# -----------------------------------------------------------------------------
# 4) Round-session persistence. Each start creates a unique round ID so a new
# practice round never overwrites a prior round. The full active-player set,
# names, 18-hole score/putt values, course/variant and timestamps are persisted.
# -----------------------------------------------------------------------------
helper_old=r'''        private int currentPar(){return parForHole(hole);}
        private int parForHole(int h){return pars[selected][variant][h-1];}
        private int currentYards(){return yards[selected][variant][hole-1];}
        private int getStroke(int pl,int h,int par){return scorePrefs.getInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,par);}
        private int getPutt(int pl,int h){return scorePrefs.getInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,0);}
        private void setStroke(int pl,int h,int v){scorePrefs.edit().putInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply();}
        private void setPutt(int pl,int h,int v){scorePrefs.edit().putInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply();}
        private int nearestCourse(Location l){int best=-1;float bd=Float.MAX_VALUE;for(int i=0;i<3;i++){float d=(float)distanceToCourse(l,i);if(d<bd){bd=d;best=i;}}return best;}
        private double distanceToCourse(Location l,int i){if(l==null)return -1;float[] o=new float[1];Location.distanceBetween(l.getLatitude(),l.getLongitude(),courseLat[i],courseLon[i],o);return o[0];}
        private int clamp(int v,int a,int b){return Math.max(a,Math.min(b,v));}
'''
if helper_old not in s:
    raise SystemExit('v1.7.0 shared helper block not found')
helper_new=r'''        private int currentPar(){return parForHole(hole);}
        private int parForHole(int h){
            if(selected==3){int ph=((h-1)%9)+1;return clamp(statePrefs.getInt("naepo_par_"+ph,4),3,5);}
            return pars[selected][variant][h-1];
        }
        private int currentYards(){
            if(selected==3){GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t!=null&&g!=null)return Math.round(distance(t.lat,t.lon,g.lat,g.lon)/.9144f);return 0;}
            return yards[selected][variant][hole-1];
        }
        private String currentRoundId(){String r=statePrefs.getString("round_id","");return r==null?"":r;}
        private String roundScoreKey(String prefix,int pl,int h){String r=currentRoundId();return r.length()>0?(prefix+"_"+r+"_"+pl+"_"+h):(prefix+"_"+selected+"_"+variant+"_"+pl+"_"+h);}
        private int getStroke(int pl,int h,int par){return scorePrefs.getInt(roundScoreKey("s",pl,h),par);}
        private int getPutt(int pl,int h){return scorePrefs.getInt(roundScoreKey("p",pl,h),0);}
        private void setStroke(int pl,int h,int v){scorePrefs.edit().putInt(roundScoreKey("s",pl,h),v).apply();}
        private void setPutt(int pl,int h,int v){scorePrefs.edit().putInt(roundScoreKey("p",pl,h),v).apply();}
        private void beginRoundSession(){
            long now=System.currentTimeMillis();String rid="R"+now+"_C"+selected+"V"+variant;
            statePrefs.edit().putString("round_id",rid).putLong("round_started_at",now).putInt("round_course",selected).putInt("round_variant",variant).apply();
        }
        private int nearestCourse(Location l){int best=-1;float bd=Float.MAX_VALUE;for(int i=0;i<courseLat.length;i++){float d=(float)distanceToCourse(l,i);if(d<bd){bd=d;best=i;}}return best;}
        private double distanceToCourse(Location l,int i){if(l==null||i<0||i>=courseLat.length)return -1;float[] o=new float[1];Location.distanceBetween(l.getLatitude(),l.getLongitude(),courseLat[i],courseLon[i],o);return o[0];}
        private int clamp(int v,int a,int b){return Math.max(a,Math.min(b,v));}
        private int roundRecordCount(){String ids=scorePrefs.getString("round_history_ids","");if(ids==null||ids.trim().length()==0)return 0;return ids.split(",").length;}
        private void saveRoundSnapshot(){
            String rid=currentRoundId();if(rid.length()==0)return;
            try{
                JSONObject root=new JSONObject();root.put("schema","HokkaidoGolfGPS.Round.v2");root.put("roundId",rid);root.put("startedAt",statePrefs.getLong("round_started_at",System.currentTimeMillis()));root.put("updatedAt",System.currentTimeMillis());root.put("courseIndex",selected);root.put("course",ko[selected]);root.put("variant",variants[selected][variant]);root.put("playerCount",playerCount());
                JSONObject players=new JSONObject();
                for(int pl=0;pl<playerCount();pl++){
                    JSONObject po=new JSONObject();po.put("name",playerName(pl));int total=0,putts=0,parTotal=0;JSONObject holes=new JSONObject();
                    for(int h=1;h<=18;h++){int pa=parForHole(h),sv=getStroke(pl,h,pa),pu=getPutt(pl,h);JSONObject ho=new JSONObject();ho.put("par",pa);ho.put("score",sv);ho.put("putt",pu);holes.put("h"+h,ho);total+=sv;putts+=pu;parTotal+=pa;}
                    po.put("total",total);po.put("toPar",total-parTotal);po.put("putts",putts);po.put("holes",holes);players.put("p"+pl,po);
                }
                root.put("players",players);scorePrefs.edit().putString("round_record_"+rid,root.toString()).apply();
                String ids=scorePrefs.getString("round_history_ids","");if(ids==null)ids="";boolean found=false;for(String x:ids.split(","))if(x.equals(rid)){found=true;break;}if(!found)scorePrefs.edit().putString("round_history_ids",ids.length()==0?rid:(ids+","+rid)).apply();
            }catch(Exception ignored){}
        }
'''
s=s.replace(helper_old,helper_new,1)

# Starting a round creates the new record namespace, both when names are already
# configured and when the setup dialog is used for the first time.
old='''                if(player>=n)player=0;dlg.dismiss();showToast(n+"명 플레이어 설정 완료");if(startAfter){screen=1;saveState();}invalidate();'''
new='''                if(player>=n)player=0;dlg.dismiss();showToast(n+"명 플레이어 설정 완료");if(startAfter){beginRoundSession();screen=1;saveState();}invalidate();'''
if old not in s:
    raise SystemExit('v1.7.0 player dialog start anchor missing')
s=s.replace(old,new,1)
old='''                if(selected>=0&&start.contains(x,y)){if(!playerNamesReady()){showPlayerNamesDialog(true);return true;}screen=1;saveState();invalidate();return true;}'''
new='''                if(selected>=0&&start.contains(x,y)){if(!playerNamesReady()){showPlayerNamesDialog(true);return true;}beginRoundSession();screen=1;saveState();invalidate();return true;}'''
if old not in s:
    raise SystemExit('v1.7.0 direct start anchor missing')
s=s.replace(old,new,1)

# Home touch: all 5 course cards. Naepo and Royal both support their B variant.
s=s.replace('for(int i=0;i<3;i++)if(cards[i].contains(x,y)){selected=i;if(i==2)variant=0;saveState();invalidate();return true;}',
            'for(int i=0;i<5;i++)if(cards[i].contains(x,y)){selected=i;if(i==2)variant=0;else if(variant>1)variant=0;saveState();invalidate();return true;}',1)
# Only Sahoro has a single effective variant.
s=s.replace('if(varB.contains(x,y)){variant=selected==2?0:1;saveState();invalidate();return true;}',
            'if(varB.contains(x,y)){variant=selected==2?0:1;saveState();invalidate();return true;}',1)

# Naepo PAR cycle is a live field-calibration control.
touch_head='''            if(screen==1){'''
if touch_head not in s:
    raise SystemExit('v1.7.0 screen1 touch anchor missing')
s=s.replace(touch_head,touch_head+'''\n                if(selected==3 && parCycleBtn.contains(x,y)){cycleNaepoPar();return true;}''',1)

# -----------------------------------------------------------------------------
# 5) Multi-player round summary + persistent snapshot. Preserve Field Pack
# backup/restore controls added in V1.6.1.
# -----------------------------------------------------------------------------
ss=s.find('        private void summary(Canvas c){')
se=s.find('        private GeoRef calibratedMapRef(',ss)
if ss<0 or se<0:
    raise SystemExit('v1.7.0 summary block not found')
summary=r'''        private void summary(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;int n=Math.max(1,playerCount());
            c.drawColor(DEEP);drawKoreaFlag(c,new RectF(w*.72f,h*.050f,w*.94f,h*.100f));
            text(c,"라운드 요약",m,h*.070f,27,Color.WHITE,true);text(c,ko[selected]+" · "+variants[selected][variant],m,h*.105f,12,Color.rgb(216,242,222),true);
            String rid=currentRoundId();long started=statePrefs.getLong("round_started_at",System.currentTimeMillis());String date=new java.text.SimpleDateFormat("yyyy.MM.dd HH:mm",java.util.Locale.KOREA).format(new java.util.Date(started));text(c,date,m,h*.134f,9,Color.rgb(216,242,222),false);
            saveRoundSnapshot();

            int[] totals=new int[4],putts=new int[4],parTotals=new int[4];
            for(int pl=0;pl<n;pl++)for(int i=1;i<=18;i++){int pa=parForHole(i),sv=getStroke(pl,i,pa);parTotals[pl]+=pa;totals[pl]+=sv;putts[pl]+=getPutt(pl,i);}
            float top=h*.188f,gap=h*.018f,cardH=h*.125f,used=n*cardH+(n-1)*gap;if(used>h*.55f){cardH=(h*.55f-gap*(n-1))/n;used=n*cardH+(n-1)*gap;}top+=(h*.55f-used)/2f;
            int[] dots={Color.rgb(112,190,87),SKY,CORAL,YELLOW};
            for(int pl=0;pl<n;pl++){
                float y=top+pl*(cardH+gap);RectF card=new RectF(m,y,w-m,y+cardH);softShadow(c,card,26);box(c,card,Color.WHITE,26);
                p.setColor(dots[pl]);c.drawCircle(card.left+28,card.top+30,11,p);text(c,playerName(pl),card.left+50,card.top+38,18,INK,true);
                int d=totals[pl]-parTotals[pl];String rel=d==0?"E":(d>0?"+"+d:""+d);goldText(c,rel,card.right-115,card.centerY(),31f,d>0?CORAL:(d<0?GREEN:INK));
                text(c,"TOTAL "+totals[pl]+"  ·  PUTT "+putts[pl],card.left+50,card.bottom-24,10,Color.GRAY,true);
            }
            RectF saved=new RectF(m,h*.765f,w-m,h*.815f);box(c,saved,Color.rgb(224,244,213),24);goldText(c,"ROUND SAVED · "+roundRecordCount()+" RECORDS",saved.centerX(),saved.centerY(),14f,DEEP);
            packExportBtn.set(m,h*.835f,w*.485f,h*.895f);packImportBtn.set(w*.515f,h*.835f,w-m,h*.895f);goldButton(c,packExportBtn,Color.rgb(238,246,226),"PACK 백업",DEEP,14.5f);goldButton(c,packImportBtn,Color.rgb(238,246,226),"PACK 복원",DEEP,14.5f);
            setFourNav(w,h);drawGoldenNav(c);
        }

'''
s=s[:ss]+summary+s[se:]

p.write_text(s)
print('applied v1.7.0 Korea field-test pack + round persistence')
