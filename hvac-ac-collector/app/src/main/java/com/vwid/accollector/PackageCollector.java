package com.vwid.accollector;

import android.content.Context;
import android.content.pm.*;
import android.os.Build;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.*;

public final class PackageCollector {
    private static final String[] EXACT_TARGETS = {"com.tw.ac", "com.zht.car.accontroller"};
    private static final String[] DEX_MARKERS = {
        "com/tw/ac", "com.tw.ac", "AirService", "IAirConditionController",
        "aircondition", "accontroller", "PROJECT_AIR", "sendExtendedInterfaFunction"
    };
    private static final long MAX_APK = 100L * 1024 * 1024;
    private static final long MAX_DEX_SCAN = 32L * 1024 * 1024;
    private PackageCollector() {}

    public static final class Candidate {
        public String packageName;
        public String sourcePath;
        public String reason;
        public final ArrayList<String> markerHits = new ArrayList<>();
        public boolean copyApk;
    }

    public static final class Scan {
        public final ArrayList<String> found = new ArrayList<>();
        public final ArrayList<String> missing = new ArrayList<>();
        public final ArrayList<String> candidateNames = new ArrayList<>();
        public final ArrayList<Candidate> candidates = new ArrayList<>();
        public int installedPackagesScanned = 0;
    }

    public interface Progress { void update(String message); }

    public static Scan scan(Context context) {
        PackageManager pm = context.getPackageManager();
        Scan result = new Scan();

        for (String name : EXACT_TARGETS) {
            try { pm.getPackageInfo(name, 0); result.found.add(name); }
            catch (PackageManager.NameNotFoundException e) { result.missing.add(name); }
        }

        List<PackageInfo> all;
        try { all = pm.getInstalledPackages(PackageManager.GET_ACTIVITIES | PackageManager.GET_SERVICES | PackageManager.GET_RECEIVERS | PackageManager.GET_PROVIDERS); }
        catch (Throwable e) { all = Collections.emptyList(); }

        for (PackageInfo p : all) {
            if (p == null || p.packageName == null || p.applicationInfo == null) continue;
            result.installedPackagesScanned++;
            String n = p.packageName;
            String lower = n.toLowerCase(Locale.US);
            boolean vendorNamespace = lower.startsWith("com.tw.") || lower.startsWith("com.zht.");
            boolean nameHint = lower.contains("aircondition") || lower.contains("accontroller") || lower.contains("climate") || lower.contains("airservice");
            boolean componentHint = hasComponentHint(p);
            if (!vendorNamespace && !nameHint && !componentHint) continue;

            Candidate c = new Candidate();
            c.packageName = n;
            c.sourcePath = p.applicationInfo.sourceDir == null ? "" : p.applicationInfo.sourceDir;
            ArrayList<String> reasons = new ArrayList<>();
            if (vendorNamespace) reasons.add("vendor_namespace");
            if (nameHint) reasons.add("package_name");
            if (componentHint) reasons.add("component_name");

            if (p.applicationInfo.sourceDir != null) {
                try { c.markerHits.addAll(scanDexMarkers(new File(p.applicationInfo.sourceDir))); }
                catch (Throwable ignored) {}
            }
            if (!c.markerHits.isEmpty()) reasons.add("dex_marker");

            c.reason = join(reasons, ",");
            c.copyApk = result.found.contains(n) || !c.markerHits.isEmpty() || nameHint || componentHint;
            result.candidates.add(c);
            result.candidateNames.add(n + (c.markerHits.isEmpty() ? "" : " [" + join(c.markerHits, ",") + "]"));
        }

        Collections.sort(result.candidateNames);
        Collections.sort(result.candidates, (a,b) -> a.packageName.compareTo(b.packageName));
        return result;
    }

    private static boolean hasComponentHint(PackageInfo p) {
        return componentsContain(p.activities) || componentsContain(p.services) || componentsContain(p.receivers) || componentsContain(p.providers);
    }

    private static boolean componentsContain(ComponentInfo[] infos) {
        if (infos == null) return false;
        for (ComponentInfo i : infos) {
            if (i == null || i.name == null) continue;
            String s = i.name.toLowerCase(Locale.US);
            if (s.contains("airservice") || s.contains("aircondition") || s.contains("accontroller") || s.contains("climate")) return true;
        }
        return false;
    }

