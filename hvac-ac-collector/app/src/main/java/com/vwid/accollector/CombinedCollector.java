package com.vwid.accollector;

import android.content.Context;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.zip.*;

final class CombinedCollector {
    private CombinedCollector() {}

    static void collect(Context context, PackageCollector.Scan scan, OutputStream destination,
                        PackageCollector.Progress progress) throws Exception {
        ByteArrayOutputStream baseBytes = new ByteArrayOutputStream();
        PackageCollector.collect(context, scan, baseBytes, progress);

        ZipOutputStream out = new ZipOutputStream(new BufferedOutputStream(destination));
        byte[] buffer = new byte[65536];
        try {
            try (ZipInputStream in = new ZipInputStream(new ByteArrayInputStream(baseBytes.toByteArray()))) {
                ZipEntry e;
                while ((e = in.getNextEntry()) != null) {
                    if ("README_KO.txt".equals(e.getName())) continue;
                    out.putNextEntry(new ZipEntry(e.getName()));
                    int n;
                    while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
                    out.closeEntry();
                    in.closeEntry();
                }
            }

            JSONObject hidden = HiddenAcCollector.collect(out, progress);
            putText(out, "hidden_ac_report.json", hidden.toString(2));
            putText(out, "README_KO.txt",
                "VWID AC Collector 1.2 - HIDDEN HVAC READ ONLY\n\n" +
                "Factory CarChoose code references /system/etc/apkx and com.tw.ac_c8e8. " +
                "This build therefore scans those read-only system locations and copies only files with HVAC name/DEX evidence.\n" +
                "No root, install, package unhide, MCU command, CAN write, service start, or vehicle control is performed.\n");
            out.finish();
            out.flush();
        } finally {
            out.close();
        }
    }

    private static void putText(ZipOutputStream zip, String name, String text) throws IOException {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(text.getBytes(StandardCharsets.UTF_8));
        zip.closeEntry();
    }
}
