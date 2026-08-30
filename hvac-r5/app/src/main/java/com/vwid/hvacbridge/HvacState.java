package com.vwid.hvacbridge;

import android.content.Context;
import android.content.SharedPreferences;
import java.util.Locale;

public final class HvacState {
    public float tempL=22f, tempR=24f;
    public int fan=0, heatL=0, heatR=0, airMode=0, statusRaw=0;
    public boolean auto=false, ac=false, dual=false, power=false;

    public static HvacState fromFrame(String raw) {
        String[] ss=raw.trim().replace(","," ").split("\\s+");
        if (ss.length<9) throw new IllegalArgumentException("need 9 bytes");

        int[] b=new int[9];
        for(int i=0;i<9;i++) b[i]=Integer.parseInt(ss[i],16)&0xff;

        if(b[0]!=0x2e || b[1]!=0x21 || b[2]!=0x05)
            throw new IllegalArgumentException("not 2E 21 05");

        int sum=0;
        for(int v:b) sum+=v;
        if((sum&0xff)!=0x2d) throw new IllegalArgumentException("checksum");

        HvacState s=new HvacState();
        int status=b[3], af=b[4], seat=b[7];
        s.statusRaw=status;

        // CONFIRMED
        s.dual=(status&0x04)!=0;
        s.auto=(status&0x18)!=0;
        s.fan=Math.min(7,af&0x0f);
        s.tempL=(b[5]+35)/2f;
        s.tempR=(b[6]+35)/2f;

        // HVAC active indication only; not used for A/C.
        s.power = (s.fan>0) || status!=0;

        // AIR semantic mapping remains intentionally hidden.
        s.airMode=af&0xf0;

        // CONFIRMED: D5 high/low nibble = heated-seat L/R 0..3.
        int l=(seat>>4)&0x0f;
        int r=seat&0x0f;
        s.heatL=l<=3?l:0;
        s.heatR=r<=3?r:0;

        // A/C is deliberately NOT guessed from D1.
        // save(Context) applies the vehicle-calibrated mapping.
        s.ac=false;
        return s;
    }

    public void save(Context c) {
        SharedPreferences p=c.getSharedPreferences("hvac",0);

        if(p.getBoolean("ac_cal_valid",false)) {
            int mask=p.getInt("ac_mask",0)&0xff;
            int on=p.getInt("ac_on_status",0)&0xff;
            ac = mask!=0 && ((statusRaw & mask) == (on & mask));
        } else {
            ac=false;
        }

        p.edit()
            .putFloat("tl",tempL)
            .putFloat("tr",tempR)
            .putInt("fan",fan)
            .putInt("hl",heatL)
            .putInt("hr",heatR)
            .putInt("air",airMode)
            .putInt("status_raw",statusRaw)
            .putBoolean("auto",auto)
            .putBoolean("ac",ac)
            .putBoolean("dual",dual)
            .putBoolean("power",power)
            .apply();
    }

    public static HvacState load(Context c){
        SharedPreferences p=c.getSharedPreferences("hvac",0);
        HvacState s=new HvacState();

        s.tempL=p.getFloat("tl",22f);
        s.tempR=p.getFloat("tr",24f);
        s.fan=p.getInt("fan",0);
        s.heatL=p.contains("hl") ? p.getInt("hl",0) : p.getInt("vl",0);
        s.heatR=p.contains("hr") ? p.getInt("hr",0) : p.getInt("vr",0);
        s.airMode=p.getInt("air",0);
        s.statusRaw=p.getInt("status_raw",0);

        s.auto=p.getBoolean("auto",false);
        s.ac=p.getBoolean("ac",false);
        s.dual=p.getBoolean("dual",false);
        s.power=p.getBoolean("power",false);

        return s;
    }

    public static String fmtTemp(float t){
        return Math.abs(t-Math.round(t))<0.01f
            ? String.format(Locale.US,"%d°",Math.round(t))
            : String.format(Locale.US,"%.1f°",t);
    }
}
