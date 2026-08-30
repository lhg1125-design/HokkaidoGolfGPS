package com.vwid.hvacbridge;

import android.content.Context;
import android.content.SharedPreferences;
import java.util.Locale;

public final class HvacState {
    public float tempL=22f, tempR=24f;
    public int fan=0, ventL=0, ventR=0, airMode=0;
    public boolean auto=false, ac=false, dual=false, power=false;

    public static HvacState fromFrame(String raw) {
        String[] ss=raw.trim().replace(","," ").split("\\s+");
        if (ss.length<9) throw new IllegalArgumentException("need 9 bytes");
        int[] b=new int[9];
        for(int i=0;i<9;i++) b[i]=Integer.parseInt(ss[i],16)&0xff;
        if(b[0]!=0x2e||b[1]!=0x21||b[2]!=0x05) throw new IllegalArgumentException("not 2E 21 05");
        int sum=0; for(int v:b) sum+=v; if((sum&0xff)!=0x2d) throw new IllegalArgumentException("checksum");
        HvacState s=new HvacState();
        int status=b[3], af=b[4], seat=b[7];
        s.power=(status&0x80)!=0;
        s.ac=s.power && (status&0x40)!=0;
        s.dual=s.power && (status&0x04)!=0;
        s.auto=s.power && (status&0x18)!=0;
        s.fan=Math.min(7,af&0x0f); s.airMode=af&0xf0;
        s.tempL=(b[5]+35)/2f; s.tempR=(b[6]+35)/2f;
        s.ventL=Math.min(3,(seat>>4)&0x0f); s.ventR=Math.min(3,seat&0x0f);
        return s;
    }

    public void save(Context c) {
        SharedPreferences p=c.getSharedPreferences("hvac",0);
        p.edit().putFloat("tl",tempL).putFloat("tr",tempR).putInt("fan",fan).putInt("vl",ventL).putInt("vr",ventR)
            .putInt("air",airMode).putBoolean("auto",auto).putBoolean("ac",ac).putBoolean("dual",dual).putBoolean("power",power).apply();
    }
    public static HvacState load(Context c){
        SharedPreferences p=c.getSharedPreferences("hvac",0); HvacState s=new HvacState();
        s.tempL=p.getFloat("tl",22f); s.tempR=p.getFloat("tr",24f); s.fan=p.getInt("fan",0); s.ventL=p.getInt("vl",0); s.ventR=p.getInt("vr",0);
        s.airMode=p.getInt("air",0); s.auto=p.getBoolean("auto",false); s.ac=p.getBoolean("ac",false); s.dual=p.getBoolean("dual",false); s.power=p.getBoolean("power",false); return s;
    }
    public static String fmtTemp(float t){ return Math.abs(t-Math.round(t))<0.01f ? String.format(Locale.US,"%d°",Math.round(t)) : String.format(Locale.US,"%.1f°",t); }
}
