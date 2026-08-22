package com.hokkaidogolf.trip;

import android.Manifest;
import android.app.Activity;
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
import android.location.LocationManager;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Toast;

public class V117HomeActivity extends Activity {
    private HomeView homeView;
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(44,171,226));
        getWindow().setNavigationBarColor(Color.rgb(51,76,31));
        homeView=new HomeView();
        setContentView(homeView);
    }
    @Override protected void onResume(){ super.onResume(); if(homeView!=null) homeView.invalidate(); }

    private final class HomeView extends View {
        private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        private final RectF[] cards={new RectF(),new RectF(),new RectF(),new RectF(),new RectF()};
        private final RectF[] nav={new RectF(),new RectF(),new RectF()};
        private final int NAVY=Color.rgb(16,46,72), GREEN=Color.rgb(0,151,75), CREAM=Color.rgb(255,251,230);
        private final String[] titles={"골프장 선택","플레이어 정보","참여 방식 선택","코드 입력 / 방 생성","라운드 시작"};
        private final int[] colors={Color.rgb(0,161,73),Color.rgb(255,112,8),Color.rgb(45,119,238),Color.rgb(139,66,226),Color.rgb(0,157,80)};
        private final String[] marks={"●","●","●","◆","▶"};
        private final SharedPreferences flow=getSharedPreferences("v117_flow",MODE_PRIVATE);

        HomeView(){ super(V117HomeActivity.this); setLayerType(View.LAYER_TYPE_SOFTWARE,null); }

        private String subFor(int i){
            if(i==0){ String s=flow.getString("course_name",""); return s.isEmpty()?"플레이할 골프장을 선택하세요":"선택됨 · "+s; }
            if(i==1){ int n=flow.getInt("player_count",0); return n>0?"플레이어 "+n+"명 저장됨":"플레이어 정보를 입력하세요"; }
            if(i==2){ String m=flow.getString("mode",""); return m.isEmpty()?"MASTER / FOLLOWER / GALLERY":"선택됨 · "+m; }
            if(i==3){ String c=flow.getString("room_code",""); return c.isEmpty()?"방 코드 입력 또는 새 방을 생성하세요":"ROOM CODE · "+c; }
            return "모든 준비가 완료되면 시작합니다";
        }

        @Override protected void onDraw(Canvas c){
            float w=getWidth(),h=getHeight();
            p.setShader(new LinearGradient(0,0,0,h,Color.rgb(47,184,239),Color.rgb(117,181,48),Shader.TileMode.CLAMP));
            c.drawRect(0,0,w,h,p); p.setShader(null);
            drawScenery(c,w,h); drawTitle(c,w,h);

            float left=w*.055f,right=w*.945f,top=h*.355f,cardH=h*.083f,gap=h*.010f;
            for(int i=0;i<5;i++){
                float y=top+i*(cardH+gap); cards[i].set(left,y,right,y+cardH);
                p.setShadowLayer(8,0,4,Color.argb(55,55,62,28)); p.setColor(Color.argb(244,255,252,228));
                c.drawRoundRect(cards[i],w*.035f,w*.035f,p); p.clearShadowLayer();
                float cx=left+w*.085f,cy=y+cardH/2,r=w*.055f;
                p.setColor(colors[i]); c.drawCircle(cx,cy,r,p);
                text(c,marks[i],cx,cy+w*.016f,w*.050f,Color.WHITE,true,Paint.Align.CENTER);
                text(c,titles[i],left+w*.18f,y+cardH*.43f,w*.049f,NAVY,true,Paint.Align.LEFT);
                text(c,subFor(i),left+w*.18f,y+cardH*.72f,w*.027f,Color.rgb(76,79,63),false,Paint.Align.LEFT);
                if(i>0) text(c,"›",right-w*.045f,cy+w*.018f,w*.070f,Color.rgb(125,119,92),false,Paint.Align.CENTER);
                if(i==0) drawTinyFlag(c,right-w*.12f,cy,w*.075f);
                if(i==1) mascot(c,right-w*.12f,cy,w*.047f);
                if(i==2){ mascot(c,right-w*.17f,cy,w*.039f); mascot(c,right-w*.10f,cy,w*.039f); }
            }

            float navTop=h*.845f; p.setColor(Color.rgb(104,74,37)); c.drawRect(0,navTop,w,h,p);
            String[] nt={"오프라인 지도","GPS READY","스코어 관리"}; String[] ni={"▦","◎","▤"};
            for(int i=0;i<3;i++){
                float l=w*i/3f,r=w*(i+1)/3f; nav[i].set(l,navTop,r,h);
                text(c,ni[i],(l+r)/2,navTop+h*.052f,w*.058f,CREAM,true,Paint.Align.CENTER);
                text(c,nt[i],(l+r)/2,navTop+h*.092f,w*.028f,Color.WHITE,true,Paint.Align.CENTER);
            }
            text(c,"스마트한 골프의 시작, GPS 캐디와 함께!",w/2,h*.985f,w*.025f,Color.rgb(255,236,147),false,Paint.Align.CENTER);
        }

        private void drawScenery(Canvas c,float w,float h){
            p.setColor(Color.argb(110,255,255,255)); c.drawCircle(w*.12f,h*.03f,w*.18f,p);
            Path m=new Path(); m.moveTo(0,h*.34f); m.lineTo(w*.24f,h*.21f); m.lineTo(w*.38f,h*.32f); m.lineTo(w*.56f,h*.19f); m.lineTo(w*.78f,h*.33f); m.lineTo(w,h*.23f); m.lineTo(w,h*.42f); m.lineTo(0,h*.42f); m.close();
            p.setColor(Color.rgb(96,159,100)); c.drawPath(m,p);
            Path m2=new Path(); m2.moveTo(0,h*.37f); m2.lineTo(w*.18f,h*.29f); m2.lineTo(w*.36f,h*.36f); m2.lineTo(w*.64f,h*.27f); m2.lineTo(w*.82f,h*.36f); m2.lineTo(w,h*.31f); m2.lineTo(w,h*.45f); m2.lineTo(0,h*.45f); m2.close();
            p.setColor(Color.rgb(49,128,64)); c.drawPath(m2,p);
        }

        private void drawTitle(Canvas c,float w,float h){
            drawTinyFlag(c,w*.50f,h*.045f,w*.10f);
            p.setColor(Color.rgb(255,239,181)); c.drawRoundRect(new RectF(w*.27f,h*.055f,w*.73f,h*.105f),w*.025f,w*.025f,p);
            text(c,"HOKKAIDO GOLF",w*.50f,h*.091f,w*.044f,Color.rgb(104,63,25),true,Paint.Align.CENTER);
            text(c,"北海道ゴルフ",w*.50f,h*.165f,w*.077f,Color.WHITE,true,Paint.Align.CENTER);
            text(c,"GPSキャディ",w*.50f,h*.225f,w*.071f,Color.rgb(255,214,0),true,Paint.Align.CENTER);
            text(c,"★ 오비히로 골프원정대 ★",w*.50f,h*.270f,w*.036f,Color.rgb(15,35,34),true,Paint.Align.CENTER);
            text(c,"OBIHIRO GOLF EXPEDITION",w*.50f,h*.304f,w*.030f,Color.rgb(238,255,209),true,Paint.Align.CENTER);
        }

        private void drawTinyFlag(Canvas c,float x,float y,float s){
            p.setStrokeWidth(Math.max(3,s*.06f)); p.setColor(Color.rgb(80,47,25)); c.drawLine(x,y-s*.36f,x,y+s*.33f,p);
            Path f=new Path(); f.moveTo(x,y-s*.34f); f.lineTo(x+s*.48f,y-s*.23f); f.lineTo(x,y-s*.11f); f.close(); p.setColor(Color.rgb(11,139,64)); c.drawPath(f,p);
            p.setColor(Color.rgb(235,244,215)); c.drawOval(new RectF(x-s*.45f,y+s*.28f,x+s*.45f,y+s*.48f),p);
        }

        private void mascot(Canvas c,float x,float y,float r){
            p.setColor(Color.WHITE); c.drawCircle(x,y,r,p); p.setColor(Color.rgb(18,146,71)); c.drawArc(new RectF(x-r,y-r*.95f,x+r,y+r*.25f),180,180,true,p);
            p.setColor(Color.rgb(30,30,30)); c.drawCircle(x-r*.32f,y-r*.05f,r*.08f,p); c.drawCircle(x+r*.32f,y-r*.05f,r*.08f,p);
            p.setColor(Color.rgb(255,166,162)); c.drawCircle(x-r*.53f,y+r*.20f,r*.12f,p); c.drawCircle(x+r*.53f,y+r*.20f,r*.12f,p);
        }

        private void text(Canvas c,String s,float x,float y,float size,int color,boolean bold,Paint.Align align){
            p.setShader(null); p.setColor(color); p.setTextSize(size); p.setTextAlign(align); p.setTypeface(Typeface.create("sans-serif",bold?Typeface.BOLD:Typeface.NORMAL)); c.drawText(s,x,y,p);
        }

        @Override public boolean onTouchEvent(MotionEvent e){
            if(e.getAction()!=MotionEvent.ACTION_UP) return true; float x=e.getX(),y=e.getY();
            for(int i=0;i<cards.length;i++) if(cards[i].contains(x,y)){ openCard(i); return true; }
            if(nav[0].contains(x,y)){ startActivity(new Intent(V117HomeActivity.this,OfflineMapActivity.class)); return true; }
            if(nav[1].contains(x,y)){ showGps(); return true; }
            if(nav[2].contains(x,y)){ Toast.makeText(V117HomeActivity.this,"스코어 관리는 GPS Play 화면과 연결됩니다.",Toast.LENGTH_SHORT).show(); return true; }
            return true;
        }

        private void openCard(int i){
            if(i==0) startActivity(new Intent(V117HomeActivity.this,CourseSelectActivity.class));
            else if(i==1) startActivity(new Intent(V117HomeActivity.this,PlayerSetupActivity.class));
            else if(i==2) startActivity(new Intent(V117HomeActivity.this,ModeSelectActivity.class));
            else if(i==3) startActivity(new Intent(V117HomeActivity.this,RoomActivity.class));
            else startActivity(new Intent(V117HomeActivity.this,RoundReadyActivity.class));
        }

        private void showGps(){
            boolean perm=checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED;
            LocationManager lm=(LocationManager)getSystemService(LOCATION_SERVICE); boolean enabled=false;
            try{ enabled=lm!=null && lm.isProviderEnabled(LocationManager.GPS_PROVIDER); }catch(Exception ignored){}
            Toast.makeText(V117HomeActivity.this,perm&&enabled?"GPS READY":"GPS 권한/위치 서비스를 확인하세요",Toast.LENGTH_SHORT).show();
        }
    }
}
