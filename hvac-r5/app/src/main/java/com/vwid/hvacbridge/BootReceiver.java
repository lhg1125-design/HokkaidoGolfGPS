package com.vwid.hvacbridge;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.*;
import android.os.Build;
import android.os.SystemClock;

public class BootReceiver extends BroadcastReceiver {
    private static final String RETRY = "com.vwid.hvacbridge.START_RETRY";

    @Override public void onReceive(Context c, Intent i) {
        String action = i == null ? "UNKNOWN" : String.valueOf(i.getAction());
        startIfEnabled(c, action);
    }

    public static void startIfEnabled(Context c, String source) {
        SharedPreferences p = HvacStore.prefs(c);
        long now = System.currentTimeMillis();
        boolean enabled = p.getBoolean("live_autostart", true);
        p.edit()
            .putString("boot_event", source)
            .putLong("boot_receiver_ms", now)
            .putBoolean("boot_start_enabled", enabled)
            .apply();

        if (!enabled) {
            p.edit().putString("boot_start_result", "DISABLED_BY_USER").apply();
            return;
        }

        // Start the MCU listener before doing any expensive widget rendering.
        // No HVAC control or unverified status-request command is transmitted here.
        try {
            Intent s = new Intent(c, TwUtilMcuService.class);
            if (Build.VERSION.SDK_INT >= 26) c.startForegroundService(s);
            else c.startService(s);
            p.edit()
                .putString("boot_start_result", "SERVICE_START_REQUESTED")
                .putString("boot_start_error", "")
                .apply();
            cancelRetry(c);
        } catch (RuntimeException e) {
            p.edit()
                .putString("boot_start_result", "START_FAILED")
                .putString("boot_start_error", e.toString())
                .apply();
            scheduleRetry(c);
        }
    }

    private static PendingIntent retryIntent(Context c) {
        Intent i = new Intent(c, BootReceiver.class).setAction(RETRY);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
        return PendingIntent.getBroadcast(c, 12122, i, flags);
    }

    private static void scheduleRetry(Context c) {
        AlarmManager am = (AlarmManager)c.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;
        PendingIntent pi = retryIntent(c);
        long when = SystemClock.elapsedRealtime() + 30000L;
        if (Build.VERSION.SDK_INT >= 23)
            am.setAndAllowWhileIdle(AlarmManager.ELAPSED_REALTIME_WAKEUP, when, pi);
        else am.set(AlarmManager.ELAPSED_REALTIME_WAKEUP, when, pi);
    }

    private static void cancelRetry(Context c) {
        AlarmManager am = (AlarmManager)c.getSystemService(Context.ALARM_SERVICE);
        if (am != null) am.cancel(retryIntent(c));
    }
}
