package com.hokkaidogolf.trip;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
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
        try { lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1200, 1.0f, this); } catch (Exception ignored) {}
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

        // Official course-center points from each course's published Google Maps link.
        private final double[] courseLat = {43.2570513, 43.3351203, 43.15515899658203};
        private final double[] courseLon = {143.2283621, 142.4817967, 142.80709838867188};

        // Official REGULAR tee yardages. Converted to meters on screen (1 yd = 0.9144 m).
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

        private int selected = -1, variant = 0, screen = 0, hole = 1, player = 0;
        private Location location;
        private float touchX=-1, touchY=-1;
        private final RectF[] cards = {new RectF(),new RectF(),new RectF()};
        private final RectF start = new RectF(), varA = new RectF(), varB = new RectF();
        private final RectF minus = new RectF(), plus = new RectF(), pm = new RectF(), pp = new RectF(), prev = new RectF(), next = new RectF(), score = new RectF(), mapTab = new RectF(), mapLaunch = new RectF(), gpsSettings = new RectF();
        private final RectF[] playerTabs = {new RectF(),new RectF(),new RectF(),new RectF()};
        private final int BG=Color.rgb(247,250,239), INK=Color.rgb(37,53,39), GREEN=Color.rgb(22,103,62), CARD=Color.WHITE, LIME=Color.rgb(183,225,92), SKY=Color.rgb(106,200,235), CORAL=Color.rgb(255,132,96), YELLOW=Color.rgb(255,211,72), DEEP=Color.rgb(10,75,49);

        GolfView(Context c) {
            super(c);
            ctx=c;
            prefs=c.getSharedPreferences("score_v04",MODE_PRIVATE);
            p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL));
            setKeepScreenOn(true);
        }

        void setLocation(Location l){
            location=l;
            if (selected < 0) {
                int near = nearestCourse(l);
                if (near >= 0 && distanceToCourse(l,near) < 8000) selected=near;
            }
            invalidate();
        }

        @Override protected void onDraw(Canvas c){
            super.onDraw(c);
            c.drawColor(BG);
            if(screen==0) home(c); else if(screen==1) round(c); else score(c);
            if (screen==1 && location==null) postInvalidateDelayed(500);
        }

        private void home(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;
            text(c,"北海道ゴルフ",m,h*.075f,29,INK,true);
            text(c,"GPSキャディ",m,h*.125f,40,GREEN,true);
            text(c,"8/24~26 · HOKKAIDO TRIP",m,h*.158f,11,Color.DKGRAY,true);
            mascot(c,w*.84f,h*.11f,18);
            text(c,"오늘 어디서 칠까요?",m,h*.205f,18,INK,true);
            text(c,"GPS + 코스 데이터 + 4인 스코어 · 모든 거리 m",m,h*.238f,11,Color.GRAY,false);

            float top=h*.275f,ch=h*.115f,gap=h*.014f; int[] a={LIME,YELLOW,SKY};
            for(int i=0;i<3;i++){
                float y=top+i*(ch+gap); cards[i].set(m,y,w-m,y+ch);
                box(c,cards[i],selected==i?Color.rgb(235,248,211):CARD,26);
                p.setColor(a[i]); c.drawCircle(m+28,y+28,9,p);
                text(c,"0"+(i+1),m+49,y+34,11,GREEN,true);
                text(c,jp[i],m+22,y+66,18,INK,true);
                text(c,ko[i],m+22,y+91,11,Color.GRAY,false);
                if(location!=null){
                    int dm=(int)Math.round(distanceToCourse(location,i));
                    text(c,dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km",w-m-18,y+34,10,selected==i?GREEN:Color.GRAY,true,Paint.Align.RIGHT);
                }
            }

            float vy=h*.69f;
            text(c,"코스 선택",m,vy,11,Color.GRAY,true);
            varA.set(m,vy+12,w*.48f,vy+58); varB.set(w*.52f,vy+12,w-m,vy+58);
            box(c,varA,variant==0?GREEN:CARD,22); box(c,varB,variant==1?GREEN:CARD,22);
            String va=selected<0?"A COURSE":variantNames[selected][0];
            String vb=selected<0?"B COURSE":variantNames[selected][1];
            text(c,va,varA.centerX(),varA.centerY()+5,11,variant==0?Color.WHITE:INK,true,Paint.Align.CENTER);
            text(c,vb,varB.centerX(),varB.centerY()+5,11,variant==1?Color.WHITE:INK,true,Paint.Align.CENTER);

            start.set(m,h*.80f,w-m,h*.875f);
            box(c,start,selected>=0?GREEN:Color.LTGRAY,36);
            text(c,selected>=0?"라운드 시작 →":"골프장을 먼저 선택해주세요",w/2,h*.848f,15,selected>=0?Color.WHITE:Color.DKGRAY,true,Paint.Align.CENTER);
            text(c,"REGULAR TEE 기준 · GPS는 휴대폰 센서 사용",w/2,h*.925f,10,Color.GRAY,false,Paint.Align.CENTER);
            if(location==null) text(c,"위치 권한을 허용하면 가까운 골프장을 자동으로 잡아요 📍",w/2,h*.958f,10,CORAL,true,Paint.Align.CENTER);
        }

        private void round(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;
            String vName=variantNames[Math.max(0,selected)][variant];
            text(c,ko[Math.max(0,selected)]+" · "+vName,m,h*.048f,12,Color.GRAY,true);
            text(c,"H"+hole,m,h*.102f,38,INK,true);
            int par=currentPar();
            text(c,"PAR "+par,m+78,h*.098f,14,GREEN,true);
            text(c,location==null?"GPS 찾는 중…":"GPS ±"+Math.round(location.getAccuracy())+"m",w-m,h*.048f,11,location==null?CORAL:GREEN,true,Paint.Align.RIGHT);

            RectF hud=new RectF(m,h*.125f,w-m,h*.225f); box(c,hud,GREEN,28);
            int officialM=(int)Math.round(currentYards()*0.9144);
            metric(c,"REGULAR",officialM,w*.22f,h*.158f);
            metric(c,"PAR",par,w*.50f,h*.158f);
            int ccDist=location==null?-1:(int)Math.round(distanceToCourse(location,selected));
            metric(c,"코스센터",ccDist,w*.78f,h*.158f);

            RectF course=new RectF(m,h*.245f,w-m,h*.61f); box(c,course,Color.rgb(225,242,204),34); drawCourse(c,course,par);
            text(c,"홀맵 V0.4 · 공식 홀 거리 + 실시간 GPS 위치 상태",w/2,h*.637f,10,Color.GRAY,false,Paint.Align.CENTER);

            mapLaunch.set(m,h*.655f,w*.58f,h*.705f); gpsSettings.set(w*.61f,h*.655f,w-m,h*.705f);
            box(c,mapLaunch,DEEP,20); box(c,gpsSettings,CARD,20);
            text(c,"지도 앱에서 코스 열기 ↗",mapLaunch.centerX(),mapLaunch.centerY()+5,11,Color.WHITE,true,Paint.Align.CENTER);
            text(c,"GPS 설정",gpsSettings.centerX(),gpsSettings.centerY()+5,11,INK,true,Paint.Align.CENTER);

            playerTabs(c,h*.73f);
            RectF panel=new RectF(m,h*.775f,w-m,h*.875f); box(c,panel,CARD,26);
            int stroke=getStroke(player,hole,par), putt=getPutt(player,hole);
            text(c,"타수",m+18,h*.805f,10,Color.GRAY,true); text(c,""+stroke,w*.28f,h*.852f,31,INK,true,Paint.Align.CENTER);
            minus.set(m+10,h*.815f,m+52,h*.865f); plus.set(w*.38f,h*.815f,w*.47f,h*.865f); button(c,minus,"−",Color.GRAY); button(c,plus,"+",GREEN);
            text(c,"퍼트",w*.56f,h*.805f,10,Color.GRAY,true); text(c,""+putt,w*.70f,h*.852f,29,INK,true,Paint.Align.CENTER);
            pm.set(w*.53f,h*.815f,w*.61f,h*.865f); pp.set(w*.82f,h*.815f,w*.90f,h*.865f); button(c,pm,"−",Color.GRAY); button(c,pp,"+",SKY);
            nav(c);
        }

        private void drawCourse(Canvas c,RectF r,int par){
            float pulse=(float)((Math.sin(SystemClock.uptimeMillis()/360.0)+1)/2.0);
            p.setColor(SKY); c.drawOval(new RectF(r.left+18,r.top+r.height()*.43f,r.left+r.width()*.40f,r.bottom-18),p);
            p.setColor(Color.rgb(91,178,82));
            Path f=new Path();
            f.moveTo(r.centerX(),r.bottom-25);
            if(par==3) f.cubicTo(r.centerX()-15,r.centerY()+30,r.centerX()+10,r.centerY()-30,r.centerX(),r.top+35);
            else if(par==4) f.cubicTo(r.left+r.width()*.32f,r.top+r.height()*.72f,r.left+r.width()*.67f,r.top+r.height()*.46f,r.centerX(),r.top+30);
            else f.cubicTo(r.left+r.width()*.27f,r.top+r.height()*.78f,r.left+r.width()*.74f,r.top+r.height()*.45f,r.centerX(),r.top+30);
            f.lineTo(r.centerX()+50,r.top+40);
            f.cubicTo(r.left+r.width()*.72f,r.top+r.height()*.47f,r.left+r.width()*.52f,r.top+r.height()*.74f,r.centerX()+25,r.bottom-25);
            f.close(); c.drawPath(f,p);
            p.setColor(YELLOW); c.drawOval(new RectF(r.centerX()+32,r.top+r.height()*.40f,r.centerX()+79,r.top+r.height()*.47f),p);
            p.setColor(CORAL); c.drawCircle(r.centerX()+13,r.top+58,8,p); text(c,"⚑",r.centerX()+13,r.top+50,20,INK,true,Paint.Align.CENTER);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(3); p.setColor(Color.argb(110,(int)(80+120*pulse),180,110)); c.drawCircle(r.centerX(),r.bottom-38,17+8*pulse,p); p.setStyle(Paint.Style.FILL);
            p.setColor(Color.WHITE); c.drawCircle(r.centerX(),r.bottom-38,10,p); text(c,"YOU",r.centerX(),r.bottom-12,9,GREEN,true,Paint.Align.CENTER);
            mascot(c,r.right-37,r.top+38,13);
        }

        private void playerTabs(Canvas c,float y){
            float w=getWidth(),m=w*.045f,gap=6,avail=w-2*m,ww=(avail-gap*3)/4;
            for(int i=0;i<4;i++){
                float l=m+i*(ww+gap); playerTabs[i].set(l,y,l+ww,y+36);
                box(c,playerTabs[i],player==i?GREEN:CARD,18);
                text(c,"P"+(i+1),playerTabs[i].centerX(),playerTabs[i].centerY()+5,10,player==i?Color.WHITE:INK,true,Paint.Align.CENTER);
            }
        }

        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.05f;
            text(c,"스코어카드",m,h*.075f,31,INK,true);
            text(c,ko[Math.max(0,selected)]+" · "+variantNames[Math.max(0,selected)][variant],m,h*.108f,10,Color.GRAY,false);
            text(c,"4명 모두 한 화면에. 계산은 앱이 할게요 😄",m,h*.14f,11,Color.GRAY,false);
            float y=h*.195f; int[] totals={0,0,0,0};
            for(int i=1;i<=18;i++){
                int pa=parForHole(i); RectF r=new RectF(m,y-18,w-m,y+20); box(c,r,i==hole?Color.rgb(235,248,211):CARD,15);
                text(c,"H"+i,m+12,y+6,10,INK,true); text(c,"P"+pa,w*.25f,y+6,9,Color.GRAY,false,Paint.Align.CENTER);
                for(int pl=0;pl<4;pl++){ int s=getStroke(pl,i,pa); totals[pl]+=s; int col=s>pa?CORAL:(s<pa?GREEN:INK); text(c,""+s,w*(.43f+pl*.14f),y+6,11,col,true,Paint.Align.CENTER); }
                y+=h*.031f;
            }
            RectF t=new RectF(m,h*.78f,w-m,h*.865f); box(c,t,GREEN,25);
            text(c,"TOTAL",m+16,h*.823f,10,Color.WHITE,true);
            for(int pl=0;pl<4;pl++) text(c,"P"+(pl+1)+" "+totals[pl],w*(.36f+pl*.16f),h*.828f,12,Color.WHITE,true,Paint.Align.CENTER);
            nav(c);
        }

        private void nav(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;
            prev.set(m,h*.905f,w*.23f,h*.965f); mapTab.set(w*.27f,h*.905f,w*.49f,h*.965f); score.set(w*.53f,h*.905f,w*.75f,h*.965f); next.set(w*.79f,h*.905f,w-m,h*.965f);
            box(c,prev,CARD,21); box(c,next,CARD,21); box(c,mapTab,screen==1?GREEN:CARD,21); box(c,score,screen==2?GREEN:CARD,21);
            text(c,"‹ 이전",prev.centerX(),prev.centerY()+5,11,INK,true,Paint.Align.CENTER); text(c,"지도",mapTab.centerX(),mapTab.centerY()+5,11,screen==1?Color.WHITE:INK,true,Paint.Align.CENTER); text(c,"스코어",score.centerX(),score.centerY()+5,11,screen==2?Color.WHITE:INK,true,Paint.Align.CENTER); text(c,"다음 ›",next.centerX(),next.centerY()+5,11,INK,true,Paint.Align.CENTER);
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

        private void metric(Canvas c,String label,int d,float x,float y){
            text(c,label,x,y,9,Color.rgb(210,235,216),true,Paint.Align.CENTER);
            String s=d<0?"--":(d>9999?String.format(Locale.US,"%.1fkm",d/1000f):d+"m");
            text(c,s,x,y+getHeight()*.042f,20,Color.WHITE,true,Paint.Align.CENTER);
        }
        private void mascot(Canvas c,float x,float y,float r){
            float bob=(float)Math.sin(SystemClock.uptimeMillis()/260.0)*3;
            p.setColor(Color.WHITE); c.drawCircle(x,y+bob,r,p); p.setColor(Color.rgb(205,205,195)); c.drawCircle(x-r*.30f,y-r*.15f+bob,r*.10f,p); c.drawCircle(x+r*.25f,y+r*.2f+bob,r*.08f,p); p.setColor(INK); c.drawCircle(x-r*.25f,y-r*.05f+bob,r*.08f,p); c.drawCircle(x+r*.25f,y-r*.05f+bob,r*.08f,p); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(2); c.drawArc(new RectF(x-r*.30f,y-r*.05f+bob,x+r*.30f,y+r*.45f+bob),15,150,false,p); p.setStyle(Paint.Style.FILL); postInvalidateDelayed(90);
        }
        private void button(Canvas c,RectF r,String s,int color){ box(c,r,Color.rgb(239,244,233),17); text(c,s,r.centerX(),r.centerY()+7,20,color,true,Paint.Align.CENTER); }
        private void box(Canvas c,RectF r,int color,float rad){ p.setColor(color); p.setStyle(Paint.Style.FILL); c.drawRoundRect(r,rad,rad,p); }
        private void text(Canvas c,String s,float x,float y,float sz,int color,boolean bold){ text(c,s,x,y,sz,color,bold,Paint.Align.LEFT); }
        private void text(Canvas c,String s,float x,float y,float sz,int color,boolean bold,Paint.Align align){ p.setColor(color); p.setTextSize(sz*getResources().getDisplayMetrics().scaledDensity); p.setTypeface(Typeface.create("sans-serif-rounded",bold?Typeface.BOLD:Typeface.NORMAL)); p.setTextAlign(align); c.drawText(s,x,y,p); }

        @Override public boolean onTouchEvent(MotionEvent e){
            if(e.getAction()!=MotionEvent.ACTION_UP)return true;
            float x=e.getX(),y=e.getY(); touchX=x;touchY=y;
            if(screen==0){
                for(int i=0;i<3;i++) if(cards[i].contains(x,y)){ selected=i; if(i==2)variant=0; invalidate(); return true; }
                if(varA.contains(x,y)){variant=0;invalidate();return true;} if(varB.contains(x,y)){variant=selected==2?0:1;invalidate();return true;}
                if(selected>=0&&start.contains(x,y)){screen=1;invalidate();} return true;
            }
            int pa=currentPar(); int st=getStroke(player,hole,pa), pt=getPutt(player,hole);
            if(minus.contains(x,y)){setStroke(player,hole,Math.max(1,st-1));}
            else if(plus.contains(x,y)){setStroke(player,hole,st+1);}
            else if(pm.contains(x,y)){setPutt(player,hole,Math.max(0,pt-1));}
            else if(pp.contains(x,y)){setPutt(player,hole,pt+1);}
            else if(mapLaunch.contains(x,y)){launchMap();return true;}
            else if(gpsSettings.contains(x,y)){launchGpsSettings();return true;}
            else {
                for(int i=0;i<4;i++) if(playerTabs[i].contains(x,y)){player=i;invalidate();return true;}
                if(prev.contains(x,y)){hole=Math.max(1,hole-1);} else if(next.contains(x,y)){hole=Math.min(18,hole+1);} else if(mapTab.contains(x,y)){screen=1;} else if(score.contains(x,y)){screen=2;}
            }
            invalidate(); return true;
        }
    }
}
