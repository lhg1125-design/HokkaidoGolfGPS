package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Shader;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;

public class MainActivity extends Activity {
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable openHome = () -> {
        startActivity(new Intent(MainActivity.this, V117HomeActivity.class));
        finish();
    };

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(51, 176, 230));
        getWindow().setNavigationBarColor(Color.rgb(7, 70, 39));
        setContentView(new SplashView());
        handler.postDelayed(openHome, 1050);
    }

    @Override protected void onDestroy() {
        handler.removeCallbacks(openHome);
        super.onDestroy();
    }

    private final class SplashView extends View {
        private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final Bitmap icon = BitmapFactory.decodeResource(getResources(), R.drawable.ic_launcher);

        SplashView() { super(MainActivity.this); }

        @Override protected void onDraw(Canvas c) {
            float w=getWidth(), h=getHeight();
            p.setShader(new LinearGradient(0,0,0,h, Color.rgb(46,190,244), Color.rgb(43,143,72), Shader.TileMode.CLAMP));
            c.drawRect(0,0,w,h,p); p.setShader(null);

            p.setColor(Color.argb(75,255,255,255)); c.drawCircle(w*.15f,h*.08f,w*.22f,p);
            p.setColor(Color.rgb(89,171,79));
            c.drawOval(new RectF(-w*.20f,h*.65f,w*1.25f,h*1.10f),p);
            p.setColor(Color.rgb(38,121,58));
            c.drawOval(new RectF(-w*.30f,h*.76f,w*1.35f,h*1.18f),p);

            if(icon!=null){
                float s=Math.min(w*.42f,h*.24f);
                c.drawBitmap(icon,null,new RectF(w/2-s/2,h*.10f,w/2+s/2,h*.10f+s),p);
            }

            text(c,"HOKKAIDO GOLF",w/2,h*.39f,w*.058f,Color.rgb(99,61,25),true);
            text(c,"北海道ゴルフ",w/2,h*.48f,w*.100f,Color.WHITE,true);
            text(c,"GPSキャディ",w/2,h*.57f,w*.090f,Color.rgb(255,214,0),true);
            text(c,"★ 오비히로 골프원정대 ★",w/2,h*.625f,w*.042f,Color.WHITE,true);
            text(c,"OBIHIRO GOLF EXPEDITION",w/2,h*.665f,w*.036f,Color.rgb(224,255,164),true);

            p.setColor(Color.argb(130,0,0,0)); c.drawRoundRect(new RectF(w*.17f,h*.82f,w*.83f,h*.845f),20,20,p);
            p.setColor(Color.rgb(155,224,0)); c.drawRoundRect(new RectF(w*.17f,h*.82f,w*.69f,h*.845f),20,20,p);
            text(c,"로딩 중…",w/2,h*.79f,w*.036f,Color.WHITE,true);
            text(c,"GPS Caddie · v1.17 Flow",w/2,h*.90f,w*.030f,Color.WHITE,false);
        }

        private void text(Canvas c,String s,float x,float y,float size,int color,boolean bold){
            p.setShader(null); p.setColor(color); p.setTextSize(size); p.setTextAlign(Paint.Align.CENTER);
            p.setTypeface(android.graphics.Typeface.create("sans-serif",bold?android.graphics.Typeface.BOLD:android.graphics.Typeface.NORMAL));
            c.drawText(s,x,y,p);
        }
    }
}
