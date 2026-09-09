package com.vwid.accollector;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.zip.*;

final class CallerCollector {
    private static final long MAX_APK = 120L * 1024 * 1024;
    private static final long MAX_DEX = 40L * 1024 * 1024;
    private static final String[] STRONG = {
        "sendExtendedInterfaFunction",
        "ITWCommandAidl",
        "com.tw.service.xt.CommandService",
        "com/tw/service/xt/aidl/ITWCommandAidl",
        "PROJECT_AIR",
        "SpeechCommandService->sendBundleFunction"
    };
    private static final String[] CONTEXT = {
        "project", "air", "data0", "data1", "dateType", "extendedInterface"
    };

    private CallerCollector() {}

    static JSONObject collect(Context context, ZipOutputStream out, PackageCollector.Progress progress) throws Exception {
        PackageManager pm = context.getPackageManager();
        JSONObject report = new JSONObject();
        report.put("strategy", "READ_ONLY_INSTALLED_CALLER_SCAN");
        report.put("goal", "Find installed APK code that calls the exported HVAC command bridge and may reveal data0/data1 meaning");
        JSONArray scanned = new JSONArray();
        JSONArray matches = new JSONArray();
        report.put("matches", matches);
        int packageCount = 0;
        int dexCount = 0;

        List<PackageInfo> all;
        try { all = pm.getInstalledPackages(0); }
        catch (Throwable e) { all = Collections.emptyList(); report.put("package_query_error", String.valueOf(e)); }
        Collections.sort(all, (a,b) -> String.valueOf(a.packageName).compareTo(String.valueOf(b.packageName)));

        for (PackageInfo p : all) {
            if (p == null || p.packageName == null || p.applicationInfo == null) continue;
            packageCount++;
            String pkg = p.packageName;
            if (pkg.equals(context.getPackageName())) continue;
            ArrayList<String> paths = new ArrayList<>();
            if (p.applicationInfo.sourceDir != null) paths.add(p.applicationInfo.sourceDir);
            if (p.applicationInfo.splitSourceDirs != null) Collections.addAll(paths, p.applicationInfo.splitSourceDirs);
            if (paths.isEmpty()) continue;

            JSONObject packageMatch = null;
            JSONArray dexMatches = null;
            for (String path : paths) {
                File apk = new File(path);
                if (!apk.isFile() || apk.length() > MAX_APK) continue;
                try (ZipFile zip = new ZipFile(apk)) {
                    Enumeration<? extends ZipEntry> entries = zip.entries();
                    while (entries.hasMoreElements()) {
                        ZipEntry e = entries.nextElement();
                        if (!e.getName().matches("classes(\\d*)\\.dex")) continue;
                        dexCount++;
                        long size = e.getSize();
                        if (size < 0 || size > MAX_DEX) continue;
                        progress.update("CALLER 검색: " + pkg + " / " + e.getName());
                        byte[] data = readLimited(zip.getInputStream(e), MAX_DEX);
                        ArrayList<String> strongHits = hits(data, STRONG);
                        ArrayList<String> contextHits = hits(data, CONTEXT);
                        boolean contextQuad = contextHits.contains("project") && contextHits.contains("air") && contextHits.contains("data0") && contextHits.contains("data1");
                        if (strongHits.isEmpty() && !contextQuad) continue;

                        if (packageMatch == null) {
                            packageMatch = new JSONObject();
                            packageMatch.put("package", pkg);
                            packageMatch.put("version_name", p.versionName == null ? "" : p.versionName);
                            packageMatch.put("source_path", p.applicationInfo.sourceDir == null ? "" : p.applicationInfo.sourceDir);
                            packageMatch.put("system_app", (p.applicationInfo.flags & ApplicationInfo.FLAG_SYSTEM) != 0);
                            dexMatches = new JSONArray();
                            packageMatch.put("dex", dexMatches);
                            matches.put(packageMatch);
                        }

                        JSONObject dm = new JSONObject();
                        dm.put("entry", e.getName());
                        dm.put("bytes", data.length);
                        dm.put("strong_hits", new JSONArray(strongHits));
                        dm.put("context_hits", new JSONArray(contextHits));
                        String safePkg = safe(pkg);
                        String dest = "caller_dex/" + safePkg + "/" + safe(e.getName());
                        dm.put("archive_path", dest);
                        dexMatches.put(dm);
                        putBytes(out, dest, data);
                    }
                } catch (Throwable ex) {
                    // Per-package read failures are non-fatal and no process/service is invoked.
                }
            }
        }
        report.put("installed_packages_scanned", packageCount);
        report.put("dex_entries_scanned", dexCount);
        report.put("match_count", matches.length());
        putText(out, "caller_scan_report.json", report.toString(2));
        return report;
    }

    private static ArrayList<String> hits(byte[] data, String[] markers) {
        ArrayList<String> out = new ArrayList<>();
        for (String marker : markers) {
            if (contains(data, marker.getBytes(StandardCharsets.UTF_8))) out.add(marker);
        }
        return out;
    }

    private static boolean contains(byte[] data, byte[] pattern) {
        if (pattern.length == 0 || data.length < pattern.length) return false;
        outer: for (int i=0; i<=data.length-pattern.length; i++) {
            for (int j=0; j<pattern.length; j++) if (data[i+j] != pattern[j]) continue outer;
            return true;
        }
        return false;
    }

    private static byte[] readLimited(InputStream input, long max) throws IOException {
        try (InputStream in = new BufferedInputStream(input); ByteArrayOutputStream b = new ByteArrayOutputStream()) {
            byte[] buf = new byte[65536];
            long count = 0;
            int n;
            while ((n = in.read(buf)) != -1) {
                count += n;
                if (count > max) throw new IOException("DEX exceeds scan limit");
                b.write(buf, 0, n);
            }
            return b.toByteArray();
        }
    }

    private static String safe(String s) { return s.replaceAll("[^A-Za-z0-9._-]", "_"); }
    private static void putBytes(ZipOutputStream zip, String name, byte[] data) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(data);
        zip.closeEntry();
    }
    private static void putText(ZipOutputStream zip, String name, String text) throws IOException {
        putBytes(zip, name, text.getBytes(StandardCharsets.UTF_8));
    }
}
