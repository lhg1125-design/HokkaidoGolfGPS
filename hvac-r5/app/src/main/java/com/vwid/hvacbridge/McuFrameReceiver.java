package com.vwid.hvacbridge;

import android.content.*;

public class McuFrameReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context c,Intent i){
        try{
            HvacState s;

            if("com.vwid.hvacbridge.RAW_FRAME".equals(i.getAction())) {
                s=HvacState.fromFrame(i.getStringExtra("raw"));
            } else {
                s=HvacState.load(c);

                if(i.hasExtra("tempL")) s.tempL=i.getFloatExtra("tempL",s.tempL);
                if(i.hasExtra("tempR")) s.tempR=i.getFloatExtra("tempR",s.tempR);
                if(i.hasExtra("fan")) s.fan=i.getIntExtra("fan",s.fan);

                if(i.hasExtra("heatL")) s.heatL=i.getIntExtra("heatL",s.heatL);
                if(i.hasExtra("heatR")) s.heatR=i.getIntExtra("heatR",s.heatR);

                // backward compatibility with R5.5 diagnostic broadcasts
                if(i.hasExtra("ventL")) s.heatL=i.getIntExtra("ventL",s.heatL);
                if(i.hasExtra("ventR")) s.heatR=i.getIntExtra("ventR",s.heatR);

                if(i.hasExtra("auto")) s.auto=i.getBooleanExtra("auto",s.auto);
                if(i.hasExtra("ac")) s.ac=i.getBooleanExtra("ac",s.ac);
                if(i.hasExtra("dual")) s.dual=i.getBooleanExtra("dual",s.dual);
            }

            s.save(c);
            HvacWidgetBase.updateAll(c);
        }catch(Exception e){
            android.util.Log.e("VWID-HVAC","frame rejected",e);
        }
    }
}
