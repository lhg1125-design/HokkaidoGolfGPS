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

        Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setTypeface(Typeface.create("sans",Typeface.NORMAL));
        p.setTextAlign(Paint.Align.CENTER);
        p.setTextSize(20f);
        p.setColor(Color.rgb(238,238,238));

        drawText(c,HvacState.fmtTemp(s.tempL),129,48,p);
        drawText(c,HvacState.fmtTemp(s.tempR),1089,48,p);
        drawVent(c,129,63,s.ventL);
        drawVent(c,1089,63,s.ventR);
        drawFan(c,529,49,s.fan,accent(t));
        drawCar(c,669,48);

        Paint a=new Paint(Paint.ANTI_ALIAS_FLAG);
        a.setColor(accent(t));
        if(s.auto)c.drawRoundRect(214,75,264,78,1,1,a);
        if(s.ac)c.drawRoundRect(788,75,838,78,1,1,a);
        if(s.dual)c.drawRoundRect(934,75,984,78,1,1,a);
        return b;
    }

    private static void drawText(Canvas c,String txt,float x,float y,Paint p){
        Paint.FontMetrics fm=p.getFontMetrics();
        c.drawText(txt,x,y-(fm.ascent+fm.descent)/2f,p);
    }

    private static void drawVent(Canvas c,int x,int y,int level){
        Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(2);
        for(int i=0;i<3;i++){
            p.setColor(i<level?Color.rgb(74,188,255):Color.argb(45,40,47,55));
            RectF r=new RectF(x-8,y+i*6-2,x+8,y+i*6+5);
            c.drawArc(r,180,180,false,p);
        }
    }

    private static Path blade(float cx,float cy,float deg){
        double a=Math.toRadians(deg);
        double b=Math.toRadians(deg+18);
        float x1=cx+9*(float)Math.cos(a), y1=cy+9*(float)Math.sin(a);
        float x2=cx+30*(float)Math.cos(b), y2=cy+30*(float)Math.sin(b);
        float x3=cx+34*(float)Math.cos(a+0.02), y3=cy+34*(float)Math.sin(a+0.02);
        float x4=cx+12*(float)Math.cos(a-0.18), y4=cy+12*(float)Math.sin(a-0.18);
        Path q=new Path(); q.moveTo(x1,y1); q.quadTo(x2,y2,x3,y3); q.lineTo(x4,y4); q.close(); return q;
    }

    private static void drawFan(Canvas c,int cx,int cy,int level,int acc){
        Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(1);
        p.setColor(Color.argb(115,72,61,50)); c.drawCircle(cx,cy,31,p);
        for(int i=0;i<7;i++){
            boolean on=i<level;
            Path q=blade(cx,cy,-90+i*360f/7f);
            p.setStyle(Paint.Style.FILL);
            p.setColor(on?Color.argb(245,62,49,37):Color.argb(210,20,20,21));
            c.drawPath(q,p);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(1);
            p.setColor(on?Color.argb(220,Math.min(255,Color.red(acc)+52),Math.min(255,Color.green(acc)+36),Math.min(255,Color.blue(acc)+22)):Color.argb(80,72,70,68));
            c.drawPath(q,p);
        }
        p.setStyle(Paint.Style.FILL); p.setColor(Color.rgb(12,12,13)); c.drawCircle(cx,cy,7,p);
        p.setStyle(Paint.Style.STROKE); p.setColor(Color.argb(180,118,96,70)); c.drawCircle(cx,cy,7,p);
        p.setStyle(Paint.Style.FILL); p.setColor(acc); c.drawCircle(cx,cy,2,p);
    }

    private static void drawCar(Canvas c,int cx,int cy){
        Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(2);
        p.setStrokeCap(Paint.Cap.ROUND); p.setStrokeJoin(Paint.Join.ROUND);
        p.setColor(Color.rgb(222,225,228));
        Path q=new Path();
        q.moveTo(cx-29,cy+5); q.lineTo(cx-25,cy+1); q.lineTo(cx-16,cy-1);
        q.lineTo(cx-8,cy-8); q.lineTo(cx+5,cy-8); q.lineTo(cx+14,cy-2);
        q.lineTo(cx+24,cy); q.lineTo(cx+29,cy+5); q.lineTo(cx+28,cy+9);
        q.lineTo(cx+22,cy+10); q.lineTo(cx-23,cy+10); q.lineTo(cx-29,cy+8);
        c.drawPath(q,p); c.drawCircle(cx-17,cy+10,4,p); c.drawCircle(cx+18,cy+10,4,p);
    }
}