    private static ArrayList<String> scanDexMarkers(File apk) throws IOException {
        ArrayList<String> hits = new ArrayList<>();
        if (!apk.isFile() || apk.length() > MAX_APK) return hits;
        try (ZipFile zip = new ZipFile(apk)) {
            Enumeration<? extends ZipEntry> entries = zip.entries();
            while (entries.hasMoreElements()) {
                ZipEntry e = entries.nextElement();
                String name = e.getName();
                if (!name.matches("classes(\\d*)\\.dex")) continue;
                if (e.getSize() > MAX_DEX_SCAN) continue;
                byte[] data = readLimited(zip.getInputStream(e), MAX_DEX_SCAN);
                for (String marker : DEX_MARKERS) {
                    if (!hits.contains(marker) && contains(data, marker.getBytes(StandardCharsets.UTF_8))) hits.add(marker);
                }
            }
        }
        return hits;
    }

    private static byte[] readLimited(InputStream in, long max) throws IOException {
        try (InputStream src = new BufferedInputStream(in); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] b = new byte[65536];
            long count = 0;
            int n;
            while ((n = src.read(b)) != -1) {
                count += n;
                if (count > max) throw new IOException("scan limit exceeded");
                out.write(b, 0, n);
            }
            return out.toByteArray();
        }
    }

    private static boolean contains(byte[] data, byte[] pattern) {
        if (pattern.length == 0 || data.length < pattern.length) return false;
        outer: for (int i=0; i<=data.length-pattern.length; i++) {
            for (int j=0; j<pattern.length; j++) if (data[i+j] != pattern[j]) continue outer;
            return true;
        }
        return false;
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
        report.put("collector", "1.1-DEEP-READONLY");
        report.put("collected_at_ms", System.currentTimeMillis());
        report.put("installed_packages_scanned", scan.installedPackagesScanned);
        report.put("missing_exact_targets", new JSONArray(scan.missing));
        report.put("exact_targets_found", new JSONArray(scan.found));
        report.put("candidate_names", new JSONArray(scan.candidateNames));

        JSONArray candidatesJson = new JSONArray();
        report.put("candidates", candidatesJson);
        JSONArray packages = new JSONArray();
        report.put("copied_packages", packages);

        byte[] buffer = new byte[65536];
        ZipOutputStream zip = new ZipOutputStream(new BufferedOutputStream(destination));
        HashSet<String> copied = new HashSet<>();
        try {
            for (Candidate c : scan.candidates) {
                JSONObject cj = new JSONObject();
                cj.put("package", c.packageName);
                cj.put("source_path", c.sourcePath);
                cj.put("reason", c.reason);
                cj.put("marker_hits", new JSONArray(c.markerHits));
                cj.put("selected_for_copy", c.copyApk);
                candidatesJson.put(cj);
                if (!c.copyApk || !copied.add(c.packageName)) continue;

                JSONObject item = collectPackage(pm, c.packageName, zip, buffer, progress);
                packages.put(item);
            }

            for (String name : scan.found) {
                if (!copied.add(name)) continue;
                packages.put(collectPackage(pm, name, zip, buffer, progress));
            }

            JSONObject bridge = new JSONObject();
            try {
                PackageInfo p = pm.getPackageInfo("com.tw.service.xt", 0);
                bridge.put("version_name", p.versionName == null ? "" : p.versionName);
                bridge.put("version_code", Build.VERSION.SDK_INT >= 28 ? p.getLongVersionCode() : p.versionCode);
                bridge.put("source_path", p.applicationInfo == null ? "" : p.applicationInfo.sourceDir);
            } catch (PackageManager.NameNotFoundException e) { bridge.put("status", "not_found"); }
            report.put("tw_service_xt", bridge);

            putText(zip, "report.json", report.toString(2));
            putText(zip, "README_KO.txt",
                "VWID AC Collector 1.1 - DEEP READ ONLY\n\n" +
                "Exact com.tw.ac packages were not present in the previous capture. This build scans installed vendor APK DEX files for HVAC implementation markers and copies only candidates with concrete package/component/DEX evidence.\n" +
                "No root, MCU command, CAN write, service invocation, app-private data or network upload is used.\n");
            zip.finish();
            zip.flush();
            return report;
        } finally { zip.close(); }
    }

    private static JSONObject collectPackage(PackageManager pm, String name, ZipOutputStream zip, byte[] buffer, Progress progress) throws Exception {
        JSONObject item = new JSONObject();
        item.put("package", name);
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
        return item;
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
    private static String join(Collection<String> values, String separator) {
        StringBuilder s = new StringBuilder();
        boolean first = true;
        for (String v : values) { if (!first) s.append(separator); first = false; s.append(v); }
        return s.toString();
    }
    private static String hex(byte[] bytes) {
        StringBuilder s = new StringBuilder();
        for (byte b : bytes) s.append(String.format(Locale.US, "%02x", b & 255));
        return s.toString();
    }
    private static void putText(ZipOutputStream zip, String name, String text) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(text.getBytes(StandardCharsets.UTF_8));
        zip.closeEntry();
    }
}
