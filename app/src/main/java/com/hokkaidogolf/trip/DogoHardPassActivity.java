package com.hokkaidogolf.trip;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

/**
 * Step-1 visual/data gate only.
 * H1-approved layout is fixed while H1..H18 OUT/IN, PAR and official Regular CENTER are data-bound.
 * FRONT/BACK stay '--' until field calibration; synthetic +/-12m is intentionally prohibited.
 */
public class DogoHardPassActivity extends Activity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(new DogoView());
    }

    private final class DogoView extends View {
        private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final DogoCourseData data;
        private final Map<Integer, Bitmap> cache = new HashMap<>();
        private int hole = 1;

        DogoView() {
            super(DogoHardPassActivity.this);
            data = DogoCourseData.load(DogoHardPassActivity.this);
            p.setTypeface(Typeface.create("sans-serif", Typeface.BOLD));
            setKeepScreenOn(true);
        }

        @Override protected void onDraw(Canvas c) {
            float w = getWidth(), h = getHeight();
            DogoCourseData.Hole m = data.hole(hole);
            c.drawColor(Color.rgb(245, 231, 197));

            // Approved H1 chrome family: navy header + wood yardage + green player card.
            p.setColor(Color.rgb(2, 27, 83)); c.drawRect(0, 0, w, h * .105f, p);
            text(c, "‹  도고CC", w*.045f, h*.046f, w*.050f, Color.WHITE, Paint.Align.LEFT);
            text(c, m.course + " · H" + m.hole + " · PAR " + m.par, w*.115f, h*.083f, w*.027f, Color.WHITE, Paint.Align.LEFT);
            text(c, "☁ 21°C    ↗ NE    3.2m/s", w*.58f, h*.044f, w*.027f, Color.WHITE, Paint.Align.LEFT);
            text(c, "▮▮▮ GPS", w*.83f, h*.082f, w*.027f, Color.rgb(124,220,45), Paint.Align.LEFT);

            RectF wood = new RectF(w*.025f,h*.106f,w*.975f,h*.205f);
            p.setColor(Color.rgb(79,40,15)); c.drawRoundRect(wood,18,18,p);
            p.setColor(Color.argb(90,255,213,140)); p.setStrokeWidth(2);
            c.drawLine(w*.34f,wood.top+18,w*.34f,wood.bottom-18,p);
            c.drawLine(w*.66f,wood.top+18,w*.66f,wood.bottom-18,p);
            metric(c,"FRONT","--",w*.18f,h*.139f);
            metric(c,"CENTER",m.regularM+"m",w*.50f,h*.139f);
            metric(c,"BACK","--",w*.82f,h*.139f);

            RectF panel = new RectF(w*.025f,h*.285f,w*.265f,h*.725f);
            p.setColor(Color.rgb(4,72,36)); c.drawRoundRect(panel,24,24,p);
            text(c,"PAR "+m.par,panel.centerX(),h*.331f,w*.040f,Color.WHITE,Paint.Align.CENTER);
            text(c,"H"+m.hole,panel.centerX(),h*.385f,w*.075f,Color.WHITE,Paint.Align.CENTER);
            player(c,panel,"회원","+3",Color.rgb(20,115,235),0);
            player(c,panel,"경집","+5",Color.rgb(20,125,55),1);
            player(c,panel,"시형","-1",Color.rgb(255,145,20),2);
            player(c,panel,"종수","+8",Color.rgb(106,45,180),3);

            RectF map = new RectF(w*.29f,h*.245f,w*.79f,h*.80f);
            drawMapAsset(c,map,m);

            // Right-side scale remains visual guide only in Step-1; no fake live distance marker.
            p.setColor(Color.rgb(60,55,46)); p.setStrokeWidth(2); c.drawLine(w*.865f,h*.34f,w*.865f,h*.735f,p);
            for(int i=0;i<=8;i++){
                float y=h*(.735f-i*.049f); c.drawLine(w*.865f,y,w*.885f,y,p);
                text(c,(i*50)+"m",w*.89f,y+w*.006f,w*.021f,Color.rgb(50,48,42),Paint.Align.LEFT);
            }
            text(c,"OFFICIAL",w*.865f,h*.795f,w*.020f,Color.rgb(100,80,50),Paint.Align.CENTER);
            text(c,"REGULAR "+m.regularM+"m",w*.865f,h*.817f,w*.020f,Color.rgb(100,80,50),Paint.Align.CENTER);

            RectF nav = new RectF(w*.025f,h*.89f,w*.975f,h*.967f);
            p.setColor(Color.rgb(0,71,63)); c.drawRoundRect(nav,30,30,p);
            String[] labels={"스코어","‹ 이전 홀","GPS 동기화","다음 홀 ›","메뉴"};
            for(int i=0;i<5;i++) text(c,labels[i],w*(.10f+i*.20f),h*.938f,w*.026f,Color.WHITE,Paint.Align.CENTER);

            text(c,"STEP 1 HARD PASS · H1 MASTER chrome lock · H"+hole+"/18",w/2,h*.985f,w*.018f,Color.DKGRAY,Paint.Align.CENTER);
        }

        private void drawMapAsset(Canvas c, RectF dst, DogoCourseData.Hole m) {
            Bitmap b = cache.get(m.hole);
            if (b == null) {
                String[] paths = {"courses/dogo_maps/"+m.mapAsset, "courses/"+m.mapAsset};
                for (String path : paths) {
                    try (InputStream in = getAssets().open(path)) { b = BitmapFactory.decodeStream(in); }
                    catch (Exception ignored) {}
                    if (b != null) break;
                }
                if (b != null) cache.put(m.hole,b);
            }
            if (b != null) {
                p.setColor(Color.WHITE); c.drawRoundRect(dst,28,28,p);
                c.save(); c.clipRect(dst); c.drawBitmap(b,null,dst,p); c.restore();
            } else {
                p.setColor(Color.rgb(223,236,197)); c.drawRoundRect(dst,28,28,p);
                text(c,"H"+m.hole+" COURSE MAP",dst.centerX(),dst.centerY()-12,getWidth()*.040f,Color.rgb(27,88,46),Paint.Align.CENTER);
                text(c,m.mapAsset,dst.centerX(),dst.centerY()+24,getWidth()*.019f,Color.DKGRAY,Paint.Align.CENTER);
                text(c,"asset package pending",dst.centerX(),dst.centerY()+52,getWidth()*.018f,Color.GRAY,Paint.Align.CENTER);
            }
        }

        private void metric(Canvas c,String label,String value,float x,float y){
            text(c,label,x,y,getWidth()*.025f,Color.WHITE,Paint.Align.CENTER);
            text(c,value,x,y+getHeight()*.042f,getWidth()*.050f,Color.WHITE,Paint.Align.CENTER);
        }

        private void player(Canvas c,RectF r,String name,String score,int dot,int idx){
            float y=r.top+r.height()*(.39f+idx*.145f);
            p.setColor(dot); c.drawCircle(r.left+r.width()*.18f,y,16,p);
            text(c,name,r.left+r.width()*.43f,y+8,getWidth()*.032f,Color.WHITE,Paint.Align.LEFT);
            text(c,score,r.left+r.width()*.63f,y+35,getWidth()*.042f,score.startsWith("-")?Color.rgb(0,100,255):Color.rgb(240,55,50),Paint.Align.LEFT);
        }

        private void text(Canvas c,String s,float x,float y,float size,int color,Paint.Align align){
            p.setTextSize(size);p.setTextAlign(align);p.setColor(color);p.setStyle(Paint.Style.FILL);c.drawText(s,x,y,p);
        }

        @Override public boolean onTouchEvent(MotionEvent e) {
            if (e.getAction()!=MotionEvent.ACTION_UP) return true;
            float x=e.getX(), w=getWidth();
            if (x<w*.43f) hole = Math.max(1,hole-1);
            else if (x>w*.57f) hole = Math.min(18,hole+1);
            invalidate();
            return true;
        }
    }
}
