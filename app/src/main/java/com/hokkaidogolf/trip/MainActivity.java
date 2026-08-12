package com.hokkaidogolf.trip;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
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
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;

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
        try { lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1500, 1.5f, this); } catch (Exception ignored) {}
    }

    @Override public void onLocationChanged(Location l) { view.setLocation(l); }
    @Override protected void onPause() { super.onPause(); try { lm.removeUpdates(this); } catch (Exception ignored) {} }
    @Override protected void onResume() { super.onResume(); startGps(); }
    @Override public void onRequestPermissionsResult(int r, String[] p, int[] g) { super.onRequestPermissionsResult(r,p,g); if (r==REQ && g.length>0 && g[0]==PackageManager.PERMISSION_GRANTED) startGps(); }

    static final class GolfView extends View {
        private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final SharedPreferences prefs;
        private final String[] jp = {"上士幌ゴルフ場","富良野ゴルフコース","サホロカントリークラブ"};
        private final String[] ko = {"가미시호로 골프장","후라노 골프코스","사호로 컨트리클럽"};
        private int selected = -1, screen = 0, hole = 1, stroke = 4, putt = 0;
        private Location location;
        private final RectF[] cards = {new RectF(),new RectF(),new RectF()};
        private final RectF start = new RectF(), minus = new RectF(), plus = new RectF(), pm = new RectF(), pp = new RectF(), prev = new RectF(), next = new RectF(), score = new RectF(), map = new RectF();
        private final int BG=Color.rgb(247,250,239), INK=Color.rgb(37,53,39), GREEN=Color.rgb(22,103,62), CARD=Color.WHITE, LIME=Color.rgb(183,225,92), SKY=Color.rgb(106,200,235), CORAL=Color.rgb(255,132,96), YELLOW=Color.rgb(255,211,72);

        GolfView(Context c) { super(c); prefs=c.getSharedPreferences("score",MODE_PRIVATE); p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL)); }
        void setLocation(Location l){ location=l; invalidate(); }

        @Override protected void onDraw(Canvas c){ super.onDraw(c); c.drawColor(BG); if(screen==0) home(c); else if(screen==1) round(c); else score(c); }

        private void home(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.055f;
            text(c,"北海道ゴルフ",m,h*.09f,31,INK,true); text(c,"GPSキャディ",m,h*.15f,43,GREEN,true);
            text(c,"8/24~26 · HOKKAIDO TRIP",m,h*.19f,12,Color.DKGRAY,true);
            text(c,"오늘 어디서 칠까요?",m,h*.25f,19,INK,true); text(c,"카트 내비 없어도 OK · 거리 단위는 m",m,h*.285f,12,Color.GRAY,false);
            float top=h*.33f,ch=h*.14f,gap=h*.022f; int[] a={LIME,YELLOW,SKY};
            for(int i=0;i<3;i++){ float y=top+i*(ch+gap); cards[i].set(m,y,w-m,y+ch); box(c,cards[i],selected==i?Color.rgb(235,248,211):CARD,28); p.setColor(a[i]); c.drawCircle(m+30,y+35,10,p); text(c,"0"+(i+1),m+53,y+42,12,GREEN,true); text(c,jp[i],m+25,y+78,20,INK,true); text(c,ko[i],m+25,y+108,12,Color.GRAY,false); }
            start.set(m,h*.84f,w-m,h*.92f); box(c,start,selected>=0?GREEN:Color.LTGRAY,38); text(c,selected>=0?"라운드 시작 →":"골프장을 먼저 선택해주세요",w/2,h*.89f,16,selected>=0?Color.WHITE:Color.DKGRAY,true,Paint.Align.CENTER);
            text(c,"GPS · 코스맵 · 스코어 · 오프라인",w/2,h*.965f,10,Color.GRAY,true,Paint.Align.CENTER);
        }

        private void round(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;
            text(c,ko[Math.max(0,selected)],m,h*.055f,14,Color.GRAY,true); text(c,"H"+hole,m,h*.12f,40,INK,true); text(c,"PAR 4",m+78,h*.115f,15,GREEN,true);
            text(c,location==null?"GPS 찾는 중…":"GPS ±"+Math.round(location.getAccuracy())+"m",w-m,h*.06f,12,location==null?CORAL:GREEN,true,Paint.Align.RIGHT);
            RectF hud=new RectF(m,h*.145f,w-m,h*.235f); box(c,hud,GREEN,28); int center=150+(hole*7)%58; metric(c,"앞",center-9,w*.21f,h*.177f); metric(c,"중앙",center,w*.50f,h*.177f); metric(c,"뒤",center+8,w*.79f,h*.177f);
            RectF course=new RectF(m,h*.255f,w-m,h*.675f); box(c,course,Color.rgb(225,242,204),34); drawCourse(c,course);
            text(c,"지도를 터치하면 타깃 거리 기능을 붙일 예정",w/2,h*.705f,11,Color.GRAY,false,Paint.Align.CENTER);
            RectF panel=new RectF(m,h*.73f,w-m,h*.86f); box(c,panel,CARD,28);
            stroke=prefs.getInt("s"+hole,4); putt=prefs.getInt("p"+hole,0);
            text(c,"타수",m+24,h*.77f,11,Color.GRAY,true); text(c,""+stroke,w*.29f,h*.825f,36,INK,true,Paint.Align.CENTER); minus.set(m+15,h*.785f,m+60,h*.845f); plus.set(w*.38f,h*.785f,w*.48f,h*.845f); button(c,minus,"−",Color.GRAY); button(c,plus,"+",GREEN);
            text(c,"퍼트",w*.58f,h*.77f,11,Color.GRAY,true); text(c,""+putt,w*.71f,h*.825f,34,INK,true,Paint.Align.CENTER); pm.set(w*.54f,h*.785f,w*.62f,h*.845f); pp.set(w*.82f,h*.785f,w*.90f,h*.845f); button(c,pm,"−",Color.GRAY); button(c,pp,"+",SKY);
            nav(c);
        }

        private void drawCourse(Canvas c,RectF r){
            p.setColor(SKY); c.drawOval(new RectF(r.left+20,r.top+r.height()*.42f,r.left+r.width()*.42f,r.bottom-20),p);
            p.setColor(Color.rgb(91,178,82)); Path f=new Path(); f.moveTo(r.centerX(),r.bottom-25); f.cubicTo(r.left+r.width()*.33f,r.top+r.height()*.72f,r.left+r.width()*.68f,r.top+r.height()*.45f,r.centerX(),r.top+30); f.lineTo(r.centerX()+52,r.top+42); f.cubicTo(r.left+r.width()*.74f,r.top+r.height()*.47f,r.left+r.width()*.50f,r.top+r.height()*.72f,r.centerX()+25,r.bottom-25); f.close(); c.drawPath(f,p);
            p.setColor(YELLOW); c.drawOval(new RectF(r.centerX()+35,r.top+r.height()*.40f,r.centerX()+85,r.top+r.height()*.47f),p);
            p.setColor(CORAL); c.drawCircle(r.centerX()+15,r.top+60,8,p); text(c,"⛳",r.centerX()+15,r.top+50,22,INK,true,Paint.Align.CENTER);
            p.setColor(Color.WHITE); c.drawCircle(r.centerX(),r.bottom-38,11,p); text(c,"YOU",r.centerX(),r.bottom-12,10,GREEN,true,Paint.Align.CENTER);
        }

        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.05f; text(c,"스코어카드",m,h*.09f,34,INK,true); text(c,"숫자는 작게, 감정은 크게 😄",m,h*.13f,12,Color.GRAY,false);
            float y=h*.19f; int total=0; for(int i=1;i<=9;i++){ int s=prefs.getInt("s"+i,4),pt=prefs.getInt("p"+i,0); total+=s; RectF r=new RectF(m,y-22,w-m,y+27); box(c,r,i==hole?Color.rgb(235,248,211):CARD,18); text(c,"H"+i,m+20,y+9,14,INK,true); text(c,"PAR 4",w*.33f,y+9,12,Color.GRAY,false,Paint.Align.CENTER); text(c,""+s,w*.62f,y+9,17,s>4?CORAL:GREEN,true,Paint.Align.CENTER); text(c,"퍼트 "+pt,w*.84f,y+9,12,SKY,true,Paint.Align.CENTER); y+=h*.066f; }
            RectF t=new RectF(m,h*.80f,w-m,h*.875f); box(c,t,GREEN,26); text(c,"OUT TOTAL",m+22,h*.846f,12,Color.WHITE,true); text(c,""+total,w-m-22,h*.85f,26,Color.WHITE,true,Paint.Align.RIGHT); nav(c);
        }

        private void nav(Canvas c){ float w=getWidth(),h=getHeight(),m=w*.045f; prev.set(m,h*.90f,w*.23f,h*.965f); map.set(w*.27f,h*.90f,w*.49f,h*.965f); score.set(w*.53f,h*.90f,w*.75f,h*.965f); next.set(w*.79f,h*.90f,w-m,h*.965f); box(c,prev,CARD,22); box(c,next,CARD,22); box(c,map,screen==1?GREEN:CARD,22); box(c,score,screen==2?GREEN:CARD,22); text(c,"‹ 이전",prev.centerX(),prev.centerY()+5,12,INK,true,Paint.Align.CENTER); text(c,"지도",map.centerX(),map.centerY()+5,12,screen==1?Color.WHITE:INK,true,Paint.Align.CENTER); text(c,"스코어",score.centerX(),score.centerY()+5,12,screen==2?Color.WHITE:INK,true,Paint.Align.CENTER); text(c,"다음 ›",next.centerX(),next.centerY()+5,12,INK,true,Paint.Align.CENTER); }
        private void metric(Canvas c,String label,int d,float x,float y){ text(c,label,x,y,10,Color.rgb(210,235,216),true,Paint.Align.CENTER); text(c,d+"m",x,y+getHeight()*.04f,22,Color.WHITE,true,Paint.Align.CENTER); }
        private void button(Canvas c,RectF r,String s,int color){ box(c,r,Color.rgb(239,244,233),18); text(c,s,r.centerX(),r.centerY()+8,22,color,true,Paint.Align.CENTER); }
        private void box(Canvas c,RectF r,int color,float rad){ p.setColor(color); p.setStyle(Paint.Style.FILL); c.drawRoundRect(r,rad,rad,p); }
        private void text(Canvas c,String s,float x,float y,float sz,int color,boolean bold){ text(c,s,x,y,sz,color,bold,Paint.Align.LEFT); }
        private void text(Canvas c,String s,float x,float y,float sz,int color,boolean bold,Paint.Align align){ p.setColor(color); p.setTextSize(sz*getResources().getDisplayMetrics().scaledDensity); p.setTypeface(Typeface.create("sans-serif-rounded",bold?Typeface.BOLD:Typeface.NORMAL)); p.setTextAlign(align); c.drawText(s,x,y,p); }

        @Override public boolean onTouchEvent(MotionEvent e){ if(e.getAction()!=MotionEvent.ACTION_UP)return true; float x=e.getX(),y=e.getY(); if(screen==0){ for(int i=0;i<3;i++)if(cards[i].contains(x,y)){selected=i;invalidate();return true;} if(selected>=0&&start.contains(x,y)){screen=1;invalidate();} return true; }
            if(minus.contains(x,y)){stroke=Math.max(1,prefs.getInt("s"+hole,4)-1);prefs.edit().putInt("s"+hole,stroke).apply();}
            else if(plus.contains(x,y)){stroke=prefs.getInt("s"+hole,4)+1;prefs.edit().putInt("s"+hole,stroke).apply();}
            else if(pm.contains(x,y)){putt=Math.max(0,prefs.getInt("p"+hole,0)-1);prefs.edit().putInt("p"+hole,putt).apply();}
            else if(pp.contains(x,y)){putt=prefs.getInt("p"+hole,0)+1;prefs.edit().putInt("p"+hole,putt).apply();}
            else if(prev.contains(x,y)){hole=Math.max(1,hole-1);} else if(next.contains(x,y)){hole=Math.min(18,hole+1);} else if(map.contains(x,y)){screen=1;} else if(score.contains(x,y)){screen=2;} invalidate(); return true; }
    }
}
