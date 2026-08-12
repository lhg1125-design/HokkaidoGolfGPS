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
import android.os.Bundle;
import android.os.SystemClock;
import android.provider.Settings;
import android.view.MotionEvent;
import android.view.View;

import java.util.Locale;

public class FieldGpsActivity extends Activity implements LocationListener {
    private static final int REQ = 1707;
    private LocationManager lm;
    private GolfView view;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        boolean preview = getIntent().getBooleanExtra("preview", false);
        view = new GolfView(this, preview);
        setContentView(view);
        lm = (LocationManager) getSystemService(LOCATION_SERVICE);
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, REQ);
        } else startGps();
    }

    private void startGps() {
        if (lm == null || checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) return;
        try { lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 900, 0.8f, this); } catch (Exception ignored) {}
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
        private final SharedPreferences scorePrefs;
        private final SharedPreferences greenPrefs;

        private final String[] jp = {"上士幌ゴルフ場","富良野ゴルフコース","サホロカントリークラブ"};
        private final String[] ko = {"가미시호로 골프장","후라노 골프코스","사호로 컨트리클럽"};
        private final String[][] variantNames = {{"CHAMPIONS","MASTERS"},{"PALMER","KING"},{"OUT / IN","OUT / IN"}};
        private final double[] courseLat = {43.2570513, 43.3351203, 43.1551590};
        private final double[] courseLon = {143.2283621, 142.4817967, 142.8070984};

        private final int[][][] yards = {
                {{523,413,170,366,361,351,135,358,481,415,183,395,167,370,509,426,399,516},
                 {454,516,416,155,331,369,373,150,367,393,351,132,455,328,167,469,356,370}},
                {{470,410,171,411,545,426,400,174,379,395,132,420,342,414,527,182,388,525},
                 {313,168,401,523,386,335,175,359,489,350,312,535,346,151,360,170,422,506}},
                {{395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493},
                 {395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493}}
        };
        private final int[][][] pars = {
                {{5,4,3,4,4,4,3,4,5,4,3,4,3,4,5,4,4,5},
                 {5,5,4,3,4,4,4,3,4,4,4,3,5,4,3,5,4,5}},
                {{5,4,3,4,5,4,4,3,4,4,3,4,4,4,5,3,4,5},
                 {4,3,4,5,4,4,3,4,5,4,4,5,4,3,4,3,4,5}},
                {{4,5,4,3,4,5,4,3,4,4,3,4,5,4,3,4,4,5},
                 {4,5,4,3,4,5,4,3,4,4,3,4,5,4,3,4,4,5}}
        };

        private int selected=-1, variant=0, screen=0, hole=1, player=0;
        private Location location;
        private long firstFixAt=0, lastHoleChange=0, lastTap=0;
        private int lastDelta=0, holeDirection=1;
        private String toastText="";
        private long toastAt=0;

        private final RectF[] cards={new RectF(),new RectF(),new RectF()};
        private final RectF start=new RectF(), varA=new RectF(), varB=new RectF();
        private final RectF prev=new RectF(), next=new RectF(), scoreTab=new RectF(), mapTab=new RectF();
        private final RectF minus=new RectF(), plus=new RectF(), pm=new RectF(), pp=new RectF();
        private final RectF gpsSettings=new RectF(), calibrate=new RectF(), courseRect=new RectF();
        private final RectF[] playerTabs={new RectF(),new RectF(),new RectF(),new RectF()};

        private final int BG=Color.rgb(249,250,240), INK=Color.rgb(34,55,40), GREEN=Color.rgb(24,111,68), DEEP=Color.rgb(8,79,52),
                MINT=Color.rgb(223,244,208), SKY=Color.rgb(96,196,230), BLUE=Color.rgb(75,166,211), CORAL=Color.rgb(255,126,92),
                YELLOW=Color.rgb(255,208,64), CARD=Color.WHITE, SOFT=Color.rgb(241,245,235);

        GolfView(Context c, boolean preview){
            super(c); ctx=c; previewMode=preview;
            scorePrefs=c.getSharedPreferences("score_v07",MODE_PRIVATE);
            greenPrefs=c.getSharedPreferences("green_v07",MODE_PRIVATE);
            p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL));
            setKeepScreenOn(true);
        }

        void setLocation(Location l){
            if(location==null) firstFixAt=SystemClock.uptimeMillis();
            location=l;
            if(selected<0){ int n=nearestCourse(l); if(n>=0 && distanceToCourse(l,n)<8000) selected=n; }
            invalidate();
        }

        @Override protected void onDraw(Canvas c){
            c.drawColor(BG);
            if(screen==0) drawHome(c); else if(screen==1) drawRound(c); else drawScore(c);
            drawToast(c);
            postInvalidateDelayed(screen==1?50:110);
        }

        private void drawHome(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;
            text(c,"北海道ゴルフ",m,h*.066f,27,INK,true);
            text(c,"GPSキャディ",m,h*.111f,38,GREEN,true);
            pill(c,new RectF(m,h*.135f,m+w*.56f,h*.177f),Color.rgb(229,244,218),"V0.7 · FIELD GPS EDITION",GREEN,9.5f);
            mascot(c,w*.84f,h*.105f,28,true);
            speech(c,w*.59f,h*.155f,"GPS 엔진 출동!",GREEN);
            text(c,"오늘 어디서 칠까요?",m,h*.222f,18,INK,true);
            text(c,"실시간 GPS · 4인 스코어 · 그린 좌표 캘리브레이션",m,h*.252f,9.5f,Color.GRAY,false);

            float top=h*.286f,ch=h*.116f,gap=h*.014f;
            int[] ac={Color.rgb(174,222,92),YELLOW,SKY};
            for(int i=0;i<3;i++){
                float y=top+i*(ch+gap); cards[i].set(m,y,w-m,y+ch);
                softShadow(c,cards[i],26); box(c,cards[i],selected==i?Color.rgb(238,249,222):CARD,26);
                p.setColor(ac[i]); c.drawCircle(m+28,y+30,11,p);
                text(c,"DAY "+(i+1),m+50,y+35,9,GREEN,true);
                text(c,jp[i],m+22,y+70,18,INK,true);
                text(c,ko[i],m+22,y+94,10,Color.GRAY,false);
                if(location!=null){
                    int dm=(int)Math.round(distanceToCourse(location,i));
                    String ds=dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km";
                    pill(c,new RectF(w-m-105,y+17,w-m-14,y+48),SOFT,ds,selected==i?GREEN:Color.GRAY,8.5f);
                }
                if(selected==i){ p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(GREEN);c.drawRoundRect(cards[i],26,26,p);p.setStyle(Paint.Style.FILL); }
            }

            float vy=h*.692f; text(c,"코스 선택",m,vy,10,Color.GRAY,true);
            varA.set(m,vy+12,w*.48f,vy+58); varB.set(w*.52f,vy+12,w-m,vy+58);
            pillButton(c,varA,variant==0?GREEN:CARD,selected<0?"A COURSE":variantNames[selected][0],variant==0?Color.WHITE:INK);
            pillButton(c,varB,variant==1?GREEN:CARD,selected<0?"B COURSE":variantNames[selected][1],variant==1?Color.WHITE:INK);
            start.set(m,h*.803f,w-m,h*.88f); gradient(c,start,selected>=0?DEEP:Color.LTGRAY,selected>=0?GREEN:Color.GRAY,36); sheen(c,start,36);
            text(c,selected>=0?"라운드 시작  →":"골프장을 먼저 선택해주세요",w/2,h*.852f,15,selected>=0?Color.WHITE:Color.DKGRAY,true,Paint.Align.CENTER);
            text(c,"모든 거리 m · Android Studio 없이 Cloud Build",w/2,h*.925f,9,Color.GRAY,false,Paint.Align.CENTER);
        }

        private void drawRound(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f; int par=currentPar(); int officialM=(int)Math.round(currentYards()*.9144);
            float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/320.0));
            text(c,ko[selected]+" · "+variantNames[selected][variant],m,h*.044f,11,Color.GRAY,true);
            text(c,"H"+hole,m,h*.095f,37,INK,true); pill(c,new RectF(m+76,h*.064f,m+145,h*.104f),Color.rgb(229,244,218),"PAR "+par,GREEN,10.5f);
            String gps=location==null?"GPS 찾는 중…":"GPS ±"+Math.round(location.getAccuracy())+"m";
            pill(c,new RectF(w-m-135,h*.022f,w-m,h*.062f),location==null?Color.rgb(255,238,229):Color.rgb(229,244,218),gps,location==null?CORAL:GREEN,9.5f);

            GreenRef ref=getGreenRef(); Distances ds=distances(ref);
            RectF range=new RectF(m,h*.125f,w-m,h*.235f); gradient(c,range,DEEP,GREEN,28); sheen(c,range,28);
            metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.159f);
            metric(c,"CENTER",ds.center<0?"--":ds.center+"m",w*.50f,h*.159f);
            metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.159f);
            String status=ref==null?"GREEN DB 미등록":(ref.demo?"DEMO 좌표":"GREEN CENTER 저장됨");
            pill(c,new RectF(w*.35f,h*.218f,w*.65f,h*.248f),ref==null?Color.rgb(255,242,225):Color.rgb(229,244,218),status,ref==null?CORAL:GREEN,8.5f);

            courseRect.set(m,h*.265f,w-m,h*.605f); drawCourse(c,courseRect,par,officialM,ref,ds,pulse);
            text(c,"V0.7 · 실제 GPS 거리 엔진 · Front/Back은 Center ±12m 임시 모델",w/2,h*.629f,8.5f,Color.GRAY,false,Paint.Align.CENTER);

            calibrate.set(m,h*.648f,w*.61f,h*.702f); gpsSettings.set(w*.64f,h*.648f,w-m,h*.702f);
            pillButton(c,calibrate,ref==null?CORAL:DEEP,ref==null?"그린 위에서 CENTER 저장":"CENTER 다시 저장",Color.WHITE);
            pillButton(c,gpsSettings,CARD,"GPS 설정",INK);

            drawPlayerTabs(c,h*.728f);
            RectF panel=new RectF(m,h*.77f,w-m,h*.872f); softShadow(c,panel,26); box(c,panel,CARD,26);
            int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);
            text(c,"타수",m+18,h*.804f,10,Color.GRAY,true); text(c,""+stroke,w*.28f,h*.85f,30,INK,true,Paint.Align.CENTER);
            minus.set(m+10,h*.812f,m+52,h*.864f); plus.set(w*.38f,h*.812f,w*.47f,h*.864f); roundButton(c,minus,"−",SOFT,Color.GRAY); roundButton(c,plus,"+",Color.rgb(229,244,218),GREEN);
            text(c,"퍼트",w*.56f,h*.804f,10,Color.GRAY,true); text(c,""+putt,w*.70f,h*.85f,29,INK,true,Paint.Align.CENTER);
            pm.set(w*.53f,h*.812f,w*.61f,h*.864f); pp.set(w*.82f,h*.812f,w*.90f,h*.864f); roundButton(c,pm,"−",SOFT,Color.GRAY); roundButton(c,pp,"+",Color.rgb(226,245,250),SKY);
            drawTapBurst(c,h); nav(c);
        }

        private void drawCourse(Canvas c,RectF r,int par,int officialM,GreenRef ref,Distances ds,float pulse){
            long now=SystemClock.uptimeMillis(); float phase=(now%2400)/2400f; float slide=holeSlideOffset(now);
            c.save(); c.translate(slide,0); gradient(c,r,Color.rgb(232,248,214),Color.rgb(202,236,191),32);
            drawMountains(c,r); drawCloud(c,r.left+r.width()*.16f+phase*10,r.top+32,18); drawCloud(c,r.left+r.width()*.76f-phase*8,r.top+44,14);
            float cx=r.centerX(); Path f=new Path(); f.moveTo(cx-22,r.bottom-25);
            if(par==3) f.cubicTo(cx-15,r.centerY()+35,cx+10,r.centerY()-35,cx-8,r.top+60);
            else if(par==4) f.cubicTo(r.left+r.width()*.38f,r.bottom-r.height()*.28f,r.left+r.width()*.64f,r.top+r.height()*.48f,cx-8,r.top+58);
            else f.cubicTo(r.left+r.width()*.31f,r.bottom-r.height()*.2f,r.left+r.width()*.69f,r.top+r.height()*.54f,cx-8,r.top+58);
            f.lineTo(cx+48,r.top+66); f.cubicTo(r.left+r.width()*.72f,r.top+r.height()*.50f,r.left+r.width()*.5f,r.bottom-r.height()*.22f,cx+24,r.bottom-25); f.close();
            p.setColor(Color.rgb(90,180,87)); c.drawPath(f,p); stripes(c,f,r,phase);
            RectF water=new RectF(r.left+16,r.top+r.height()*.48f,r.left+r.width()*.39f,r.bottom-18); p.setColor(BLUE); c.drawOval(water,p); ripples(c,water,phase);
            p.setColor(YELLOW); c.drawOval(new RectF(cx+36,r.top+r.height()*.43f,cx+84,r.top+r.height()*.50f),p);
            float flagX=cx+12,flagY=r.top+58; p.setStrokeWidth(4);p.setColor(INK);c.drawLine(flagX,flagY,flagX,r.top+25,p); Path flag=new Path();flag.moveTo(flagX,r.top+25);flag.lineTo(flagX+28+6*pulse,r.top+32);flag.lineTo(flagX,r.top+41);flag.close();p.setColor(CORAL);c.drawPath(flag,p);p.setColor(Color.rgb(74,168,78));c.drawOval(new RectF(cx-29,r.top+46,cx+50,r.top+84),p);
            float youX=cx,youY=r.bottom-34; dashRoute(c,youX,youY,flagX,flagY+10,phase); p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.argb(90+(int)(80*pulse),24,111,68));c.drawCircle(youX,youY,16+10*pulse,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.WHITE);c.drawCircle(youX,youY,10,p);p.setColor(GREEN);c.drawCircle(youX,youY,4,p);text(c,"YOU",youX,r.bottom-8,8,GREEN,true,Paint.Align.CENTER);
            String bubble;
            if(ref==null) bubble="그린 좌표가 필요해!"; else if(ds.center>=0) bubble="CENTER "+ds.center+"m"; else bubble="GPS 기다리는 중!";
            mascot(c,r.right-45,r.top+48,22,true); speech(c,r.right-188,r.top+18,bubble,ref==null?CORAL:DEEP);
            if(previewMode){ pill(c,new RectF(r.left+15,r.bottom-45,r.left+116,r.bottom-16),Color.argb(225,255,255,255),"PREVIEW GPS",CORAL,7.5f); }
            c.restore();
        }

        private void calibrateGreen(){
            if(location==null){ showToast("GPS 위치를 먼저 잡아주세요"); return; }
            String k=greenKey(); greenPrefs.edit().putLong(k+"_lat",Double.doubleToRawLongBits(location.getLatitude())).putLong(k+"_lon",Double.doubleToRawLongBits(location.getLongitude())).apply();
            showToast("H"+hole+" 그린 CENTER 저장 완료"); invalidate();
        }

        private GreenRef getGreenRef(){
            String k=greenKey();
            if(greenPrefs.contains(k+"_lat")) return new GreenRef(Double.longBitsToDouble(greenPrefs.getLong(k+"_lat",0)),Double.longBitsToDouble(greenPrefs.getLong(k+"_lon",0)),false);
            if(previewMode && selected==0 && variant==0 && hole==1) return new GreenRef(43.25982,143.22836,true);
            return null;
        }
        private String greenKey(){ return "g_"+selected+"_"+variant+"_"+hole; }
        private Distances distances(GreenRef ref){
            if(ref==null || location==null) return new Distances(-1,-1,-1);
            float[] out=new float[1]; Location.distanceBetween(location.getLatitude(),location.getLongitude(),ref.lat,ref.lon,out); int center=Math.round(out[0]); return new Distances(Math.max(0,center-12),center,center+12);
        }

        private void drawScore(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.05f; text(c,"스코어카드",m,h*.068f,29,INK,true); text(c,ko[selected]+" · "+variantNames[selected][variant],m,h*.10f,10,Color.GRAY,false); mascot(c,w*.88f,h*.078f,20,true); text(c,"4명 한 번에 · 홀 이동은 아래 버튼",m,h*.132f,10,Color.GRAY,false);
            float y=h*.18f; int[] totals={0,0,0,0};
            for(int i=1;i<=18;i++){ int pa=parForHole(i); RectF row=new RectF(m,y-17,w-m,y+19); box(c,row,i==hole?Color.rgb(238,249,222):(i%2==0?Color.rgb(252,253,248):CARD),14); text(c,"H"+i,m+12,y+6,9,INK,true); text(c,"P"+pa,w*.25f,y+6,8,Color.GRAY,false,Paint.Align.CENTER); for(int pl=0;pl<4;pl++){int s=getStroke(pl,i,pa);totals[pl]+=s;int col=s>pa?CORAL:(s<pa?GREEN:INK);text(c,""+s,w*(.43f+pl*.14f),y+6,10,col,true,Paint.Align.CENTER);} y+=h*.031f; }
            RectF total=new RectF(m,h*.775f,w-m,h*.862f);gradient(c,total,DEEP,GREEN,25);sheen(c,total,25);text(c,"TOTAL",m+16,h*.818f,9,Color.WHITE,true);for(int pl=0;pl<4;pl++)text(c,"P"+(pl+1)+"  "+totals[pl],w*(.36f+pl*.16f),h*.826f,11,Color.WHITE,true,Paint.Align.CENTER);nav(c);
        }

        private void drawPlayerTabs(Canvas c,float y){ float w=getWidth(),m=w*.045f,gap=6,avail=w-2*m,ww=(avail-gap*3)/4;int[] dots={GREEN,SKY,CORAL,YELLOW};for(int i=0;i<4;i++){float l=m+i*(ww+gap);playerTabs[i].set(l,y,l+ww,y+34);box(c,playerTabs[i],player==i?GREEN:CARD,18);p.setColor(dots[i]);c.drawCircle(l+13,y+17,4,p);text(c,"P"+(i+1),l+ww/2+6,y+22,10,player==i?Color.WHITE:INK,true,Paint.Align.CENTER);} }
        private void nav(Canvas c){ float w=getWidth(),h=getHeight(),m=w*.045f;prev.set(m,h*.905f,w*.23f,h*.965f);mapTab.set(w*.27f,h*.905f,w*.49f,h*.965f);scoreTab.set(w*.53f,h*.905f,w*.75f,h*.965f);next.set(w*.79f,h*.905f,w-m,h*.965f);pillButton(c,prev,CARD,"‹ 이전",INK);pillButton(c,mapTab,screen==1?GREEN:CARD,"지도",screen==1?Color.WHITE:INK);pillButton(c,scoreTab,screen==2?GREEN:CARD,"스코어",screen==2?Color.WHITE:INK);pillButton(c,next,CARD,"다음 ›",INK); }

        private int currentPar(){return parForHole(hole);} private int parForHole(int h){return pars[selected][variant][h-1];} private int currentYards(){return yards[selected][variant][hole-1];}
        private int getStroke(int pl,int h,int par){return scorePrefs.getInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,par);} private int getPutt(int pl,int h){return scorePrefs.getInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,0);} private void setStroke(int pl,int h,int v){scorePrefs.edit().putInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply();} private void setPutt(int pl,int h,int v){scorePrefs.edit().putInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply();}
        private int nearestCourse(Location l){int best=-1;float bd=Float.MAX_VALUE;for(int i=0;i<3;i++){float d=(float)distanceToCourse(l,i);if(d<bd){bd=d;best=i;}}return best;} private double distanceToCourse(Location l,int i){if(l==null)return -1;float[] out=new float[1];Location.distanceBetween(l.getLatitude(),l.getLongitude(),courseLat[i],courseLon[i],out);return out[0];}
        private void launchGpsSettings(){try{ctx.startActivity(new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS));}catch(Exception ignored){}}

        private void showToast(String s){toastText=s;toastAt=SystemClock.uptimeMillis();}
        private void drawToast(Canvas c){if(toastAt==0)return;long age=SystemClock.uptimeMillis()-toastAt;if(age>1800)return;float w=getWidth(),h=getHeight();int a=age<1400?245:(int)(245*(1-(age-1400)/400f));RectF r=new RectF(w*.19f,h*.49f,w*.81f,h*.545f);box(c,r,Color.argb(Math.max(0,a),20,70,45),24);text(c,toastText,w/2,r.centerY()+5,10,Color.WHITE,true,Paint.Align.CENTER);}
        private void drawTapBurst(Canvas c,float h){long age=SystemClock.uptimeMillis()-lastTap;if(age>600||lastDelta==0)return;float t=age/600f;float x=lastDelta>0?getWidth()*.43f:getWidth()*.12f;float y=h*.82f-t*45;int a=(int)(255*(1-t));p.setColor(Color.argb(Math.min(220,a),255,255,255));c.drawCircle(x,y,18,p);text(c,lastDelta>0?"+1":"−1",x,y+5,10,Color.argb(a,24,111,68),true,Paint.Align.CENTER);}
        private float holeSlideOffset(long now){if(lastHoleChange==0)return 0;float t=(now-lastHoleChange)/320f;if(t>=1)return 0;float e=1-(1-t)*(1-t)*(1-t);return holeDirection*getWidth()*(1-e)*.34f;}

        private void drawMountains(Canvas c,RectF r){Path a=new Path();a.moveTo(r.left,r.top+90);a.lineTo(r.left+78,r.top+30);a.lineTo(r.left+145,r.top+90);a.close();p.setColor(Color.argb(70,100,150,112));c.drawPath(a,p);Path b=new Path();b.moveTo(r.left+92,r.top+90);b.lineTo(r.left+176,r.top+18);b.lineTo(r.left+262,r.top+90);b.close();p.setColor(Color.argb(58,70,130,95));c.drawPath(b,p);}
        private void drawCloud(Canvas c,float x,float y,float s){p.setColor(Color.argb(210,255,255,255));c.drawCircle(x,y,s*.45f,p);c.drawCircle(x+s*.4f,y-s*.1f,s*.58f,p);c.drawCircle(x+s*.86f,y,s*.42f,p);c.drawRoundRect(new RectF(x-s*.1f,y,x+s*1.15f,y+s*.38f),s*.18f,s*.18f,p);}
        private void stripes(Canvas c,Path f,RectF r,float phase){c.save();c.clipPath(f);p.setStrokeWidth(22);for(int i=-8;i<20;i++){float x=r.left+i*44+phase*44;p.setColor(i%2==0?Color.argb(18,255,255,255):Color.argb(11,20,90,40));c.drawLine(x,r.bottom,x+r.height()*.55f,r.top,p);}c.restore();}
        private void ripples(Canvas c,RectF water,float phase){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);p.setColor(Color.argb(100,255,255,255));for(int i=0;i<3;i++){float g=(phase+i*.28f)%1f;float rw=water.width()*(.12f+.28f*g),rh=water.height()*(.04f+.07f*g),cy=water.centerY()+i*15;c.drawOval(new RectF(water.centerX()-rw,cy-rh,water.centerX()+rw,cy+rh),p);}p.setStyle(Paint.Style.FILL);}
        private void dashRoute(Canvas c,float x1,float y1,float x2,float y2,float phase){float dx=x2-x1,dy=y2-y1,len=(float)Math.sqrt(dx*dx+dy*dy);if(len<1)return;float ux=dx/len,uy=dy/len,start=(phase*24)%24;p.setStrokeWidth(2);p.setColor(Color.argb(170,255,255,255));for(float d=start;d<len;d+=24){float e=Math.min(d+11,len);c.drawLine(x1+ux*d,y1+uy*d,x1+ux*e,y1+uy*e,p);}}
        private void mascot(Canvas c,float x,float y,float r,boolean wave){float bob=(float)Math.sin(SystemClock.uptimeMillis()/300.0)*2;y+=bob;p.setColor(Color.argb(24,20,60,30));c.drawOval(new RectF(x-r*.8f,y+r*.78f,x+r*.8f,y+r,p));p.setColor(Color.WHITE);c.drawCircle(x,y,r,p);p.setColor(INK);c.drawCircle(x-r*.25f,y-r*.05f,r*.075f,p);c.drawCircle(x+r*.25f,y-r*.05f,r*.075f,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);c.drawArc(new RectF(x-r*.3f,y-r*.02f,x+r*.3f,y+r*.45f),15,150,false,p);p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawRoundRect(new RectF(x-r*.65f,y-r*.82f,x+r*.58f,y-r*.48f),r*.16f,r*.16f,p);if(wave){p.setStrokeWidth(Math.max(3,r*.12f));p.setColor(INK);c.drawLine(x+r*.68f,y,x+r*1.15f,y-r*.42f+(float)Math.sin(SystemClock.uptimeMillis()/160.0)*r*.18f,p);}}
        private void speech(Canvas c,float x,float y,String s,int col){RectF b=new RectF(x,y,x+135,y+36);softShadow(c,b,18);box(c,b,Color.argb(242,255,255,255),18);text(c,s,b.centerX(),b.centerY()+4,8.8f,col,true,Paint.Align.CENTER);}
        private void metric(Canvas c,String lab,String val,float x,float y){text(c,lab,x,y,9,Color.rgb(212,237,219),true,Paint.Align.CENTER);text(c,val,x,y+getHeight()*.041f,19,Color.WHITE,true,Paint.Align.CENTER);}
        private void pill(Canvas c,RectF r,int bg,String s,int fg,float z){box(c,r,bg,r.height()/2);text(c,s,r.centerX(),r.centerY()+4,z,fg,true,Paint.Align.CENTER);} private void pillButton(Canvas c,RectF r,int bg,String s,int fg){softShadow(c,r,20);box(c,r,bg,20);text(c,s,r.centerX(),r.centerY()+5,10.2f,fg,true,Paint.Align.CENTER);} private void roundButton(Canvas c,RectF r,String s,int bg,int fg){box(c,r,bg,16);text(c,s,r.centerX(),r.centerY()+7,20,fg,true,Paint.Align.CENTER);} private void softShadow(Canvas c,RectF r,float rad){p.setColor(Color.argb(18,20,60,30));c.drawRoundRect(new RectF(r.left,r.top+4,r.right,r.bottom+4),rad,rad,p);} private void gradient(Canvas c,RectF r,int a,int b,float rad){Shader old=p.getShader();p.setShader(new LinearGradient(r.left,r.top,r.right,r.bottom,a,b,Shader.TileMode.CLAMP));c.drawRoundRect(r,rad,rad,p);p.setShader(old);} private void sheen(Canvas c,RectF r,float rad){float phase=(SystemClock.uptimeMillis()%3200)/3200f;float x=r.left-r.width()*.35f+phase*r.width()*1.7f;Path clip=new Path();clip.addRoundRect(r,rad,rad,Path.Direction.CW);c.save();c.clipPath(clip);p.setColor(Color.argb(18,255,255,255));Path s=new Path();s.moveTo(x-r.width()*.12f,r.bottom);s.lineTo(x+r.width()*.06f,r.top);s.lineTo(x+r.width()*.22f,r.top);s.lineTo(x+r.width()*.04f,r.bottom);s.close();c.drawPath(s,p);c.restore();} private void box(Canvas c,RectF r,int col,float rad){p.setShader(null);p.setStyle(Paint.Style.FILL);p.setColor(col);c.drawRoundRect(r,rad,rad,p);} private void text(Canvas c,String s,float x,float y,float z,int col,boolean bold){text(c,s,x,y,z,col,bold,Paint.Align.LEFT);} private void text(Canvas c,String s,float x,float y,float z,int col,boolean bold,Paint.Align a){p.setShader(null);p.setStyle(Paint.Style.FILL);p.setColor(col);p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);p.setTypeface(Typeface.create("sans-serif-rounded",bold?Typeface.BOLD:Typeface.NORMAL));p.setTextAlign(a);c.drawText(s,x,y,p);}

        @Override public boolean onTouchEvent(MotionEvent e){
            if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();
            if(screen==0){for(int i=0;i<3;i++)if(cards[i].contains(x,y)){selected=i;if(i==2)variant=0;invalidate();return true;}if(varA.contains(x,y)){variant=0;invalidate();return true;}if(varB.contains(x,y)){variant=selected==2?0:1;invalidate();return true;}if(selected>=0&&start.contains(x,y)){screen=1;invalidate();return true;}return true;}
            if(calibrate.contains(x,y)){calibrateGreen();return true;}if(gpsSettings.contains(x,y)){launchGpsSettings();return true;}for(int i=0;i<4;i++)if(playerTabs[i].contains(x,y)){player=i;invalidate();return true;}
            int par=currentPar();if(minus.contains(x,y)){setStroke(player,hole,Math.max(1,getStroke(player,hole,par)-1));lastTap=SystemClock.uptimeMillis();lastDelta=-1;}else if(plus.contains(x,y)){setStroke(player,hole,getStroke(player,hole,par)+1);lastTap=SystemClock.uptimeMillis();lastDelta=1;}else if(pm.contains(x,y)){setPutt(player,hole,Math.max(0,getPutt(player,hole)-1));lastTap=SystemClock.uptimeMillis();lastDelta=-1;}else if(pp.contains(x,y)){setPutt(player,hole,getPutt(player,hole)+1);lastTap=SystemClock.uptimeMillis();lastDelta=1;}else if(prev.contains(x,y)){if(hole>1){hole--;holeDirection=-1;lastHoleChange=SystemClock.uptimeMillis();}}else if(next.contains(x,y)){if(hole<18){hole++;holeDirection=1;lastHoleChange=SystemClock.uptimeMillis();}}else if(mapTab.contains(x,y)){screen=1;}else if(scoreTab.contains(x,y)){screen=2;}invalidate();return true;
        }

        static final class GreenRef{final double lat,lon;final boolean demo;GreenRef(double a,double o,boolean d){lat=a;lon=o;demo=d;}}
        static final class Distances{final int front,center,back;Distances(int f,int c,int b){front=f;center=c;back=b;}}
    }
}
