package com.vwid.hvacbridge;

import android.app.*;
import android.content.*;
import android.os.*;
import java.lang.reflect.*;
import java.util.Locale;

public class TwUtilMcuService extends Service {
    private static final int NOTIFY_ID = 2155;
    private static final String CH = "hvac_live";
    private static final String HANDLER_TAG = "VWIDHVAC";

    private Object tw;
    private Class<?> twClass;
    private Method mWrite3, mRemoveHandler, mStop, mClose;
    private boolean active;

    private long msgCount, rxDebugCount, hvacCount;
    private final byte[] stream = new byte[8192];
    private int streamLen = 0;

    private int heatLatchL = 0, heatLatchR = 0;
    private int lastStatus = -1, lastModeFan = -1, lastTempL = -1, lastTempR = -1;
    private int lastSeatRaw = -1;
    private boolean lastCoreValid = false;

    private final Handler mcuHandler = new Handler(Looper.getMainLooper()) {
        @Override public void handleMessage(Message msg) {
            msgCount++;
            prefs().edit()
                .putLong("live_msg_count", msgCount)
                .putInt("live_last_what", msg.what)
                .apply();

            if (msg.what != 0x50D || !(msg.obj instanceof byte[])) return;

            byte[] raw = (byte[]) msg.obj;
            if (raw.length < 2) return;

            int kind = raw[0] & 0xFF;
            prefs().edit()
                .putInt("live_debug_kind", kind)
                .putString("live_last_debug", hex(raw, 0, Math.min(raw.length, 160)))
                .apply();

            // Factory MCUdebug mapping:
            // kind=1 RX, kind=2 TX, kind=3 String.
            if (kind == 1) {
                rxDebugCount++;
                prefs().edit().putLong("live_rx_count", rxDebugCount).apply();
                feed(raw, 1, raw.length - 1);
            }
        }
    };

    @Override public void onCreate() {
        super.onCreate();

        SharedPreferences p = prefs();
        long last = p.getLong("live_last_update_ms", 0L);
        long age = last == 0L ? Long.MAX_VALUE : (System.currentTimeMillis() - last);
        if (age >= 0 && age < 600000L) {
            heatLatchL = p.getInt("heat_latch_l", p.getInt("hl", 0));
            heatLatchR = p.getInt("heat_latch_r", p.getInt("hr", 0));
        } else {
            heatLatchL = 0;
            heatLatchR = 0;
        }

        createNotification();
        setStatus("STARTING");
        connectTwUtil();
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    private void createNotification() {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel nc = new NotificationChannel(
                CH, "VWID HVAC Live MCU", NotificationManager.IMPORTANCE_MIN);
            getSystemService(NotificationManager.class).createNotificationChannel(nc);
        }
        Notification.Builder b = Build.VERSION.SDK_INT >= 26
            ? new Notification.Builder(this, CH)
            : new Notification.Builder(this);
        startForeground(NOTIFY_ID, b
            .setSmallIcon(android.R.drawable.stat_notify_sync_noanim)
            .setContentTitle("VWID HVAC Bridge R5.10")
            .setContentText("Ownice MCU live bridge")
            .build());
    }

    private void connectTwUtil() {
        try {
            twClass = Class.forName("android.tw.john.TWUtil");
            setStatus("TWUtil CLASS OK");

            Constructor<?> ctor;
            try {
                ctor = twClass.getDeclaredConstructor(int.class);
                ctor.setAccessible(true);
                tw = ctor.newInstance(0x11);
            } catch (NoSuchMethodException e) {
                ctor = twClass.getDeclaredConstructor();
                ctor.setAccessible(true);
                tw = ctor.newInstance();
            }

            short[] events = new short[] {
                (short)0x0102, (short)0x0103, (short)0x0104,
                (short)0x0106, (short)0x0108, (short)0x0109,
                (short)0x010A, (short)0x010B, (short)0x0110,
                (short)0x0112, (short)0x050D, (short)0x0603,
                (short)0x0605
            };

            Method open = twClass.getMethod("open", short[].class);
            Object rcObj = open.invoke(tw, (Object) events);
            int rc = rcObj instanceof Number ? ((Number)rcObj).intValue() : 0;
            prefs().edit().putInt("live_open_rc", rc).apply();
            if (rc != 0) throw new IllegalStateException("TWUtil.open rc=" + rc);

            Method start = twClass.getMethod("start");
            start.invoke(tw);

            Method addHandler = twClass.getMethod(
                "addHandler", String.class, Handler.class);
            addHandler.invoke(tw, HANDLER_TAG, mcuHandler);

            mWrite3 = twClass.getMethod(
                "write", int.class, int.class, int.class);
            mRemoveHandler = twClass.getMethod("removeHandler", String.class);
            mStop = twClass.getMethod("stop");
            mClose = twClass.getMethod("close");

            // Exact factory MCUdebug command: RX debug ON.
            Object wr = mWrite3.invoke(tw, 0x050D, 1, 1);
            prefs().edit().putString("live_rx_enable_rc", String.valueOf(wr)).apply();

            // Harmless MCU version query used by the factory debug service.
            try {
                Method write2 = twClass.getMethod("write", int.class, int.class);
                write2.invoke(tw, 0x010A, 0x00FF);
            } catch (Throwable ignored) {}

            active = true;
            setStatus("LIVE ACTIVE - WAITING MCU RX");
        } catch (Throwable e) {
            active = false;
            setError(e);
        }
    }

