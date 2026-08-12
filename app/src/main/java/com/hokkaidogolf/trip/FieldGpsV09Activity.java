package com.hokkaidogolf.trip;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.SystemClock;
import android.provider.Settings;
import android.view.MotionEvent;
import android.view.View;

public class FieldGpsV09Activity extends Activity implements LocationListener {
    private static final int REQ = 1909;
    private LocationManager lm;
    private GolfView view;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        boolean preview = getIntent().getBooleanExtra("preview", false);
        view = new GolfView(this, preview);
        setContentView(view);
        lm = (LocationManager)getSystemService(LOCATION_SERVICE);
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, REQ);
        } else startGps();
    }

    private void startGps() {
        if (lm == null || checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) return;
        try { lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 700, 0.6f, this); } catch (Exception ignored) {}
    }

    @Override public void onLocationChanged(Location l) { if (view != null) view.setLocation(l); }
    @Override protected void onPause() { super.onPause(); try { if (lm != null) lm.removeUpdates(this); } catch (Exception ignored) {} }
    @Override protected void onResume() { super.onResume(); startGps(); }
    @Override public void onRequestPermissionsResult(int r, String[] p, int[] g) {
        super.onRequestPermissionsResult(r,p,g);
        if (r == REQ && g.length > 0 && g[0] == PackageManager.PERMISSION_GRANTED) startGps();
    }

    static final class GolfView extends View {
        private final Context ctx;
        private final boolean previewMode;
        private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final SharedPreferences scorePrefs, calPrefs, statePrefs;

        private final String[] ko={"가미시호로 골프장","후라노 골프코스","사호로 컨트리클럽"};
        private final String[][] variants={{"CHAMPIONS","MASTERS"},{"PALMER","KING"},{"OUT / IN","OUT / IN"}};
        private final double[] courseLat={43.2570513,43.3351203,43.1551590};
        private final double[] courseLon={143.2283621,142.4817967,142.8070984};

        private final int[][][] yards={
            {{523,413,170,366,361,351,135,358,481,415,183,395,167,370,509,426,399,516},
             {454,516,416,155,331,369,373,150,367,393,351,132,455,328,167,469,356,370}},
            {{470,410,171,411,545,426,400,174,379,395,132,420,342,414,527,182,388,525},
             {313,168,401,523,386,335,175,359,489,350,312,535,346,151,360,170,422,506}},
            {{395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493},
             {395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493}}
        };
        private final int[][][] pars={
            {{5,4,3,4,4,4,3,4,5,4,3,4,3,4,5,4,4,5},
             {5,5,4,3,4,4,4,3,4,4,4,3,5,4,3,5,4,5}},
            {{5,4,3,4,5,4,4,3,4,4,3,4,4,4,5,3,4,5},
             {4,3,4,5,4,4,3,4,5,4,4,5,4,3,4,3,4,5}},
            {{4,5,4,3,4,5,4,3,4,4,3,4,5,4,3,4,4,5},
             {4,5,4,3,4,5,4,3,4,4,3,4,5,4,3,4,4,5}}
        };

        private int selected=-1, variant=0, screen=0, hole=1, player=0;
        private boolean autoHole=true, hasTarget=false;
        private float targetX,targetY;
        private Location location;
        private long lastAutoHoleAt=0,lastHoleChange=0,lastTap=0,confirmUntil=0,lastFixElapsed=0;
        private int lastDelta=0,holeDirection=1,confirmKind=0;
        private String toastText=""; private long toastAt=0;

        private final RectF[] cards={new RectF(),new RectF(),new RectF()};
        private final RectF start=new RectF(),varA=new RectF(),varB=new RectF();
        private final RectF courseRect=new RectF(),greenSave=new RectF(),teeSave=new RectF(),mapLaunch=new RectF(),autoBtn=new RectF();
        private final RectF minus=new RectF(),plus=new RectF(),pm=new RectF(),pp=new RectF();
        private final RectF prev=new RectF(),next=new RectF(),mapTab=new RectF(),scoreTab=new RectF();
        private final RectF[] playerTabs={new RectF(),new RectF(),new RectF(),new RectF()};

        private final int BG=Color.rgb(249,250,240),INK=Color.rgb(34,55,40),GREEN=Color.rgb(24,111,68),DEEP=Color.rgb(8,79,52),
                SKY=Color.rgb(96,196,230),BLUE=Color.rgb(75,166,211),CORAL=Color.rgb(255,126,92),YELLOW=Color.rgb(255,208,64),
                CARD=Color.WHITE,SOFT=Color.rgb(241,245,235),AMBER=Color.rgb(184,126,30);

        GolfView(Context c, boolean preview) {
            super(c); ctx=c; previewMode=preview;
            scorePrefs=c.getSharedPreferences("score_v09",MODE_PRIVATE);
            calPrefs=c.getSharedPreferences("cal_v09",MODE_PRIVATE);
            statePrefs=c.getSharedPreferences("state_v09",MODE_PRIVATE);
            p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL));
            setKeepScreenOn(true);
            if (previewMode) { selected=0; variant=0; hole=11; }
            else {
                selected=statePrefs.getInt("selected",-1);
                variant=statePrefs.getInt("variant",0);
                hole=clamp(statePrefs.getInt("hole",1),1,18);
                player=clamp(statePrefs.getInt("player",0),0,3);
                autoHole=statePrefs.getBoolean("auto",true);
            }
        }

        void setLocation(Location l) {
            location=l; lastFixElapsed=SystemClock.elapsedRealtime();
            if (selected<0) { int n=nearestCourse(l); if(n>=0 && distanceToCourse(l,n)<8000) {selected=n;variant=0;saveState();} }
            maybeAutoHole(); invalidate();
        }

        private void saveState(){
            statePrefs.edit().putInt("selected",selected).putInt("variant",variant).putInt("hole",hole).putInt("player",player).putBoolean("auto",autoHole).apply();
        }

        private void maybeAutoHole(){
            if(!autoHole || !gpsUsable() || selected<0 || savedCount("t")<3) return;
            if(SystemClock.uptimeMillis()-lastAutoHoleAt<45000) return;
            int best=-1; float bd=Float.MAX_VALUE;
            for(int h=1;h<=18;h++){
                GeoRef r=getRef("t",h); if(r==null) continue;
                float d=distance(location,r.lat,r.lon); if(d<bd){bd=d;best=h;}
            }
            if(best>0 && best!=hole && bd<80){
                holeDirection=best>hole?1:-1; hole=best; lastHoleChange=SystemClock.uptimeMillis(); lastAutoHoleAt=SystemClock.uptimeMillis(); hasTarget=false;
                saveState(); showToast("TEE 감지 · H"+hole+" 자동 전환");
            }
        }

        @Override protected void onDraw(Canvas c){
            c.drawColor(BG);
            if(screen==0) home(c); else if(screen==1) round(c); else score(c);
            drawToast(c); postInvalidateDelayed(screen==1?50:120);
        }

        private void home(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;
            text(c,"北海道ゴルフ",m,h*.066f,27,INK,true);
            text(c,"GPSキャディ",m,h*.111f,38,GREEN,true);
            pill(c,new RectF(m,h*.135f,m+w*.62f,h*.177f),Color.rgb(229,244,218),"V0.9 · SAFETY + STRATEGY",GREEN,9.2f);
            mascot(c,w*.84f,h*.105f,28,true); speech(c,w*.57f,h*.155f,"코스 공략 탑재!",GREEN);
            text(c,"오늘 어디서 칠까요?",m,h*.222f,18,INK,true);
            text(c,"공식 정규 거리 · GPS 안전잠금 · 현장 좌표 DB · 4인 스코어",m,h*.252f,9.0f,Color.GRAY,false);

            float top=h*.286f,ch=h*.116f,gap=h*.014f; int[] ac={Color.rgb(174,222,92),YELLOW,SKY};
            for(int i=0;i<3;i++){
                float y=top+i*(ch+gap); cards[i].set(m,y,w-m,y+ch);
                softShadow(c,cards[i],26); box(c,cards[i],selected==i?Color.rgb(238,249,222):CARD,26);
                p.setColor(ac[i]); c.drawCircle(m+28,y+30,11,p);
                text(c,"DAY "+(i+1),m+50,y+35,9,GREEN,true);
                text(c,ko[i],m+22,y+71,18,INK,true);
                text(c,variants[i][0]+(i<2?" / "+variants[i][1]:""),m+22,y+95,9.7f,Color.GRAY,false);
                if(location!=null){
                    int dm=(int)Math.round(distanceToCourse(location,i)); String ds=dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km";
                    pill(c,new RectF(w-m-105,y+17,w-m-14,y+48),SOFT,ds,selected==i?GREEN:Color.GRAY,8.2f);
                }
                if(selected==i){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(GREEN);c.drawRoundRect(cards[i],26,26,p);p.setStyle(Paint.Style.FILL);}
            }

            float vy=h*.692f; text(c,"코스 선택",m,vy,10,Color.GRAY,true);
            varA.set(m,vy+12,w*.48f,vy+58); varB.set(w*.52f,vy+12,w-m,vy+58);
            pillButton(c,varA,variant==0?GREEN:CARD,selected<0?"A COURSE":variants[selected][0],variant==0?Color.WHITE:INK);
            pillButton(c,varB,variant==1?GREEN:CARD,selected<0?"B COURSE":variants[selected][1],variant==1?Color.WHITE:INK);
            start.set(m,h*.803f,w-m,h*.88f); gradient(c,start,selected>=0?DEEP:Color.LTGRAY,selected>=0?GREEN:Color.GRAY,36); sheen(c,start,36);
            text(c,selected>=0?"라운드 시작  →":"골프장을 먼저 선택해주세요",w/2,h*.852f,15,selected>=0?Color.WHITE:Color.DKGRAY,true,Paint.Align.CENTER);
            text(c,"모든 거리 m · 정규 티 거리 데이터 검증 완료",w/2,h*.925f,9,Color.GRAY,false,Paint.Align.CENTER);
        }

        private void round(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f; int par=currentPar(); int officialM=(int)Math.round(currentYards()*.9144);
            float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/320.0));

            text(c,ko[selected]+" · "+variants[selected][variant],m,h*.043f,11,Color.GRAY,true);
            text(c,"H"+hole,m,h*.093f,37,INK,true);
            pill(c,new RectF(m+76,h*.062f,m+145,h*.102f),Color.rgb(229,244,218),"PAR "+par,GREEN,10.5f);
            pill(c,new RectF(m+153,h*.062f,m+243,h*.102f),CARD,officialM+"m",INK,10.2f);

            String gps=gpsLabel(); int gpsCol=gpsColor();
            pill(c,new RectF(w-m-140,h*.021f,w-m,h*.061f),gpsBg(),gps,gpsCol,9.1f);

            GeoRef green=getRef("g",hole); Distances ds=distances(green);
            RectF range=new RectF(m,h*.119f,w-m,h*.223f); gradient(c,range,DEEP,GREEN,28); sheen(c,range,28);
            metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.150f);
            metric(c,"CENTER",ds.center<0?"--":ds.center+"m",w*.50f,h*.150f);
            metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.150f);

            int gc=savedCount("g"),tc=savedCount("t");
            pill(c,new RectF(m,h*.231f,w*.30f,h*.262f),gpsBg(),gpsStatusShort(),gpsCol,8.0f);
            pill(c,new RectF(w*.315f,h*.231f,w*.70f,h*.262f),CARD,"DB  G "+gc+"/18 · T "+tc+"/18",gc>0?GREEN:Color.GRAY,8.0f);
            autoBtn.set(w*.715f,h*.231f,w-m,h*.262f); pill(c,autoBtn,autoHole?Color.rgb(229,244,218):CARD,autoHole?"AUTO ON":"AUTO OFF",autoHole?GREEN:Color.GRAY,8.0f);

            courseRect.set(m,h*.276f,w-m,h*.566f); drawCourse(c,courseRect,par,officialM,green,ds,pulse);

            RectF strategy=new RectF(m,h*.580f,w-m,h*.631f); softShadow(c,strategy,20); box(c,strategy,CARD,20);
            text(c,"공략 포인트",m+14,h*.601f,8.7f,GREEN,true);
            String note=strategyNote();
            textFit(c,note,m+14,h*.620f,w-m-14,8.2f,INK,true);

            greenSave.set(m,h*.646f,w*.41f,h*.697f); teeSave.set(w*.43f,h*.646f,w*.69f,h*.697f); mapLaunch.set(w*.71f,h*.646f,w-m,h*.697f);
            pillButton(c,greenSave,green==null?CORAL:DEEP,confirmKind==1&&SystemClock.uptimeMillis()<confirmUntil?"한 번 더 눌러 저장":"GREEN 저장",Color.WHITE);
            pillButton(c,teeSave,getRef("t",hole)==null?Color.rgb(67,145,105):DEEP,confirmKind==2&&SystemClock.uptimeMillis()<confirmUntil?"다시 탭":"TEE 저장",Color.WHITE);
            pillButton(c,mapLaunch,CARD,"외부 지도",INK);

            drawPlayerTabs(c,h*.719f);
            RectF panel=new RectF(m,h*.761f,w-m,h*.862f); softShadow(c,panel,26); box(c,panel,CARD,26);
            int stroke=getStroke(player,hole,par), putt=getPutt(player,hole);
            text(c,"타수",m+18,h*.795f,10,Color.GRAY,true); text(c,""+stroke,w*.28f,h*.842f,30,INK,true,Paint.Align.CENTER);
            minus.set(m+10,h*.813f,m+52,h*.862f); plus.set(w*.38f,h*.813f,w*.47f,h*.862f);
            roundButton(c,minus,"−",SOFT,Color.GRAY); roundButton(c,plus,"+",Color.rgb(229,244,218),GREEN);
            text(c,"퍼트",w*.56f,h*.795f,10,Color.GRAY,true); text(c,""+putt,w*.70f,h*.842f,29,INK,true,Paint.Align.CENTER);
            pm.set(w*.53f,h*.813f,w*.61f,h*.862f); pp.set(w*.82f,h*.813f,w*.90f,h*.862f);
            roundButton(c,pm,"−",SOFT,Color.GRAY); roundButton(c,pp,"+",Color.rgb(226,245,250),SKY);
            drawTapBurst(c,h); nav(c);
        }

        private void drawCourse(Canvas c,RectF r,int par,int officialM,GeoRef green,Distances ds,float pulse){
            long now=SystemClock.uptimeMillis(); float phase=(now%2400)/2400f,slide=holeSlideOffset(now);
            c.save(); c.translate(slide,0);
            gradient(c,r,Color.rgb(232,248,214),Color.rgb(202,236,191),32);
            drawMountains(c,r); drawCloud(c,r.left+r.width()*.14f+phase*10,r.top+30,17); drawCloud(c,r.left+r.width()*.77f-phase*8,r.top+42,13);
            float cx=r.centerX(); Path f=new Path(); f.moveTo(cx-22,r.bottom-22);
            if(par==3) f.cubicTo(cx-18,r.centerY()+18,cx+8,r.centerY()-25,cx-6,r.top+55);
            else if(par==4) f.cubicTo(r.left+r.width()*.36f,r.bottom-r.height()*.25f,r.left+r.width()*.65f,r.top+r.height()*.44f,cx-8,r.top+54);
            else f.cubicTo(r.left+r.width()*.29f,r.bottom-r.height()*.17f,r.left+r.width()*.70f,r.top+r.height()*.54f,cx-8,r.top+54);
            f.lineTo(cx+48,r.top+63); f.cubicTo(r.left+r.width()*.71f,r.top+r.height()*.49f,r.left+r.width()*.51f,r.bottom-r.height()*.20f,cx+24,r.bottom-22); f.close();
            p.setColor(Color.rgb(90,180,87)); c.drawPath(f,p); stripes(c,f,r,phase);
            RectF water=new RectF(r.left+18,r.top+r.height()*.50f,r.left+r.width()*.37f,r.bottom-15); p.setColor(BLUE); c.drawOval(water,p); ripples(c,water,phase);
            p.setColor(YELLOW); c.drawOval(new RectF(cx+34,r.top+r.height()*.40f,cx+80,r.top+r.height()*.47f),p);
            float flagX=cx+12,flagY=r.top+54; p.setStrokeWidth(4);p.setColor(INK);c.drawLine(flagX,flagY,flagX,r.top+22,p);
            Path flag=new Path();flag.moveTo(flagX,r.top+22);flag.lineTo(flagX+28+6*pulse,r.top+29);flag.lineTo(flagX,r.top+38);flag.close();p.setColor(CORAL);c.drawPath(flag,p);
            p.setColor(Color.rgb(74,168,78)); c.drawOval(new RectF(cx-29,r.top+43,cx+50,r.top+79),p);

            float youX=cx,youY=r.bottom-30; dashRoute(c,youX,youY,flagX,flagY+8,phase);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.argb(90+(int)(80*pulse),24,111,68));c.drawCircle(youX,youY,16+10*pulse,p);p.setStyle(Paint.Style.FILL);
            p.setColor(Color.WHITE);c.drawCircle(youX,youY,10,p);p.setColor(GREEN);c.drawCircle(youX,youY,4,p);text(c,"YOU",youX,r.bottom-6,8,GREEN,true,Paint.Align.CENTER);

            if(hasTarget){
                p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(CORAL);c.drawCircle(targetX,targetY,12+4*pulse,p);p.setStyle(Paint.Style.FILL);
                p.setColor(CORAL);c.drawCircle(targetX,targetY,4,p);
                int est=estimateTargetM(r,officialM);
                speech(c,Math.max(r.left+8,Math.min(targetX-70,r.right-150)),Math.max(r.top+8,targetY-52),"공략 약 "+est+"m",CORAL);
            }

            String bubble = !gpsUsable() ? "GPS 품질 확인!" : (green==null ? "GREEN 좌표 필요" : (ds.center>=0 ? "CENTER "+ds.center+"m" : "거리 계산 중"));
            mascot(c,r.right-42,r.top+45,20,true); speech(c,r.right-184,r.top+14,bubble,green==null?CORAL:DEEP);
            if(previewMode) pill(c,new RectF(r.left+13,r.bottom-41,r.left+112,r.bottom-14),Color.argb(225,255,255,255),"PREVIEW GPS",CORAL,7.3f);
            c.restore();
        }

        private int estimateTargetM(RectF r,int officialM){
            float frac=(r.bottom-targetY)/Math.max(1f,r.height());
            frac=Math.max(0.05f,Math.min(.95f,frac));
            int base=distances(getRef("g",hole)).center;
            if(base<0) base=officialM;
            return Math.max(20,Math.round(base*frac));
        }

        private String strategyNote(){
            if(selected==0 && variant==0){
                if(hole==7) return "업힐 · 조금 큰 클럽으로 왼쪽 포트벙커 회피";
                if(hole==9) return "티샷은 좌측 쪽 · 2타부터 약간 오르막";
                if(hole==11) return "그린 앞 긴 벙커 · 오른쪽 공략이 안전";
                if(hole==13) return "조금 큰 클럽으로 높은 탄도 권장";
                if(hole==18) return "FW 벙커 방향 티샷 · 그린 좌우 가드벙커 주의";
            }
            if(selected==0 && variant==1){
                if(hole==13) return "명물홀 · 우도그렉 + 중간 크리크, 정확한 위치 선정";
                if(hole==15) return "그린 반주변을 감싼 연못 + 양쪽 큰 벙커 주의";
                return "정확도 우선 · 크리크/연못을 피해 다음 샷 각도 만들기";
            }
            if(selected==1 && variant==0){
                if(hole==15) return "명물 PAR5 · 그린 주변 연못, 무리한 직공략보다 위치 선정";
                return "PALMER · 긴 거리와 전략성, 다음 샷 각도 우선";
            }
            if(selected==1 && variant==1) return "KING · 비교적 짧은 코스, 티샷 정확도로 스코어 메이킹";
            if(selected==2){
                if(hole==3 || hole==13) return "드라이버 추천홀 · 넓은 FW지만 고원 바람 체크";
                if(hole==8 || hole==15) return "니어핀 추천홀 · 핀보다 안전한 그린 중앙 우선";
                return "3개의 소하천과 다수의 연못 · 물 해저드 방향 먼저 확인";
            }
            return "정규 거리 "+Math.round(currentYards()*.9144)+"m · 다음 샷 각도 우선";
        }

        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.05f;
            text(c,"스코어카드",m,h*.068f,29,INK,true); text(c,ko[selected]+" · "+variants[selected][variant],m,h*.10f,10,Color.GRAY,false);
            mascot(c,w*.88f,h*.078f,20,true); text(c,"4명 한 번에 · 홀/플레이어 상태 자동 저장",m,h*.132f,9.5f,Color.GRAY,false);
            float y=h*.18f; int[] totals={0,0,0,0};
            for(int i=1;i<=18;i++){
                int pa=parForHole(i); RectF row=new RectF(m,y-17,w-m,y+19); box(c,row,i==hole?Color.rgb(238,249,222):(i%2==0?Color.rgb(252,253,248):CARD),14);
                text(c,"H"+i,m+12,y+6,9,INK,true); text(c,"P"+pa,w*.25f,y+6,8,Color.GRAY,false,Paint.Align.CENTER);
                for(int pl=0;pl<4;pl++){int s=getStroke(pl,i,pa);totals[pl]+=s;int col=s>pa?CORAL:(s<pa?GREEN:INK);text(c,""+s,w*(.43f+pl*.14f),y+6,10,col,true,Paint.Align.CENTER);}
                y+=h*.031f;
            }
            RectF total=new RectF(m,h*.775f,w-m,h*.862f); gradient(c,total,DEEP,GREEN,25); sheen(c,total,25);
            text(c,"TOTAL",m+16,h*.818f,9,Color.WHITE,true);
            for(int pl=0;pl<4;pl++) text(c,"P"+(pl+1)+"  "+totals[pl],w*(.36f+pl*.16f),h*.826f,11,Color.WHITE,true,Paint.Align.CENTER);
            nav(c);
        }

        private void saveRef(int kind){
            if(location==null){showToast("GPS 위치를 먼저 잡아주세요");return;}
            if(!previewMode && location.getAccuracy()>12){showToast("GPS ±"+Math.round(location.getAccuracy())+"m · 12m 이하에서 저장");return;}
            long now=SystemClock.uptimeMillis();
            if(confirmKind!=kind || now>confirmUntil){confirmKind=kind;confirmUntil=now+3200;showToast(kind==1?"그린 CENTER에서 한 번 더 눌러 저장":"티잉구역에서 한 번 더 눌러 저장");invalidate();return;}
            String type=kind==1?"g":"t", k=refKey(type,hole);
            calPrefs.edit().putLong(k+"_lat",Double.doubleToRawLongBits(location.getLatitude())).putLong(k+"_lon",Double.doubleToRawLongBits(location.getLongitude())).apply();
            confirmKind=0;confirmUntil=0;showToast("H"+hole+" "+(kind==1?"GREEN CENTER":"TEE")+" 저장 완료");maybeAutoHole();invalidate();
        }

        private GeoRef getRef(String type,int h){
            String k=refKey(type,h);
            if(calPrefs.contains(k+"_lat")) return new GeoRef(Double.longBitsToDouble(calPrefs.getLong(k+"_lat",0)),Double.longBitsToDouble(calPrefs.getLong(k+"_lon",0)),false);
            if(previewMode && selected==0 && variant==0 && h==11){
                if(type.equals("g")) return new GeoRef(43.25982,143.22836,true);
                if(type.equals("t")) return new GeoRef(43.25720,143.22836,true);
            }
            return null;
        }

        private String refKey(String type,int h){return type+"_"+selected+"_"+variant+"_"+h;}
        private int savedCount(String type){int n=0;for(int h=1;h<=18;h++)if(getRef(type,h)!=null)n++;return n;}
        private Distances distances(GeoRef ref){
            if(ref==null || !gpsUsable()) return new Distances(-1,-1,-1);
            int center=Math.round(distance(location,ref.lat,ref.lon)); return new Distances(Math.max(0,center-12),center,center+12);
        }
        private float distance(Location l,double lat,double lon){float[] o=new float[1];Location.distanceBetween(l.getLatitude(),l.getLongitude(),lat,lon,o);return o[0];}

        private boolean gpsUsable(){return location!=null && (previewMode || location.getAccuracy()<=25) && fixAgeSec()<=15;}
        private int fixAgeSec(){if(location==null||lastFixElapsed==0)return 999;return (int)Math.min(999,(SystemClock.elapsedRealtime()-lastFixElapsed)/1000);}
        private String gpsLabel(){
            if(location==null)return "GPS 찾는 중…";
            if(fixAgeSec()>15)return "GPS 오래됨 "+fixAgeSec()+"s";
            return "GPS ±"+Math.round(location.getAccuracy())+"m";
        }
        private String gpsStatusShort(){
            if(location==null)return "GPS WAIT";
            if(fixAgeSec()>15)return "GPS STALE";
            float a=location.getAccuracy(); return a<=8?"GPS GOOD":(a<=15?"GPS FAIR":(a<=25?"GPS WEAK":"GPS LOCK"));
        }
        private int gpsColor(){
            if(location==null||fixAgeSec()>15)return CORAL; float a=location.getAccuracy();
            return a<=8?GREEN:(a<=15?AMBER:(a<=25?CORAL:Color.rgb(150,50,50)));
        }
        private int gpsBg(){
            int col=gpsColor();
            return col==GREEN?Color.rgb(229,244,218):(col==AMBER?Color.rgb(255,246,218):Color.rgb(255,238,229));
        }

        private void launchExternalMap(){
            if(selected<0)return;
            try{
                Uri u=Uri.parse("geo:"+courseLat[selected]+","+courseLon[selected]+"?q="+courseLat[selected]+","+courseLon[selected]+"("+Uri.encode(ko[selected])+")");
                ctx.startActivity(new Intent(Intent.ACTION_VIEW,u));
            }catch(Exception e){
                try{ctx.startActivity(new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS));}catch(Exception ignored){}
            }
        }

        private void drawPlayerTabs(Canvas c,float y){
            float w=getWidth(),m=w*.045f,gap=6,avail=w-2*m,ww=(avail-gap*3)/4;int[] dots={GREEN,SKY,CORAL,YELLOW};
            for(int i=0;i<4;i++){float l=m+i*(ww+gap);playerTabs[i].set(l,y,l+ww,y+34);box(c,playerTabs[i],player==i?GREEN:CARD,18);p.setColor(dots[i]);c.drawCircle(l+13,y+17,4,p);text(c,"P"+(i+1),l+ww/2+6,y+22,10,player==i?Color.WHITE:INK,true,Paint.Align.CENTER);}
        }
        private void nav(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;prev.set(m,h*.905f,w*.23f,h*.965f);mapTab.set(w*.27f,h*.905f,w*.49f,h*.965f);scoreTab.set(w*.53f,h*.905f,w*.75f,h*.965f);next.set(w*.79f,h*.905f,w-m,h*.965f);
            pillButton(c,prev,CARD,"‹ 이전",INK);pillButton(c,mapTab,screen==1?GREEN:CARD,"지도",screen==1?Color.WHITE:INK);pillButton(c,scoreTab,screen==2?GREEN:CARD,"스코어",screen==2?Color.WHITE:INK);pillButton(c,next,CARD,"다음 ›",INK);
        }

        private int currentPar(){return parForHole(hole);} private int parForHole(int h){return pars[selected][variant][h-1];} private int currentYards(){return yards[selected][variant][hole-1];}
        private int getStroke(int pl,int h,int par){return scorePrefs.getInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,par);}
        private int getPutt(int pl,int h){return scorePrefs.getInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,0);}
        private void setStroke(int pl,int h,int v){scorePrefs.edit().putInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply();}
        private void setPutt(int pl,int h,int v){scorePrefs.edit().putInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply();}
        private int nearestCourse(Location l){int best=-1;float bd=Float.MAX_VALUE;for(int i=0;i<3;i++){float d=(float)distanceToCourse(l,i);if(d<bd){bd=d;best=i;}}return best;}
        private double distanceToCourse(Location l,int i){if(l==null)return -1;float[] o=new float[1];Location.distanceBetween(l.getLatitude(),l.getLongitude(),courseLat[i],courseLon[i],o);return o[0];}
        private int clamp(int v,int a,int b){return Math.max(a,Math.min(b,v));}

        private void showToast(String s){toastText=s;toastAt=SystemClock.uptimeMillis();}
        private void drawToast(Canvas c){
            if(toastAt==0)return;long age=SystemClock.uptimeMillis()-toastAt;if(age>1800)return;float w=getWidth(),h=getHeight();int a=age<1400?245:(int)(245*(1-(age-1400)/400f));
            RectF r=new RectF(w*.18f,h*.49f,w*.82f,h*.545f);box(c,r,Color.argb(Math.max(0,a),20,70,45),24);text(c,toastText,w/2,r.centerY()+5,9.5f,Color.WHITE,true,Paint.Align.CENTER);
        }
        private void drawTapBurst(Canvas c,float h){
            long age=SystemClock.uptimeMillis()-lastTap;if(age>600||lastDelta==0)return;float t=age/600f;float x=lastDelta>0?getWidth()*.43f:getWidth()*.12f,y=h*.82f-t*45;int a=(int)(255*(1-t));
            p.setColor(Color.argb(Math.min(220,a),255,255,255));c.drawCircle(x,y,18,p);text(c,lastDelta>0?"+1":"−1",x,y+5,10,Color.argb(a,24,111,68),true,Paint.Align.CENTER);
        }
        private float holeSlideOffset(long now){if(lastHoleChange==0)return 0;float t=(now-lastHoleChange)/320f;if(t>=1)return 0;float e=1-(1-t)*(1-t)*(1-t);return holeDirection*getWidth()*(1-e)*.34f;}

        private void drawMountains(Canvas c,RectF r){Path a=new Path();a.moveTo(r.left,r.top+84);a.lineTo(r.left+72,r.top+28);a.lineTo(r.left+138,r.top+84);a.close();p.setColor(Color.argb(70,100,150,112));c.drawPath(a,p);Path b=new Path();b.moveTo(r.left+88,r.top+84);b.lineTo(r.left+168,r.top+17);b.lineTo(r.left+246,r.top+84);b.close();p.setColor(Color.argb(58,70,130,95));c.drawPath(b,p);}
        private void drawCloud(Canvas c,float x,float y,float s){p.setColor(Color.argb(210,255,255,255));c.drawCircle(x,y,s*.45f,p);c.drawCircle(x+s*.4f,y-s*.1f,s*.58f,p);c.drawCircle(x+s*.86f,y,s*.42f,p);c.drawRoundRect(new RectF(x-s*.1f,y,x+s*1.15f,y+s*.38f),s*.18f,s*.18f,p);}
        private void stripes(Canvas c,Path f,RectF r,float phase){c.save();c.clipPath(f);p.setStrokeWidth(22);for(int i=-8;i<20;i++){float x=r.left+i*44+phase*44;p.setColor(i%2==0?Color.argb(18,255,255,255):Color.argb(11,20,90,40));c.drawLine(x,r.bottom,x+r.height()*.55f,r.top,p);}c.restore();}
        private void ripples(Canvas c,RectF water,float phase){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);p.setColor(Color.argb(100,255,255,255));for(int i=0;i<3;i++){float g=(phase+i*.28f)%1f,rw=water.width()*(.12f+.28f*g),rh=water.height()*(.04f+.07f*g),cy=water.centerY()+i*15;c.drawOval(new RectF(water.centerX()-rw,cy-rh,water.centerX()+rw,cy+rh),p);}p.setStyle(Paint.Style.FILL);}
        private void dashRoute(Canvas c,float x1,float y1,float x2,float y2,float phase){float dx=x2-x1,dy=y2-y1,len=(float)Math.sqrt(dx*dx+dy*dy);if(len<1)return;float ux=dx/len,uy=dy/len,start=(phase*24)%24;p.setStrokeWidth(2);p.setColor(Color.argb(170,255,255,255));for(float d=start;d<len;d+=24){float e=Math.min(d+11,len);c.drawLine(x1+ux*d,y1+uy*d,x1+ux*e,y1+uy*e,p);}}
        private void mascot(Canvas c,float x,float y,float r,boolean wave){float bob=(float)Math.sin(SystemClock.uptimeMillis()/300.0)*2;y+=bob;p.setColor(Color.argb(24,20,60,30));c.drawOval(new RectF(x-r*.8f,y+r*.78f,x+r*.8f,y+r),p);p.setColor(Color.WHITE);c.drawCircle(x,y,r,p);p.setColor(INK);c.drawCircle(x-r*.25f,y-r*.05f,r*.075f,p);c.drawCircle(x+r*.25f,y-r*.05f,r*.075f,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);c.drawArc(new RectF(x-r*.3f,y-r*.02f,x+r*.3f,y+r*.45f),15,150,false,p);p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawRoundRect(new RectF(x-r*.65f,y-r*.82f,x+r*.58f,y-r*.48f),r*.16f,r*.16f,p);if(wave){p.setStrokeWidth(Math.max(3,r*.12f));p.setColor(INK);c.drawLine(x+r*.68f,y,x+r*1.15f,y-r*.42f+(float)Math.sin(SystemClock.uptimeMillis()/160.0)*r*.18f,p);}}
        private void speech(Canvas c,float x,float y,String s,int col){RectF b=new RectF(x,y,x+145,y+36);softShadow(c,b,18);box(c,b,Color.argb(242,255,255,255),18);text(c,s,b.centerX(),b.centerY()+4,8.4f,col,true,Paint.Align.CENTER);}
        private void metric(Canvas c,String lab,String val,float x,float y){text(c,lab,x,y,9,Color.rgb(212,237,219),true,Paint.Align.CENTER);text(c,val,x,y+getHeight()*.040f,19,Color.WHITE,true,Paint.Align.CENTER);}
        private void pill(Canvas c,RectF r,int bg,String s,int fg,float z){box(c,r,bg,r.height()/2);text(c,s,r.centerX(),r.centerY()+4,z,fg,true,Paint.Align.CENTER);}
        private void pillButton(Canvas c,RectF r,int bg,String s,int fg){softShadow(c,r,20);box(c,r,bg,20);text(c,s,r.centerX(),r.centerY()+5,9.8f,fg,true,Paint.Align.CENTER);}
        private void roundButton(Canvas c,RectF r,String s,int bg,int fg){box(c,r,bg,16);text(c,s,r.centerX(),r.centerY()+7,20,fg,true,Paint.Align.CENTER);}
        private void softShadow(Canvas c,RectF r,float rad){p.setColor(Color.argb(18,20,60,30));c.drawRoundRect(new RectF(r.left,r.top+4,r.right,r.bottom+4),rad,rad,p);}
        private void gradient(Canvas c,RectF r,int a,int b,float rad){Shader old=p.getShader();p.setShader(new LinearGradient(r.left,r.top,r.right,r.bottom,a,b,Shader.TileMode.CLAMP));c.drawRoundRect(r,rad,rad,p);p.setShader(old);}
        private void sheen(Canvas c,RectF r,float rad){float phase=(SystemClock.uptimeMillis()%3200)/3200f,x=r.left-r.width()*.35f+phase*r.width()*1.7f;Path clip=new Path();clip.addRoundRect(r,rad,rad,Path.Direction.CW);c.save();c.clipPath(clip);p.setColor(Color.argb(18,255,255,255));Path s=new Path();s.moveTo(x-r.width()*.12f,r.bottom);s.lineTo(x+r.width()*.06f,r.top);s.lineTo(x+r.width()*.22f,r.top);s.lineTo(x+r.width()*.04f,r.bottom);s.close();c.drawPath(s,p);c.restore();}
        private void box(Canvas c,RectF r,int col,float rad){p.setShader(null);p.setStyle(Paint.Style.FILL);p.setColor(col);c.drawRoundRect(r,rad,rad,p);}
        private void text(Canvas c,String s,float x,float y,float z,int col,boolean bold){text(c,s,x,y,z,col,bold,Paint.Align.LEFT);}
        private void text(Canvas c,String s,float x,float y,float z,int col,boolean bold,Paint.Align a){p.setShader(null);p.setStyle(Paint.Style.FILL);p.setColor(col);p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);p.setTypeface(Typeface.create("sans-serif-rounded",bold?Typeface.BOLD:Typeface.NORMAL));p.setTextAlign(a);c.drawText(s,x,y,p);}
        private void textFit(Canvas c,String s,float x,float y,float right,float z,int col,boolean bold){p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);while(p.measureText(s)>right-x && z>6.5f){z-=.25f;p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);}text(c,s,x,y,z,col,bold);}

        @Override public boolean onTouchEvent(MotionEvent e){
            if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();
            if(screen==0){
                for(int i=0;i<3;i++)if(cards[i].contains(x,y)){selected=i;if(i==2)variant=0;saveState();invalidate();return true;}
                if(varA.contains(x,y)){variant=0;saveState();invalidate();return true;}
                if(varB.contains(x,y)){variant=selected==2?0:1;saveState();invalidate();return true;}
                if(selected>=0&&start.contains(x,y)){screen=1;saveState();invalidate();return true;}
                return true;
            }
            if(screen==1 && courseRect.contains(x,y)){targetX=x;targetY=y;hasTarget=true;showToast("공략 지점 선택 · 도식 추정거리");invalidate();return true;}
            if(greenSave.contains(x,y)){saveRef(1);return true;}
            if(teeSave.contains(x,y)){saveRef(2);return true;}
            if(mapLaunch.contains(x,y)){launchExternalMap();return true;}
            if(autoBtn.contains(x,y)){autoHole=!autoHole;saveState();showToast(autoHole?"홀 자동 감지 ON":"홀 자동 감지 OFF");invalidate();return true;}
            for(int i=0;i<4;i++)if(playerTabs[i].contains(x,y)){player=i;saveState();invalidate();return true;}
            int par=currentPar();
            if(minus.contains(x,y)){setStroke(player,hole,Math.max(1,getStroke(player,hole,par)-1));lastTap=SystemClock.uptimeMillis();lastDelta=-1;}
            else if(plus.contains(x,y)){setStroke(player,hole,getStroke(player,hole,par)+1);lastTap=SystemClock.uptimeMillis();lastDelta=1;}
            else if(pm.contains(x,y)){setPutt(player,hole,Math.max(0,getPutt(player,hole)-1));lastTap=SystemClock.uptimeMillis();lastDelta=-1;}
            else if(pp.contains(x,y)){setPutt(player,hole,getPutt(player,hole)+1);lastTap=SystemClock.uptimeMillis();lastDelta=1;}
            else if(prev.contains(x,y)){if(hole>1){hole--;holeDirection=-1;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;saveState();}}
            else if(next.contains(x,y)){if(hole<18){hole++;holeDirection=1;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;saveState();}}
            else if(mapTab.contains(x,y)){screen=1;}
            else if(scoreTab.contains(x,y)){screen=2;}
            invalidate();return true;
        }

        static final class GeoRef{final double lat,lon;final boolean demo;GeoRef(double a,double o,boolean d){lat=a;lon=o;demo=d;}}
        static final class Distances{final int front,center,back;Distances(int f,int c,int b){front=f;center=c;back=b;}}
    }
}
