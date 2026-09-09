package com.vwid.accollector;

import android.content.Context;
import android.content.pm.*;
import android.os.Build;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.*;

public final class PackageCollector {
    private static final String[] TARGETS = {"com.tw.ac", "com.zht.car.accontroller"};
    private static final long MAX_APK = 100L * 1024 * 1024;
    private PackageCollector() {}

    public static final class Scan {
        public final ArrayList<String> found = new ArrayList<>();
        public final ArrayList<String> candidates = new ArrayList<>();
        public final ArrayList<String> missing = new ArrayList<>();
    }

    public interface Progress { void update(String message); }

    public static Scan scan(Context context) {
        PackageManager pm = context.getPackageManager();
        Scan result = new Scan();
        for (String name : TARGETS) {
            try { pm.getPackageInfo(name, 0); result.found.add(name); }
            catch (PackageManager.NameNotFoundException e) { result.missing.add(name); }
        }
        try {
            for (PackageInfo p : pm.getInstalledPackages(0)) {
                String n = p.packageName;
                String l = n.toLowerCase(Locale.US);
                if (!result.found.contains(n) && (l.contains("aircondition") || l.contains("accontroller") || l.contains("climate") || l.equals("com.tw.ac")))
                    result.candidates.add(n);
            }
        } catch (RuntimeException ignored) {}
        Collections.sort(result.candidates);
        return result;
    }

    public static JSONObject collect(Context context, Scan scan, OutputStream destination, Progress progress) throws Exception {
        PackageManager pm = context.getPackageManager();
        JSONObject report = new JSONObject();
        JSONObject device = new JSONObject();
        device.put("manufacturer", Build.MANUFACTURER);
        device.put("model", Build.MODEL);
        device.put("android", Build.VERSION.RELEASE);
        device.put("sdk", Build.VERSION.SDK_INT);
        device.put("build_display", Build.DISPLAY);
        report.put("device", device);
        report.put("collector", "1.0-READONLY");
        report.put("collected_at_ms", System.currentTimeMillis());
        report.put("missing", new JSONArray(scan.missing));
        report.put("candidates", new JSONArray(scan.candidates));
        JSONArray packages = new JSONArray();
        report.put("packages", packages);
        byte[] buffer = new byte[65536];
        ZipOutputStream zip = new ZipOutputStream(new BufferedOutputStream(destination));
        try {
            for (String name : scan.found) {
                JSONObject item = new JSONObject();
                item.put("package", name);
                packages.put(item);
                try {
                    PackageInfo p = pm.getPackageInfo(name, PackageManager.GET_ACTIVITIES | PackageManager.GET_SERVICES | PackageManager.GET_RECEIVERS | PackageManager.GET_PROVIDERS | PackageManager.GET_PERMISSIONS);
                    item.put("version_name", p.versionName == null ? "" : p.versionName);
                    item.put("version_code", Build.VERSION.SDK_INT >= 28 ? p.getLongVersionCode() : p.versionCode);
                    item.put("application_flags", p.applicationInfo.flags);
                    item.put("components", components(p));
                    item.put("requested_permissions", new JSONArray(p.requestedPermissions == null ? new String[0] : p.requestedPermissions));
                    ArrayList<String> paths = new ArrayList<>();
                    if (p.applicationInfo.sourceDir != null) paths.add(p.applicationInfo.sourceDir);
                    if (p.applicationInfo.splitSourceDirs != null) Collections.addAll(paths, p.applicationInfo.splitSourceDirs);
                    JSONArray files = new JSONArray();
                    item.put("files", files);
                    int index = 0;
                    for (String path : paths) {
                        JSONObject entry = new JSONObject();
                        files.put(entry);
                        entry.put("source_path", path);
                        File source = new File(path);
                        String outputName = index == 0 ? "base.apk" : "split_" + index + "_" + safeName(source.getName());
                        index++;
                        String zipName = "packages/" + name + "/" + outputName;
                        entry.put("archive_path", zipName);
                        progress.update("읽는 중: " + name + " / " + outputName);
                        try {
                            if (!source.isFile()) throw new IOException("APK file is not readable");
                            if (source.length() > MAX_APK) throw new IOException("APK exceeds 100 MiB limit");
                            MessageDigest digest = MessageDigest.getInstance("SHA-256");
                            long count = 0;
                            try (InputStream in = new BufferedInputStream(new FileInputStream(source))) {
                                zip.putNextEntry(new ZipEntry(zipName));
                                try {
                                    int n;
                                    while ((n = in.read(buffer)) != -1) {
                                        count += n;
                                        if (count > MAX_APK) throw new IOException("APK exceeds 100 MiB limit");
                                        zip.write(buffer, 0, n);
                                        digest.update(buffer, 0, n);
                                    }
                                } finally { zip.closeEntry(); }
                            }
                            entry.put("bytes", count);
                            entry.put("sha256", hex(digest.digest()));
                            entry.put("status", "copied");
                        } catch (Exception e) {
                            entry.put("status", "failed");
                            entry.put("error", e.getClass().getSimpleName() + ": " + String.valueOf(e.getMessage()));
                        }
                    }
                } catch (Exception e) {
                    item.put("status", "failed");
                    item.put("error", e.getClass().getSimpleName() + ": " + String.valueOf(e.getMessage()));
                }
            }
            JSONObject bridge = new JSONObject();
            try {
                PackageInfo p = pm.getPackageInfo("com.tw.service.xt", 0);
                bridge.put("version_name", p.versionName == null ? "" : p.versionName);
                bridge.put("version_code", Build.VERSION.SDK_INT >= 28 ? p.getLongVersionCode() : p.versionCode);
            } catch (PackageManager.NameNotFoundException e) { bridge.put("status", "not_found"); }
            report.put("tw_service_xt", bridge);
            putText(zip, "report.json", report.toString(2));
            putText(zip, "README_KO.txt", "VWID AC Collector 1.0 - READ ONLY\n\nThis archive contains only selected installed HVAC APK files, their component metadata and package-name candidates. No app-private data, root access, MCU command, CAN write or network upload is used.\n\nIf com.tw.ac is absent or unreadable, inspect report.json and share the report. Do not guess a control command.\n");
            zip.finish();
            zip.flush();
            return report;
        } finally { zip.close(); }
    }

    private static JSONArray components(PackageInfo p) throws Exception {
        JSONArray out = new JSONArray();
        addComponents(out, "activity", p.activities);
        addComponents(out, "service", p.services);
        addComponents(out, "receiver", p.receivers);
        addComponents(out, "provider", p.providers);
        return out;
    }
    private static void addComponents(JSONArray out, String type, ComponentInfo[] components) throws Exception {
        if (components == null) return;
        for (ComponentInfo c : components) {
            JSONObject j = new JSONObject();
            j.put("type", type);
            j.put("name", c.name);
            j.put("exported", c.exported);
            j.put("enabled", c.enabled);
            j.put("permission", c instanceof ServiceInfo ? ((ServiceInfo)c).permission : c instanceof ActivityInfo ? ((ActivityInfo)c).permission : c instanceof ProviderInfo ? ((ProviderInfo)c).readPermission : JSONObject.NULL);
            out.put(j);
        }
    }
    private static String safeName(String name) { return name.replaceAll("[^A-Za-z0-9._-]", "_"); }
    private static String hex(byte[] bytes) {
        StringBuilder s = new StringBuilder();
        for (byte b : bytes) s.append(String.format(Locale.US, "%02x", b & 255));
        return s.toString();
    }
    private static void putText(ZipOutputStream zip, String name, String text) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(text.getBytes("UTF-8"));
        zip.closeEntry();
    }
}
