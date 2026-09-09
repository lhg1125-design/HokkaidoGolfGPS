package com.vwid.accollector;

import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.*;

final class HiddenAcCollector {
    private static final long MAX_FILE = 80L * 1024 * 1024;
    private static final String[] MARKERS = {
        "com/tw/ac", "com.tw.ac", "AirService", "IAirConditionController",
        "aircondition", "accontroller", "PROJECT_AIR", "extendedInterface"
    };

    private HiddenAcCollector() {}

    static JSONObject collect(ZipOutputStream out, PackageCollector.Progress progress) throws Exception {
        JSONObject report = new JSONObject();
        JSONArray roots = new JSONArray();
        JSONArray files = new JSONArray();
        report.put("strategy", "READ_ONLY_FILESYSTEM_SCAN");
        report.put("code_evidence", "/system/etc/apkx + com.tw.ac_c8e8 referenced by factory CarChoose");
        report.put("roots", roots);
        report.put("files", files);

        scanRoot(new File("/system/etc/apkx"), true, 1, roots, files, out, progress);
        scanRoot(new File("/system/etc/apk"), true, 1, roots, files, out, progress);
        scanRoot(new File("/system/priv-app"), false, 2, roots, files, out, progress);
        scanRoot(new File("/system/app"), false, 2, roots, files, out, progress);
        scanRoot(new File("/product/priv-app"), false, 2, roots, files, out, progress);
        scanRoot(new File("/product/app"), false, 2, roots, files, out, progress);
        return report;
    }

    private static void scanRoot(File root, boolean inspectAllApks, int depth,
                                 JSONArray roots, JSONArray files, ZipOutputStream out,
                                 PackageCollector.Progress progress) throws Exception {
        JSONObject r = new JSONObject();
        r.put("path", root.getAbsolutePath());
        r.put("exists", root.exists());
        r.put("readable", root.canRead());
        roots.put(r);
        if (!root.isDirectory() || !root.canRead()) return;
        ArrayList<File> discovered = new ArrayList<>();
        walk(root, depth, discovered);
        r.put("entries_seen", discovered.size());
        int selected = 0;
        for (File f : discovered) {
            if (!f.isFile()) continue;
            String lower = f.getName().toLowerCase(Locale.US);
            boolean apk = lower.endsWith(".apk");
            boolean nameHit = lower.contains("com.tw.ac") || lower.contains("accontroller") ||
                              lower.contains("airservice") || lower.contains("aircondition") ||
                              lower.contains("climate") || lower.contains("c8e8");
            ArrayList<String> markerHits = new ArrayList<>();
            if (apk && (inspectAllApks || nameHit) && f.length() > 0 && f.length() <= MAX_FILE) {
                try { markerHits.addAll(scanMarkers(f)); } catch (Throwable ignored) {}
            }
            if (!nameHit && markerHits.isEmpty()) continue;
            selected++;
            JSONObject j = new JSONObject();
            j.put("source_path", f.getAbsolutePath());
            j.put("bytes", f.length());
            j.put("name_hit", nameHit);
            j.put("marker_hits", new JSONArray(markerHits));
            files.put(j);
            progress.update("숨은 공조 파일 읽는 중: " + f.getName());
            try {
                if (!f.canRead()) throw new IOException("file not readable");
                if (f.length() > MAX_FILE) throw new IOException("file too large");
                String zipName = "hidden_ac/" + safe(root.getName()) + "/" + safe(f.getName());
                MessageDigest md = MessageDigest.getInstance("SHA-256");
                long count = 0;
                byte[] buf = new byte[65536];
                try (InputStream in = new BufferedInputStream(new FileInputStream(f))) {
                    out.putNextEntry(new ZipEntry(zipName));
                    try {
                        int n;
                        while ((n = in.read(buf)) != -1) {
                            count += n;
                            if (count > MAX_FILE) throw new IOException("file exceeded size limit");
                            out.write(buf, 0, n);
                            md.update(buf, 0, n);
                        }
                    } finally { out.closeEntry(); }
                }
                j.put("archive_path", zipName);
                j.put("copied_bytes", count);
                j.put("sha256", hex(md.digest()));
                j.put("status", "copied");
            } catch (Throwable e) {
                j.put("status", "failed");
                j.put("error", e.getClass().getSimpleName() + ": " + String.valueOf(e.getMessage()));
            }
        }
        r.put("selected", selected);
    }

    private static void walk(File dir, int depth, ArrayList<File> out) {
        if (depth < 0 || dir == null || !dir.isDirectory()) return;
        File[] list;
        try { list = dir.listFiles(); } catch (Throwable e) { list = null; }
        if (list == null) return;
        for (File f : list) {
            out.add(f);
            if (f.isDirectory() && depth > 0) walk(f, depth - 1, out);
        }
    }

    private static ArrayList<String> scanMarkers(File apk) throws IOException {
        ArrayList<String> hits = new ArrayList<>();
        try (ZipFile zip = new ZipFile(apk)) {
            Enumeration<? extends ZipEntry> en = zip.entries();
            while (en.hasMoreElements()) {
                ZipEntry e = en.nextElement();
                if (!e.getName().matches("classes(\\d*)\\.dex")) continue;
                if (e.getSize() < 0 || e.getSize() > 32L * 1024 * 1024) continue;
                byte[] data = readAllLimited(zip.getInputStream(e), 32L * 1024 * 1024);
                for (String marker : MARKERS) {
                    if (!hits.contains(marker) && contains(data, marker.getBytes(StandardCharsets.UTF_8))) hits.add(marker);
                }
            }
        }
        return hits;
    }

    private static byte[] readAllLimited(InputStream raw, long max) throws IOException {
        try (InputStream in = new BufferedInputStream(raw); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] b = new byte[65536];
            long count = 0;
            int n;
            while ((n = in.read(b)) != -1) {
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

    private static String safe(String s) { return s.replaceAll("[^A-Za-z0-9._-]", "_"); }
    private static String hex(byte[] bytes) {
        StringBuilder s = new StringBuilder();
        for (byte b : bytes) s.append(String.format(Locale.US, "%02x", b & 255));
        return s.toString();
    }
}
