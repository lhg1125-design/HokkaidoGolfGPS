package com.vwid.hvacbridge;

import android.content.*;

public class BootReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context c, Intent i) {
        if (!c.getSharedPreferences("hvac",0).getBoolean("live_autostart",false)) return;
        Intent s = new Intent(c, TwUtilMcuService.class);
        if (android.os.Build.VERSION.SDK_INT >= 26) c.startForegroundService(s);
        else c.startService(s);
    }
}
