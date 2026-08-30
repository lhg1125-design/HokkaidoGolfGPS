package com.vwid.hvacbridge;
import android.content.*;
public class BootReceiver extends BroadcastReceiver {
    public void onReceive(Context c,Intent i){
        if(c.getSharedPreferences("hvac",0).getBoolean("file_autostart",false)){
            Intent s=new Intent(c,FileMcuService.class);
            if(android.os.Build.VERSION.SDK_INT>=26)c.startForegroundService(s); else c.startService(s);
        }
    }
}
