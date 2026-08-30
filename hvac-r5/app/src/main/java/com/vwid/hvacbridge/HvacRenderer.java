package com.vwid.hvacbridge;

import android.graphics.*;

public final class HvacRenderer {
    public static final int W=1280,H=96;
    public enum Theme { LIGHT_BROWN, DEEP_RED, DARK_LAVENDER }

    private static int accent(Theme t){
        switch(t){
            case DEEP_RED:return Color.rgb(185,72,58);
            case DARK_LAVENDER:return Color.rgb(124,80,151);
            default:return Color.rgb(143,91,37);
        }
    }

    public static Bitmap render(HvacState s, Theme t){
        Bitmap b=Bitmap.createBitmap(W,H,Bitmap.Config.ARGB_8888);
        Canvas c=new Canvas(b);
        c.drawColor(Color.TRANSPARENT,PorterDuff.Mode.CLEAR);

        Paint text=new Paint(Paint.ANTI_ALIAS_FLAG);
        text.setTypeface(Typeface.create("sans",Typeface.NORMAL));
        text.setTextAlign(Paint.Align.CENTER);
        text.setTextSize(20f);
        text.setColor(Color.rgb(238,238,238));

        // LOCKED temperature positions.
        drawText(c,HvacState.fmtTemp(s.tempL),129,48,text);
        drawText(c,HvacState.fmtTemp(s.tempR),1089,48,text);

        // Heated-seat indicators live BESIDE temperatures, never below them.
        // OFF = draw absolutely nothing.
        drawHeatWaves(c,82,48,s.heatL,false);
        drawHeatWaves(c,1137,48,s.heatR,true);

        drawFan(c,529,49,s.fan,accent(t));
        drawCar(c,669,48);

        // Status underline: immediate first-frame response, no debounce.
        drawStatusUnderline(c,214,264,s.auto,accent(t));
        drawStatusUnderline(c,788,838,s.ac,accent(t));
        drawStatusUnderline(c,934,984,s.dual,accent(t));

        return b;
    }

    private static void drawText(Canvas c,String txt,float x,float y,Paint p){
        Paint.FontMetrics fm=p.getFontMetrics();
        c.drawText(txt,x,y-(fm.ascent+fm.descent)/2f,p);
    }

    private static void drawStatusUnderline(Canvas c,float x1,float x2,boolean on,int color){
        if(!on) return;
        Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setColor(color);
        p.setStrokeCap(Paint.Cap.ROUND);
        p.setStrokeWidth(3.0f);
        c.drawLine(x1,76,x2,76,p);
    }

    private static void drawHeatWaves(Canvas c,int x,int y,int level,boolean mirror){
        if(level<=0) return;

        Paint glow=new Paint(Paint.ANTI_ALIAS_FLAG);
        glow.setStyle(Paint.Style.STROKE);
        glow.setStrokeCap(Paint.Cap.ROUND);
        glow.setStrokeWidth(6f);
        glow.setColor(Color.argb(38,255,92,54));

        Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeCap(Paint.Cap.ROUND);
        p.setStrokeWidth(2.5f);
        p.setColor(Color.rgb(245,82,54));

        int dir=mirror?-1:1;
        for(int i=0;i<level;i++){
            float wx=x + dir*(i*7);
            Path w=new Path();
            w.moveTo(wx,y+11);
            w.cubicTo(wx-2,y+7,wx+2,y+3,wx,y-1);
            w.cubicTo(wx-2,y-5,wx+2,y-9,wx,y-13);
            c.drawPath(w,glow);
            c.drawPath(w,p);
        }
    }

    private static Path blade(float cx,float cy,float deg){
        double a=Math.toRadians(deg);
        double b=Math.toRadians(deg+18);
        float x1=cx+9*(float)Math.cos(a), y1=cy+9*(float)Math.sin(a);
        float x2=cx+30*(float)Math.cos(b), y2=cy+30*(float)Math.sin(b);
        float x3=cx+34*(float)Math.cos(a+0.02), y3=cy+34*(float)Math.sin(a+0.02);
        float x4=cx+12*(float)Math.cos(a-0.18), y4=cy+12*(float)Math.sin(a-0.18);
        Path q=new Path();
        q.moveTo(x1,y1);
        q.quadTo(x2,y2,x3,y3);
        q.lineTo(x4,y4);
        q.close();
        return q;
    }

    private static void drawFan(Canvas c,int cx,int cy,int level,int acc){
        Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(1);
        p.setColor(Color.argb(115,72,61,50));
        c.drawCircle(cx,cy,31,p);

        for(int i=0;i<7;i++){
            boolean on=i<level;
            Path q=blade(cx,cy,-90+i*360f/7f);

            p.setStyle(Paint.Style.FILL);
            p.setColor(on?Color.argb(245,62,49,37):Color.argb(210,20,20,21));
            c.drawPath(q,p);

            p.setStyle(Paint.Style.STROKE);
            p.setStrokeWidth(1);
            p.setColor(on
                ? Color.argb(220,
                    Math.min(255,Color.red(acc)+52),
                    Math.min(255,Color.green(acc)+36),
                    Math.min(255,Color.blue(acc)+22))
                : Color.argb(80,72,70,68));
            c.drawPath(q,p);
        }

        p.setStyle(Paint.Style.FILL);
        p.setColor(Color.rgb(12,12,13));
        c.drawCircle(cx,cy,7,p);

        p.setStyle(Paint.Style.STROKE);
        p.setColor(Color.argb(180,118,96,70));
        c.drawCircle(cx,cy,7,p);

        p.setStyle(Paint.Style.FILL);
        p.setColor(acc);
        c.drawCircle(cx,cy,2,p);
    }

    private static void drawCar(Canvas c,int cx,int cy){
        Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(2);
        p.setStrokeCap(Paint.Cap.ROUND);
        p.setStrokeJoin(Paint.Join.ROUND);
        p.setColor(Color.rgb(222,225,228));

        Path q=new Path();
        q.moveTo(cx-29,cy+5);
        q.lineTo(cx-25,cy+1);
        q.lineTo(cx-16,cy-1);
        q.lineTo(cx-8,cy-8);
        q.lineTo(cx+5,cy-8);
        q.lineTo(cx+14,cy-2);
        q.lineTo(cx+24,cy);
        q.lineTo(cx+29,cy+5);
        q.lineTo(cx+28,cy+9);
        q.lineTo(cx+22,cy+10);
        q.lineTo(cx-23,cy+10);
        q.lineTo(cx-29,cy+8);
        c.drawPath(q,p);
        c.drawCircle(cx-17,cy+10,4,p);
        c.drawCircle(cx+18,cy+10,4,p);
    }
}
