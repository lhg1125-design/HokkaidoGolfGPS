package com.vwid.hvacbridge;

import android.content.*;

public class BootReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context c, Intent i) {
        android.content.SharedPreferences p=HvacStore.prefs(c);
        String action=i==null?"":String.valueOf(i.getAction());

        p.edit()
            .putString("boot_event",action)
            .putLong("boot_receiver_ms",System.currentTimeMillis())
            .apply();

        if(p.getBoolean("snapshot_valid",false)) {
            p.edit().putString("sync_source","CACHE_BOOT").apply();
            try {
                HvacWidgetBase.updateAll(c);
            } catch(Throwable e) {
                p.edit().putString("boot_widget_error",e.toString()).apply();
            }
        }

        if(!p.getBoolean("live_autostart",false)) return;

        Intent s=new Intent(c,TwUtilMcuService.class);
        if(android.os.Build.VERSION.SDK_INT>=26) c.startForegroundService(s);
        else c.startService(s);
    }
}
