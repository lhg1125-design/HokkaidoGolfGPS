package com.hokkaidogolf.trip;

import android.content.ClipData;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.location.Location;
import android.net.Uri;

import org.json.JSONObject;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Map;

/** Persistent on-device round logger. Each line is one standalone JSON object. */
public final class RoundLogV1134 {
    private static final String PREF = "round_log_v1134";
    private static final String KEY_FILE = "current_file";
    private static final long NEW_SESSION_AFTER_MS = 12L * 60L * 60L * 1000L;

    private RoundLogV1134() {}

    private static File dir(Context c) {
        File d = new File(c.getFilesDir(), "roundlogs");
        if (!d.exists()) d.mkdirs();
        return d;
    }

    public static synchronized File currentFile(Context c) {
        SharedPreferences p = c.getSharedPreferences(PREF, Context.MODE_PRIVATE);
        String name = p.getString(KEY_FILE, "");
        File f = name.isEmpty() ? null : new File(dir(c), name);
        long now = System.currentTimeMillis();
        if (f == null || !f.exists() || now - f.lastModified() > NEW_SESSION_AFTER_MS) {
            String ts = new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date(now));
            name = "HokkaidoGolfGPS-round-" + ts + ".jsonl";
            f = new File(dir(c), name);
            p.edit().putString(KEY_FILE, name).apply();
            JSONObject meta = new JSONObject();
            try {
                meta.put("type", "meta");
                meta.put("schema", "HokkaidoGolfGPS.RoundLog.v1");
                meta.put("createdAt", now);
                meta.put("version", "1.13.4-round-log");
                meta.put("note", "Precise GPS coordinates included");
            } catch (Exception ignored) {}
            appendLine(f, meta.toString());
        }
        return f;
    }

    private static void appendLine(File f, String line) {
        try (BufferedWriter w = new BufferedWriter(new FileWriter(f, true))) {
            w.write(line);
            w.newLine();
        } catch (Exception ignored) {}
    }

    public static synchronized void sample(Context c, int course, int variant, int hole, int par,
                                           int totalM, int remainM, float progress, float crossTrackM,
                                           Location l, boolean preview) {
        if (l == null) return;
        JSONObject o = new JSONObject();
        try {
            long now = System.currentTimeMillis();
            o.put("type", "gps");
            o.put("ts", now);
            o.put("fixTs", l.getTime());
            o.put("fixAgeMs", l.getTime() > 0 ? Math.max(0, now - l.getTime()) : -1);
            o.put("course", course);
            o.put("variant", variant);
            o.put("hole", hole);
            o.put("par", par);
            o.put("lat", l.getLatitude());
            o.put("lon", l.getLongitude());
            o.put("accuracyM", l.hasAccuracy() ? l.getAccuracy() : -1);
            if (l.hasAltitude()) o.put("altitudeM", l.getAltitude());
            if (l.hasSpeed()) o.put("speedMps", l.getSpeed());
            if (l.hasBearing()) o.put("bearingDeg", l.getBearing());
            o.put("totalM", totalM);
            o.put("remainM", remainM);
            o.put("progress", progress);
            o.put("crossTrackM", crossTrackM);
            o.put("preview", preview);
        } catch (Exception ignored) {}
        appendLine(currentFile(c), o.toString());
    }

    public static synchronized void event(Context c, String event, int course, int variant, int hole,
                                          Location l, String detail) {
        JSONObject o = new JSONObject();
        try {
            o.put("type", "event");
            o.put("ts", System.currentTimeMillis());
            o.put("event", event);
            o.put("course", course);
            o.put("variant", variant);
            o.put("hole", hole);
            o.put("detail", detail == null ? "" : detail);
            if (l != null) {
                o.put("lat", l.getLatitude());
                o.put("lon", l.getLongitude());
                o.put("accuracyM", l.hasAccuracy() ? l.getAccuracy() : -1);
            }
        } catch (Exception ignored) {}
        appendLine(currentFile(c), o.toString());
    }

    private static JSONObject prefsJson(SharedPreferences p) {
        JSONObject o = new JSONObject();
        try {
            for (Map.Entry<String, ?> e : p.getAll().entrySet()) {
                Object v = e.getValue();
                if (v instanceof Number || v instanceof Boolean || v instanceof String) o.put(e.getKey(), v);
            }
        } catch (Exception ignored) {}
        return o;
    }

    private static synchronized void appendSnapshot(Context c) {
        JSONObject o = new JSONObject();
        try {
            o.put("type", "snapshot");
            o.put("ts", System.currentTimeMillis());
            o.put("scores", prefsJson(c.getSharedPreferences("score_v09", Context.MODE_PRIVATE)));
            o.put("calibration", prefsJson(c.getSharedPreferences("cal_v09", Context.MODE_PRIVATE)));
            o.put("state", prefsJson(c.getSharedPreferences("state_v09", Context.MODE_PRIVATE)));
        } catch (Exception ignored) {}
        appendLine(currentFile(c), o.toString());
    }

    public static synchronized void share(Context c) {
        appendSnapshot(c);
        File f = currentFile(c);
        Uri uri = Uri.parse("content://" + c.getPackageName() + ".roundlog/current");
        Intent send = new Intent(Intent.ACTION_SEND);
        send.setType("application/x-ndjson");
        send.putExtra(Intent.EXTRA_SUBJECT, "HokkaidoGolfGPS ROUND LOG");
        send.putExtra(Intent.EXTRA_TEXT, "라운드 GPS 로그 · " + f.getName());
        send.putExtra(Intent.EXTRA_STREAM, uri);
        send.setClipData(ClipData.newRawUri("ROUND LOG", uri));
        send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        Intent chooser = Intent.createChooser(send, "ROUND LOG 공유");
        chooser.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
        c.startActivity(chooser);
    }
}