    private void feed(byte[] b, int off, int len) {
        if (len <= 0) return;

        if (len > stream.length) {
            off += len - stream.length;
            len = stream.length;
        }
        if (streamLen + len > stream.length) {
            int keep = Math.min(streamLen, 512);
            System.arraycopy(stream, streamLen - keep, stream, 0, keep);
            streamLen = keep;
        }
        System.arraycopy(b, off, stream, streamLen, len);
        streamLen += len;

        parseStream();
    }

    private void parseStream() {
        while (streamLen >= 4) {
            int start = 0;
            while (start < streamLen && (stream[start] & 0xFF) != 0x2E) start++;
            if (start > 0) removePrefix(start);
            if (streamLen < 4) return;

            int dataLen = stream[2] & 0xFF;
            int total = dataLen + 4;
            if (dataLen > 96 || total < 5) {
                removePrefix(1);
                continue;
            }
            if (streamLen < total) return;

            int sum = 0;
            for (int i=0;i<total;i++) sum += stream[i] & 0xFF;
            if ((sum & 0xFF) != 0x2D) {
                removePrefix(1);
                continue;
            }

            int cmd = stream[1] & 0xFF;
            if (cmd == 0x21 && dataLen == 0x05 && total == 9) {
                String f = hex(stream, 0, total);
                try {
                    HvacState s = HvacState.fromFrame(f);

                    int status = stream[3] & 0xFF;
                    int modeFan = stream[4] & 0xFF;
                    int tempL = stream[5] & 0xFF;
                    int tempR = stream[6] & 0xFF;
                    int seatRaw = stream[7] & 0xFF;
                    int rawL = (seatRaw >> 4) & 0x0F;
                    int rawR = seatRaw & 0x0F;

                    boolean coreSame = lastCoreValid
                        && status == lastStatus
                        && modeFan == lastModeFan
                        && tempL == lastTempL
                        && tempR == lastTempR;

                    int prevRawL = lastSeatRaw < 0 ? -1 : ((lastSeatRaw >> 4) & 0x0F);
                    int prevRawR = lastSeatRaw < 0 ? -1 : (lastSeatRaw & 0x0F);

                    String reasonL = "hold";
                    String reasonR = "hold";

                    if (rawL >= 1 && rawL <= 3) {
                        heatLatchL = rawL;
                        reasonL = "level";
                    } else if (rawL == 0 && coreSame && prevRawL >= 1 && prevRawL <= 3) {
                        heatLatchL = 0;
                        reasonL = "explicit-off";
                    }

                    if (rawR >= 1 && rawR <= 3) {
                        heatLatchR = rawR;
                        reasonR = "level";
                    } else if (rawR == 0 && coreSame && prevRawR >= 1 && prevRawR <= 3) {
                        heatLatchR = 0;
                        reasonR = "explicit-off";
                    }

                    s.heatL = heatLatchL;
                    s.heatR = heatLatchR;
                    s.save(this);
                    HvacWidgetBase.updateAll(this);

                    hvacCount++;
                    prefs().edit()
                        .putLong("live_hvac_count", hvacCount)
                        .putString("live_last_hvac", f)
                        .putLong("live_last_update_ms", System.currentTimeMillis())
                        .putInt("heat_raw_d5", seatRaw)
                        .putInt("heat_latch_l", heatLatchL)
                        .putInt("heat_latch_r", heatLatchR)
                        .putString("heat_latch_reason_l", reasonL)
                        .putString("heat_latch_reason_r", reasonR)
                        .apply();

                    lastStatus = status;
                    lastModeFan = modeFan;
                    lastTempL = tempL;
                    lastTempR = tempR;
                    lastSeatRaw = seatRaw;
                    lastCoreValid = true;

                    setStatus("LIVE HVAC DATA OK");
                } catch (Throwable e) {
                    prefs().edit().putString("live_parse_error", e.toString()).apply();
                }
            }
            removePrefix(total);
        }
    }

    private void removePrefix(int n) {
        if (n <= 0) return;
        if (n >= streamLen) {
            streamLen = 0;
            return;
        }
        System.arraycopy(stream, n, stream, 0, streamLen - n);
        streamLen -= n;
    }

    private SharedPreferences prefs() {
        return getSharedPreferences("hvac", 0);
    }

    private void setStatus(String s) {
        prefs().edit().putString("live_status", s).apply();
    }

    private void setError(Throwable e) {
        String msg = e.getClass().getName() + ": " + String.valueOf(e.getMessage());
        prefs().edit()
            .putString("live_status", "ERROR")
            .putString("live_error", msg)
            .apply();
        android.util.Log.e("VWID-HVAC", "TWUtil bridge failed", e);
    }

    private static String hex(byte[] b, int off, int len) {
        StringBuilder s = new StringBuilder(len * 3);
        for (int i=0;i<len;i++) {
            if (i>0) s.append(' ');
            s.append(String.format(Locale.US, "%02x", b[off+i] & 0xFF));
        }
        return s.toString();
    }

    @Override public void onDestroy() {
        try {
            if (tw != null && mWrite3 != null) {
                // Exact factory command: RX debug OFF.
                mWrite3.invoke(tw, 0x050D, 1, 0);
            }
        } catch (Throwable ignored) {}
        try {
            if (tw != null && mRemoveHandler != null)
                mRemoveHandler.invoke(tw, HANDLER_TAG);
        } catch (Throwable ignored) {}
        try {
            if (tw != null && mStop != null) mStop.invoke(tw);
        } catch (Throwable ignored) {}
        try {
            if (tw != null && mClose != null) mClose.invoke(tw);
        } catch (Throwable ignored) {}

        active = false;
        setStatus("STOPPED");
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) {
        return null;
    }
}
