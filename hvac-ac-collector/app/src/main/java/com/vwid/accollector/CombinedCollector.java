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
            CallerCollector.collect(context, out, progress);
            putText(out, "README_KO.txt",
                "VWID AC Collector 1.3 - CALLER TRACE READ ONLY\n\n" +
                "This build combines three read-only searches: installed HVAC implementation evidence, hidden system APK locations, and installed DEX callers of the exported HVAC command bridge.\n" +
                "caller_scan_report.json and caller_dex/ are intended to reveal the meaning of project=air data0/data1 without sending any vehicle command.\n" +
                "No root, install, package unhide, MCU/CAN command, service start, broadcast, or network upload is performed.\n");
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
