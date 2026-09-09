package com.vwid.accollector;

import android.app.Activity;
import android.content.*;
import android.net.Uri;
import android.os.*;
import android.provider.MediaStore;
import android.graphics.Color;
import android.view.View;
import android.widget.*;
import java.io.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.*;

public final class MainActivity extends Activity {
    private static final int REQUEST_SAVE = 1001;
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final Handler ui = new Handler(Looper.getMainLooper());
    private TextView status;
    private Button scanButton, saveButton, alternateButton, shareButton;
    private PackageCollector.Scan scan;
    private Uri lastArchive;
    private boolean busy;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(18), dp(20), dp(18));
        root.setBackgroundColor(Color.rgb(16, 17, 19));
        TextView title = new TextView(this);
        title.setText("VWID AC Collector 1.1");
        title.setTextSize(22);
        title.setTextColor(Color.WHITE);
        root.addView(title);
        TextView note = new TextView(this);
        note.setText("차량 내부에서 공조 제어 구현 APK를 심층 검색합니다. PC·ADB·루트 불필요.\nDEX 문자열을 읽기만 하며 MCU 송신/CAN 쓰기/공조 조작은 하지 않습니다.");
        note.setTextSize(14);
        note.setTextColor(Color.rgb(205, 205, 205));
        note.setPadding(0, dp(12), 0, dp(12));
        root.addView(note);
        scanButton = button(root, "공조 구현 APK 심층 검색", v -> runScan());
        saveButton = button(root, "결과 ZIP 생성 · 다운로드 저장", v -> saveToDownloads());
        alternateButton = button(root, "다른 위치에 저장", v -> chooseDestination());
        shareButton = button(root, "저장한 ZIP 공유", v -> shareArchive());
        ScrollView scroll = new ScrollView(this);
        status = new TextView(this);
        status.setTextColor(Color.WHITE);
        status.setTextSize(15);
        status.setTextIsSelectable(true);
        status.setPadding(0, dp(12), 0, dp(12));
        scroll.addView(status);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(root);
        show("설치 APK와 DEX 공조 흔적 검색 중…");
        refreshButtons();
        runScan();
    }

    private Button button(LinearLayout parent, String label, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setOnClickListener(listener);
        parent.addView(b, new LinearLayout.LayoutParams(-1, -2));
        return b;
    }
    private int dp(int value) { return (int)(value * getResources().getDisplayMetrics().density + 0.5f); }
    private void show(String message) { status.setText(message); }
    private void post(String message) { ui.post(() -> { if (!isFinishing() && !isDestroyed()) show(message); }); }
    private void refreshButtons() {
        if (scanButton == null) return;
        scanButton.setEnabled(!busy);
        saveButton.setEnabled(!busy && scan != null);
        alternateButton.setEnabled(!busy && scan != null);
        shareButton.setEnabled(!busy && lastArchive != null);
    }
    private void setBusy(boolean value) { busy = value; refreshButtons(); }

    private void runScan() {
        if (busy) return;
        setBusy(true);
        show("설치 APK와 DEX 공조 흔적 검색 중… 잠시 기다리세요.");
        Context app = getApplicationContext();
        worker.execute(() -> {
            try {
                PackageCollector.Scan result = PackageCollector.scan(app);
                ui.post(() -> {
                    scan = result;
                    setBusy(false);
                    StringBuilder text = new StringBuilder();
                    text.append("검색 완료 · 설치 패키지 ").append(result.installedPackagesScanned).append("개 확인\n\n");
                    for (String s : result.found) text.append("정확한 대상 ✓ ").append(s).append('\n');
                    for (String s : result.missing) text.append("정확한 대상 없음: ").append(s).append('\n');
                    text.append("\nVendor/DEX 후보\n");
                    int selected = 0;
                    for (PackageCollector.Candidate c : result.candidates) {
                        if (!c.copyApk) continue;
                        selected++;
                        text.append("✓ ").append(c.packageName);
                        if (!c.markerHits.isEmpty()) text.append("\n   DEX: ").append(join(c.markerHits));
                        text.append("\n   근거: ").append(c.reason).append('\n');
                    }
                    if (selected == 0) text.append("뚜렷한 구현 APK 없음\n");
                    text.append("\n결과 ZIP을 저장해 이 대화에 올려주세요.\n이번 버전은 후보 APK 자체도 함께 담습니다.");
                    show(text.toString());
                });
            } catch (Throwable e) {
                ui.post(() -> { setBusy(false); show("검색 실패: " + e); });
            }
        });
    }

    private String join(Collection<String> values) {
        StringBuilder s = new StringBuilder();
        boolean first = true;
        for (String v : values) { if (!first) s.append(", "); first=false; s.append(v); }
        return s.toString();
    }

    private String archiveName() {
        return "VWID_AC_DEEP_SOURCE_" + new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date()) + ".zip";
    }
    private void saveToDownloads() {
        if (busy || scan == null) return;
        if (Build.VERSION.SDK_INT < 29) { chooseDestination(); return; }
        PackageCollector.Scan selected = scan;
        setBusy(true);
        show("Downloads/VWID_HVAC에 결과 ZIP 저장 중…");
        Context app = getApplicationContext();
        worker.execute(() -> {
            Uri uri = null;
            try {
                ContentValues values = new ContentValues();
                values.put(MediaStore.MediaColumns.DISPLAY_NAME, archiveName());
                values.put(MediaStore.MediaColumns.MIME_TYPE, "application/zip");
                values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/VWID_HVAC");
                values.put(MediaStore.MediaColumns.IS_PENDING, 1);
                uri = app.getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                if (uri == null) throw new IOException("Downloads entry creation failed");
                writeArchive(app, selected, uri);
                ContentValues done = new ContentValues();
                done.put(MediaStore.MediaColumns.IS_PENDING, 0);
                app.getContentResolver().update(uri, done, null, null);
                success(uri, "저장 완료\nDownloads/VWID_HVAC\n\n'저장한 ZIP 공유'로 이 대화에 전달하세요.");
            } catch (Throwable e) {
                if (uri != null) try { app.getContentResolver().delete(uri, null, null); } catch (Throwable ignored) {}
                failure("Downloads 저장 실패: " + e + "\n\n'다른 위치에 저장'을 사용하세요.");
            }
        });
    }

    private void chooseDestination() {
        if (busy || scan == null) return;
        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("application/zip");
        intent.putExtra(Intent.EXTRA_TITLE, archiveName());
        try { startActivityForResult(intent, REQUEST_SAVE); }
        catch (Exception e) { show("파일 저장 화면을 열 수 없습니다: " + e); }
    }
    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQUEST_SAVE || resultCode != RESULT_OK || data == null || data.getData() == null || busy || scan == null) return;
        Uri uri = data.getData();
        PackageCollector.Scan selected = scan;
        setBusy(true);
        show("선택한 위치에 ZIP 저장 중…");
        Context app = getApplicationContext();
        worker.execute(() -> {
            try { writeArchive(app, selected, uri); success(uri, "저장 완료\n\n공유 버튼으로 ZIP을 전달하세요."); }
            catch (Throwable e) { failure("저장 실패: " + e); }
        });
    }

    private void writeArchive(Context app, PackageCollector.Scan selected, Uri uri) throws Exception {
        OutputStream out = app.getContentResolver().openOutputStream(uri, "w");
        if (out == null) throw new IOException("Cannot open destination");
        PackageCollector.collect(app, selected, out, this::post);
    }
    private void success(Uri uri, String message) {
        ui.post(() -> { lastArchive = uri; setBusy(false); show(message); });
    }
    private void failure(String message) {
        ui.post(() -> { setBusy(false); show(message); });
    }
    private void shareArchive() {
        if (lastArchive == null) return;
        Intent send = new Intent(Intent.ACTION_SEND);
        send.setType("application/zip");
        send.putExtra(Intent.EXTRA_STREAM, lastArchive);
        send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try { startActivity(Intent.createChooser(send, "공조 심층 진단 ZIP 공유")); }
        catch (Exception e) { show("공유 앱을 열 수 없습니다: " + e); }
    }
}
