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

import java.util.Locale;

public class MainActivity extends Activity implements LocationListener {
    private static final int REQ = 1001;
    private LocationManager lm;
    private GolfView view;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        view = new GolfView(this);
        setContentView(view);
        lm = (LocationManager) getSystemService(LOCATION_SERVICE);
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, REQ);
        } else startGps();
    }

    private void startGps() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) return;
        try { lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000, 1.0f, this); } catch (Exception ignored) {}
    }

    @Override public void onLocationChanged(Location l) { view.setLocation(l); }
    @Override protected void onPause() { super.onPause(); try { lm.removeUpdates(this); } catch (Exception ignored) {} }
    @Override protected void onResume() { super.onResume(); startGps(); }
    @Override public void onRequestPermissionsResult(int r, String[] p, int[] g) {
        super.onRequestPermissionsResult(r,p,g);
        if (r==REQ && g.length>0 && g[0]==PackageManager.PERMISSION_GRANTED) startGps();
    }

    static final class GolfView extends View {
        private final Context ctx;
        private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final SharedPreferences prefs;
        private final String[] jp = {"上士幌ゴルフ場","富良野ゴルフコース","サホロカントリークラブ"};
        private final String[] ko = {"가미시호로 골프장","후라노 골프코스","사호로 컨트리클럽"};
        private final String[][] variantNames = {{"CHAMPIONS","MASTERS"},{"PALMER","KING"},{"OUT / IN","OUT / IN"}};
        private final double[] courseLat = {43.2570513, 43.3351203, 43.15515899658203};
        private final double[] courseLon = {143.2283621, 142.4817967, 142.80709838867188};

        private final int[][][] yards = {
                {
                        {523,413,170,366,361,351,135,358,481,415,183,395,167,370,509,426,399,516},
                        {454,516,416,155,331,369,373,150,367,393,351,132,455,328,167,469,356,370}
                },
                {
                        {470,410,171,411,545,426,400,174,379,395,132,420,342,414,527,182,388,525},
                        {313,168,401,523,386,335,175,359,489,350,312,535,346,151,360,170,422,506}
                },
                {
                        {395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493},
                        {395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493}
                }
        };
        private final int[][][] pars = {
                {
                        {5,4,3,4,4,4,3,4,5,4,3,4,3,4,5,4,4,5},
                        {5,5,4,3,4,4,4,3,4,4,4,3,5,4,3,5,4,5}
                },
                {
                        {5,4,3,4,5,4,4,3,4,4,3,4,4,4,5,3,4,5},
                        {4,3,4,5,4,4,3,4,5,4,4,5,4,3,4,3,4,5}
                },
                {
                        {4,5,4,3,4,5,4,3,4,4,3,4,5,4,3,4,4,5},
                        {4,5,4,3,4,5,4,3,4,4,3,4,5,4,3,4,4,5}
                }
        };

        private int selected=-1, variant=0, screen=0, hole=1, player=0;
        private Location location;
        private boolean hasTarget=false;
        private float targetX, targetY;
        private long lastScoreTap=0;

        private final RectF[] cards={new RectF(),new RectF(),new RectF()};
        private final RectF start=new RectF(), varA=new RectF(), varB=new RectF();
        private final RectF minus=new RectF(), plus=new RectF(), pm=new RectF(), pp=new RectF();
        private final RectF prev=new RectF(), next=new RectF(), scoreTab=new RectF(), mapTab=new RectF();
        private final RectF mapLaunch=new RectF(), gpsSettings=new RectF(), courseRect=new RectF();
        private final RectF[] playerTabs={new RectF(),new RectF(),new RectF(),new RectF()};

        private final int BG=Color.rgb(249,250,240), INK=Color.rgb(35,55,41), GREEN=Color.rgb(25,111,69), DEEP=Color.rgb(10,82,54),
                MINT=Color.rgb(218,241,202), SKY=Color.rgb(99,196,230), BLUE=Color.rgb(75,167,210), CORAL=Color.rgb(255,126,93),
                YELLOW=Color.rgb(255,208,64), CREAM=Color.rgb(255,251,237), CARD=Color.WHITE, SOFT=Color.rgb(241,245,235);

        GolfView(Context c){
            super(c);
            ctx=c;
            prefs=c.getSharedPreferences("score_v05",MODE_PRIVATE);
            p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL));
            setKeepScreenOn(true);
        }

        void setLocation(Location l){
            location=l;
            if(selected<0){
                int near=nearestCourse(l);
                if(near>=0 && distanceToCourse(l,near)<8000) selected=near;
            }
            invalidate();
        }

        @Override protected void onDraw(Canvas c){
            super.onDraw(c);
            c.drawColor(BG);
            if(screen==0) home(c); else if(screen==1) round(c); else score(c);
            postInvalidateDelayed(screen==1?60:120);
        }

        private void home(Canvas c){
            float w=getWidth(), h=getHeight(), m=w*.055f;
            float bob=(float)Math.sin(SystemClock.uptimeMillis()/330.0)*5;
            text(c,"北海道ゴルフ",m,h*.067f,27,INK,true);
            text(c,"GPSキャディ",m,h*.112f,38,GREEN,true);
            pill(c,new RectF(m,h*.135f,m+w*.48f,h*.178f),Color.rgb(229,244,218),"8/24~26 · HOKKAIDO TRIP",GREEN,10);
            mascot(c,w*.83f,h*.10f+bob,24,true);
            speech(c,w*.62f,h*.16f,"오늘도 굿샷!",GREEN);

            text(c,"오늘 어디서 칠까요?",m,h*.225f,18,INK,true);
            text(c,"GPS · 코스 · 4인 스코어 · 거리 단위 m",m,h*.254f,10,Color.GRAY,false);

            float top=h*.29f, ch=h*.115f, gap=h*.015f;
            int[] accents={Color.rgb(172,221,92),YELLOW,SKY};
            String[] tags={"DAY 1","DAY 2","DAY 3"};
            for(int i=0;i<3;i++){
                float y=top+i*(ch+gap);
                cards[i].set(m,y,w-m,y+ch);
                softShadow(c,cards[i],26);
                box(c,cards[i],selected==i?Color.rgb(238,249,222):CARD,26);
                p.setColor(accents[i]); c.drawCircle(m+28,y+31,11,p);
                text(c,tags[i],m+50,y+35,9,GREEN,true);
                text(c,jp[i],m+22,y+70,18,INK,true);
                text(c,ko[i],m+22,y+94,10,Color.GRAY,false);
                if(location!=null){
                    int dm=(int)Math.round(distanceToCourse(location,i));
                    String ds=dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km";
                    pill(c,new RectF(w-m-108,y+18,w-m-14,y+49),SOFT,ds,selected==i?GREEN:Color.GRAY,9);
                }
                if(selected==i){ p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(3); p.setColor(GREEN); c.drawRoundRect(cards[i],26,26,p); p.setStyle(Paint.Style.FILL); }
            }

            float vy=h*.70f;
            text(c,"코스 선택",m,vy,10,Color.GRAY,true);
            varA.set(m,vy+12,w*.48f,vy+58); varB.set(w*.52f,vy+12,w-m,vy+58);
            pillButton(c,varA,variant==0?GREEN:CARD,selected<0?"A COURSE":variantNames[selected][0],variant==0?Color.WHITE:INK);
            pillButton(c,varB,variant==1?GREEN:CARD,selected<0?"B COURSE":variantNames[selected][1],variant==1?Color.WHITE:INK);

            start.set(m,h*.805f,w-m,h*.882f);
            gradientBox(c,start,selected>=0?DEEP:Color.LTGRAY,selected>=0?GREEN:Color.GRAY,36);
            text(c,selected>=0?"라운드 시작  →":"골프장을 먼저 선택해주세요",w/2,h*.854f,15,selected>=0?Color.WHITE:Color.DKGRAY,true,Paint.Align.CENTER);
            text(c,"REGULAR TEE · 휴대폰 GPS · 오프라인 스코어",w/2,h*.925f,9,Color.GRAY,false,Paint.Align.CENTER);
        }

        private void round(Canvas c){
            float w=getWidth(), h=getHeight(), m=w*.045f;
            int par=currentPar();
            int officialM=(int)Math.round(currentYards()*0.9144);
            float t=(float)(SystemClock.uptimeMillis()%2000)/2000f;
            float pulse=(float)(0.5+0.5*Math.sin(t*Math.PI*2));

            text(c,ko[Math.max(0,selected)]+" · "+variantNames[Math.max(0,selected)][variant],m,h*.045f,11,Color.GRAY,true);
            text(c,"H"+hole,m,h*.098f,38,INK,true);
            RectF parPill=new RectF(m+76,h*.065f,m+145,h*.105f);
            pill(c,parPill,Color.rgb(229,244,218),"PAR "+par,GREEN,11);

            RectF gpsPill=new RectF(w-m-132,h*.024f,w-m,h*.064f);
            if(location==null){
                int alpha=120+(int)(100*pulse);
                pill(c,gpsPill,Color.argb(alpha,255,238,229),"GPS 찾는 중…",CORAL,10);
            } else {
                pill(c,gpsPill,Color.rgb(229,244,218),"GPS ±"+Math.round(location.getAccuracy())+"m",GREEN,10);
            }

            RectF hud=new RectF(m,h*.125f,w-m,h*.23f);
            gradientBox(c,hud,DEEP,GREEN,28);
            metric(c,"REGULAR",officialM+"m",w*.21f,h*.16f);
            metric(c,"PAR",""+par,w*.50f,h*.16f);
            int ccDist=location==null?-1:(int)Math.round(distanceToCourse(location,selected));
            metric(c,"코스센터",ccDist<0?"--":(ccDist>9999?String.format(Locale.US,"%.1fkm",ccDist/1000f):ccDist+"m"),w*.79f,h*.16f);

            courseRect.set(m,h*.25f,w-m,h*.61f);
            drawAnimatedCourse(c,courseRect,par,officialM);
            text(c,"홀맵 V0.5 · 애니메이션 UI · 실제 그린 좌표는 V0.6에서 연결",w/2,h*.635f,9,Color.GRAY,false,Paint.Align.CENTER);

            mapLaunch.set(m,h*.655f,w*.61f,h*.708f); gpsSettings.set(w*.64f,h*.655f,w-m,h*.708f);
            pillButton(c,mapLaunch,DEEP,"지도 앱에서 코스 열기 ↗",Color.WHITE);
            pillButton(c,gpsSettings,CARD,"GPS 설정",INK);

            playerTabs(c,h*.735f);
            RectF panel=new RectF(m,h*.775f,w-m,h*.875f);
            softShadow(c,panel,26); box(c,panel,CARD,26);
            int stroke=getStroke(player,hole,par), putt=getPutt(player,hole);
            float pop=1f;
            long since=SystemClock.uptimeMillis()-lastScoreTap;
            if(since<220) pop=1f+(float)Math.sin((220-since)/220f*Math.PI)*0.18f;

            text(c,"타수",m+18,h*.807f,10,Color.GRAY,true);
            text(c,""+stroke,w*.28f,h*.852f,30*pop,INK,true,Paint.Align.CENTER);
            minus.set(m+10,h*.815f,m+52,h*.865f); plus.set(w*.38f,h*.815f,w*.47f,h*.865f);
            roundButton(c,minus,"−",Color.rgb(238,243,232),Color.GRAY); roundButton(c,plus,"+",Color.rgb(229,244,218),GREEN);
            text(c,"퍼트",w*.56f,h*.807f,10,Color.GRAY,true);
            text(c,""+putt,w*.70f,h*.852f,28*pop,INK,true,Paint.Align.CENTER);
            pm.set(w*.53f,h*.815f,w*.61f,h*.865f); pp.set(w*.82f,h*.815f,w*.90f,h*.865f);
            roundButton(c,pm,"−",Color.rgb(238,243,232),Color.GRAY); roundButton(c,pp,"+",Color.rgb(226,245,250),SKY);
            nav(c);
        }

        private void drawAnimatedCourse(Canvas c,RectF r,int par,int officialM){
            long now=SystemClock.uptimeMillis();
            float phase=(now%2400)/2400f;
            float pulse=(float)(0.5+0.5*Math.sin(phase*Math.PI*2));

            gradientBox(c,r,Color.rgb(230,247,210),Color.rgb(205,236,191),32);
            drawMountains(c,r);
            drawCloud(c,r.left+r.width()*.18f,r.top+32+(float)Math.sin(now/700.0)*3,20);
            drawCloud(c,r.left+r.width()*.78f,r.top+45+(float)Math.sin(now/850.0)*3,15);

            p.setColor(Color.rgb(91,181,88));
            Path f=new Path();
            float cx=r.centerX();
            f.moveTo(cx-20,r.bottom-22);
            if(par==3){
                f.cubicTo(cx-10,r.centerY()+45,cx+12,r.centerY()-35,cx-8,r.top+55);
            } else if(par==4){
                f.cubicTo(r.left+r.width()*.40f,r.bottom-r.height()*.28f,r.left+r.width()*.62f,r.top+r.height()*.48f,cx-8,r.top+55);
            } else {
                f.cubicTo(r.left+r.width()*.32f,r.bottom-r.height()*.20f,r.left+r.width()*.69f,r.top+r.height()*.54f,cx-8,r.top+55);
            }
            f.lineTo(cx+48,r.top+62);
            f.cubicTo(r.left+r.width()*.72f,r.top+r.height()*.50f,r.left+r.width()*.50f,r.bottom-r.height()*.22f,cx+22,r.bottom-22);
            f.close(); c.drawPath(f,p);

            p.setColor(BLUE); c.drawOval(new RectF(r.left+15,r.top+r.height()*.48f,r.left+r.width()*.39f,r.bottom-16),p);
            p.setColor(Color.rgb(114,190,240)); c.drawOval(new RectF(r.left+30,r.top+r.height()*.54f,r.left+r.width()*.35f,r.bottom-30),p);
            p.setColor(YELLOW); c.drawOval(new RectF(cx+38,r.top+r.height()*.43f,cx+82,r.top+r.height()*.50f),p);

            float flagX=cx+12, flagY=r.top+56;
            p.setStrokeWidth(4); p.setColor(INK); c.drawLine(flagX,flagY,flagX,r.top+24,p);
            Path flag=new Path(); flag.moveTo(flagX,r.top+24); flag.lineTo(flagX+27+6*pulse,r.top+31); flag.lineTo(flagX,r.top+39); flag.close(); p.setColor(CORAL); c.drawPath(flag,p);
            p.setColor(Color.rgb(75,168,78)); c.drawOval(new RectF(cx-28,r.top+43,cx+50,r.top+83),p);

            float youX=cx, youY=r.bottom-32;
            drawDashRoute(c,youX,youY,flagX,flagY+10,phase);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(3); p.setColor(Color.argb(80+(int)(90*pulse),25,111,69)); c.drawCircle(youX,youY,15+10*pulse,p); p.setStyle(Paint.Style.FILL);
            p.setColor(Color.WHITE); c.drawCircle(youX,youY,10,p); p.setColor(GREEN); c.drawCircle(youX,youY,4,p);
            text(c,"YOU",youX,r.bottom-7,8,GREEN,true,Paint.Align.CENTER);

            if(hasTarget && r.contains(targetX,targetY)){
                p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(3); p.setColor(CORAL); c.drawCircle(targetX,targetY,12+8*pulse,p); p.setStyle(Paint.Style.FILL);
                p.setColor(CORAL); c.drawCircle(targetX,targetY,7,p);
                int mapEstimate=(int)Math.max(0,Math.min(officialM,officialM*((youY-targetY)/(youY-(flagY+10)))));
                RectF bubble=new RectF(targetX-60,targetY-49,targetX+60,targetY-18);
                box(c,bubble,Color.argb(235,255,255,255),16);
                text(c,"맵 추정 "+mapEstimate+"m",bubble.centerX(),bubble.centerY()+4,9,CORAL,true,Paint.Align.CENTER);
            }

            mascot(c,r.right-28,r.top+28,11,false);
            if(pulse>.58f) speech(c,r.right-156,r.top+22,"핀까지 가자!",DEEP);
        }

        private void drawMountains(Canvas c,RectF r){
            Path m1=new Path(); m1.moveTo(r.left,r.top+95); m1.lineTo(r.left+80,r.top+30); m1.lineTo(r.left+145,r.top+95); m1.close(); p.setColor(Color.argb(85,110,155,120)); c.drawPath(m1,p);
            Path m2=new Path(); m2.moveTo(r.left+100,r.top+95); m2.lineTo(r.left+185,r.top+18); m2.lineTo(r.left+270,r.top+95); m2.close(); p.setColor(Color.argb(70,80,135,100)); c.drawPath(m2,p);
        }

        private void drawCloud(Canvas c,float x,float y,float s){
            p.setColor(Color.argb(210,255,255,255)); c.drawCircle(x,y,s*.45f,p); c.drawCircle(x+s*.40f,y-s*.10f,s*.58f,p); c.drawCircle(x+s*.86f,y,s*.42f,p); c.drawRoundRect(new RectF(x-s*.10f,y,x+s*1.15f,y+s*.38f),s*.18f,s*.18f,p);
        }

        private void drawDashRoute(Canvas c,float x1,float y1,float x2,float y2,float phase){
            float dx=x2-x1, dy=y2-y1, len=(float)Math.sqrt(dx*dx+dy*dy); if(len<1)return;
            float ux=dx/len, uy=dy/len; float start=(phase*24)%24;
            p.setStrokeWidth(2); p.setColor(Color.argb(170,255,255,255));
            for(float d=start;d<len;d+=24){ float e=Math.min(d+11,len); c.drawLine(x1+ux*d,y1+uy*d,x1+ux*e,y1+uy*e,p); }
        }

        private void playerTabs(Canvas c,float y){
            float w=getWidth(),m=w*.045f,gap=6,avail=w-2*m,ww=(avail-gap*3)/4;
            int[] dots={GREEN,SKY,CORAL,YELLOW};
            for(int i=0;i<4;i++){
                float l=m+i*(ww+gap); playerTabs[i].set(l,y,l+ww,y+34);
                box(c,playerTabs[i],player==i?GREEN:CARD,18);
                p.setColor(dots[i]); c.drawCircle(l+13,y+17,4,p);
                text(c,"P"+(i+1),l+ww/2+6,y+22,10,player==i?Color.WHITE:INK,true,Paint.Align.CENTER);
            }
        }

        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.05f;
            text(c,"스코어카드",m,h*.067f,29,INK,true);
            text(c,ko[Math.max(0,selected)]+" · "+variantNames[Math.max(0,selected)][variant],m,h*.098f,10,Color.GRAY,false);
            mascot(c,w*.88f,h*.075f,16,true);
            text(c,"4명 한 번에. 계산은 제가 할게요 :) ",m,h*.13f,10,Color.GRAY,false);
            float y=h*.18f; int[] totals={0,0,0,0};
            for(int i=1;i<=18;i++){
                int pa=parForHole(i); RectF row=new RectF(m,y-17,w-m,y+19);
                box(c,row,i==hole?Color.rgb(238,249,222):(i%2==0?Color.rgb(252,253,248):CARD),14);
                text(c,"H"+i,m+12,y+6,9,INK,true); text(c,"P"+pa,w*.25f,y+6,8,Color.GRAY,false,Paint.Align.CENTER);
                for(int pl=0;pl<4;pl++){
                    int s=getStroke(pl,i,pa); totals[pl]+=s; int col=s>pa?CORAL:(s<pa?GREEN:INK);
                    text(c,""+s,w*(.43f+pl*.14f),y+6,10,col,true,Paint.Align.CENTER);
                }
                y+=h*.031f;
            }
            RectF total=new RectF(m,h*.775f,w-m,h*.862f); gradientBox(c,total,DEEP,GREEN,25);
            text(c,"TOTAL",m+16,h*.818f,9,Color.WHITE,true);
            for(int pl=0;pl<4;pl++) text(c,"P"+(pl+1)+"  "+totals[pl],w*(.36f+pl*.16f),h*.826f,11,Color.WHITE,true,Paint.Align.CENTER);
            nav(c);
        }

        private void nav(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;
            prev.set(m,h*.905f,w*.23f,h*.965f); mapTab.set(w*.27f,h*.905f,w*.49f,h*.965f); scoreTab.set(w*.53f,h*.905f,w*.75f,h*.965f); next.set(w*.79f,h*.905f,w-m,h*.965f);
            pillButton(c,prev,CARD,"‹ 이전",INK);
            pillButton(c,mapTab,screen==1?GREEN:CARD,"지도",screen==1?Color.WHITE:INK);
            pillButton(c,scoreTab,screen==2?GREEN:CARD,"스코어",screen==2?Color.WHITE:INK);
            pillButton(c,next,CARD,"다음 ›",INK);
        }

        private void mascot(Canvas c,float x,float y,float r,boolean wave){
            float bob=(float)Math.sin(SystemClock.uptimeMillis()/300.0)*2;
            y+=bob;
            p.setColor(Color.WHITE); c.drawCircle(x,y,r,p);
            p.setColor(Color.rgb(210,210,198)); c.drawCircle(x-r*.32f,y-r*.22f,r*.10f,p); c.drawCircle(x+r*.23f,y+r*.22f,r*.08f,p);
            p.setColor(INK); c.drawCircle(x-r*.25f,y-r*.05f,r*.075f,p); c.drawCircle(x+r*.25f,y-r*.05f,r*.075f,p);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(2); p.setColor(INK); c.drawArc(new RectF(x-r*.30f,y-r*.02f,x+r*.30f,y+r*.45f),15,150,false,p); p.setStyle(Paint.Style.FILL);
            p.setColor(GREEN); c.drawRoundRect(new RectF(x-r*.65f,y-r*.82f,x+r*.58f,y-r*.48f),r*.16f,r*.16f,p); c.drawCircle(x-r*.28f,y-r*.82f,r*.28f,p);
            if(wave){ p.setStrokeWidth(4); p.setColor(INK); c.drawLine(x+r*.7f,y,x+r*1.15f,y-r*.45f,p); }
        }

        private void speech(Canvas c,float x,float y,String s,int color){
            RectF b=new RectF(x,y,x+112,y+34); box(c,b,Color.argb(238,255,255,255),17); text(c,s,b.centerX(),b.centerY()+4,9,color,true,Paint.Align.CENTER);
        }

        private int currentPar(){ return parForHole(hole); }
        private int parForHole(int h){ return pars[Math.max(0,selected)][variant][h-1]; }
        private int currentYards(){ return yards[Math.max(0,selected)][variant][hole-1]; }
        private int getStroke(int pl,int h,int par){ return prefs.getInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,par); }
        private int getPutt(int pl,int h){ return prefs.getInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,0); }
        private void setStroke(int pl,int h,int v){ prefs.edit().putInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply(); }
        private void setPutt(int pl,int h,int v){ prefs.edit().putInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply(); }

        private int nearestCourse(Location l){
            int best=-1; float bd=Float.MAX_VALUE;
            for(int i=0;i<3;i++){ float d=(float)distanceToCourse(l,i); if(d<bd){bd=d;best=i;} }
            return best;
        }
        private double distanceToCourse(Location l,int idx){
            if(l==null||idx<0) return -1;
            float[] out=new float[1]; Location.distanceBetween(l.getLatitude(),l.getLongitude(),courseLat[idx],courseLon[idx],out); return out[0];
        }

        private void launchMap(){
            if(selected<0)return;
            String label=Uri.encode(jp[selected]);
            Uri uri=Uri.parse("geo:"+courseLat[selected]+","+courseLon[selected]+"?q="+courseLat[selected]+","+courseLon[selected]+"("+label+")");
            try { ctx.startActivity(new Intent(Intent.ACTION_VIEW,uri)); }
            catch(Exception e){ ctx.startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse("https://www.google.com/maps/search/?api=1&query="+courseLat[selected]+","+courseLon[selected]))); }
        }
        private void launchGpsSettings(){ try { ctx.startActivity(new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS)); } catch(Exception ignored){} }

        private void metric(Canvas c,String label,String value,float x,float y){
            text(c,label,x,y,9,Color.rgb(212,237,219),true,Paint.Align.CENTER);
            text(c,value,x,y+getHeight()*.040f,19,Color.WHITE,true,Paint.Align.CENTER);
        }
        private void pill(Canvas c,RectF r,int bg,String s,int fg,float size){ box(c,r,bg,r.height()/2); text(c,s,r.centerX(),r.centerY()+4,size,fg,true,Paint.Align.CENTER); }
        private void pillButton(Canvas c,RectF r,int bg,String s,int fg){ softShadow(c,r,20); box(c,r,bg,20); text(c,s,r.centerX(),r.centerY()+5,10.5f,fg,true,Paint.Align.CENTER); }
        private void roundButton(Canvas c,RectF r,String s,int bg,int fg){ box(c,r,bg,16); text(c,s,r.centerX(),r.centerY()+7,20,fg,true,Paint.Align.CENTER); }
        private void softShadow(Canvas c,RectF r,float rad){ p.setColor(Color.argb(18,20,60,30)); RectF s=new RectF(r.left,r.top+4,r.right,r.bottom+4); c.drawRoundRect(s,rad,rad,p); }
        private void gradientBox(Canvas c,RectF r,int c1,int c2,float rad){ Shader old=p.getShader(); p.setShader(new LinearGradient(r.left,r.top,r.right,r.bottom,c1,c2,Shader.TileMode.CLAMP)); c.drawRoundRect(r,rad,rad,p); p.setShader(old); }
        private void box(Canvas c,RectF r,int color,float rad){ p.setShader(null); p.setColor(color); p.setStyle(Paint.Style.FILL); c.drawRoundRect(r,rad,rad,p); }
        private void text(Canvas c,String s,float x,float y,float sz,int color,boolean bold){ text(c,s,x,y,sz,color,bold,Paint.Align.LEFT); }
        private void text(Canvas c,String s,float x,float y,float sz,int color,boolean bold,Paint.Align align){ p.setShader(null); p.setStyle(Paint.Style.FILL); p.setColor(color); p.setTextSize(sz*getResources().getDisplayMetrics().scaledDensity); p.setTypeface(Typeface.create("sans-serif-rounded",bold?Typeface.BOLD:Typeface.NORMAL)); p.setTextAlign(align); c.drawText(s,x,y,p); }

        @Override public boolean onTouchEvent(MotionEvent e){
            if(e.getAction()!=MotionEvent.ACTION_UP)return true;
            float x=e.getX(),y=e.getY();
            if(screen==0){
                for(int i=0;i<3;i++) if(cards[i].contains(x,y)){ selected=i; if(i==2)variant=0; invalidate(); return true; }
                if(varA.contains(x,y)){variant=0;invalidate();return true;}
                if(varB.contains(x,y)){variant=selected==2?0:1;invalidate();return true;}
                if(selected>=0&&start.contains(x,y)){screen=1;hasTarget=false;invalidate();return true;}
                return true;
            }

            if(screen==1 && courseRect.contains(x,y)){
                hasTarget=true; targetX=x; targetY=y; invalidate(); return true;
            }
            if(mapLaunch.contains(x,y)){launchMap();return true;}
            if(gpsSettings.contains(x,y)){launchGpsSettings();return true;}
            for(int i=0;i<4;i++) if(playerTabs[i].contains(x,y)){player=i;invalidate();return true;}

            int par=currentPar();
            if(minus.contains(x,y)){ setStroke(player,hole,Math.max(1,getStroke(player,hole,par)-1)); lastScoreTap=SystemClock.uptimeMillis(); }
            else if(plus.contains(x,y)){ setStroke(player,hole,getStroke(player,hole,par)+1); lastScoreTap=SystemClock.uptimeMillis(); }
            else if(pm.contains(x,y)){ setPutt(player,hole,Math.max(0,getPutt(player,hole)-1)); lastScoreTap=SystemClock.uptimeMillis(); }
            else if(pp.contains(x,y)){ setPutt(player,hole,getPutt(player,hole)+1); lastScoreTap=SystemClock.uptimeMillis(); }
            else if(prev.contains(x,y)){hole=Math.max(1,hole-1);hasTarget=false;}
            else if(next.contains(x,y)){hole=Math.min(18,hole+1);hasTarget=false;}
            else if(mapTab.contains(x,y)){screen=1;}
            else if(scoreTab.contains(x,y)){screen=2;}
            invalidate(); return true;
        }
    }
}
