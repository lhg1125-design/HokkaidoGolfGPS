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

public final class HiddenCollectorActivity extends Activity {
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final Handler ui = new Handler(Looper.getMainLooper());
    private TextView status;
    private Button collectButton, shareButton;
    private Uri lastArchive;
    private boolean busy;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22), dp(20), dp(22), dp(20));
        root.setBackgroundColor(Color.rgb(16,17,19));

        TextView title = new TextView(this);
        title.setText("VWID AC Collector 1.3 CALLER");
        title.setTextSize(23);
        title.setTextColor(Color.WHITE);
        root.addView(title);

        TextView note = new TextView(this);
        note.setText("차량 자체에서 공조 제어 명령을 호출하는 APK/DEX까지 찾습니다.\n설치 공조 후보 + 숨은 시스템 경로 + project=air / data0 / data1 호출 흔적을 한 번에 수집합니다.\n\n읽기 전용: 실제 공조 명령 송신, 서비스 실행, CAN 조작 없음.");
        note.setTextSize(14);
        note.setTextColor(Color.rgb(210,210,210));
        note.setPadding(0,dp(12),0,dp(14));
        root.addView(note);

        collectButton = button(root,"공조 CALLER 추적 ZIP 생성",v -> collect());
        shareButton = button(root,"생성한 ZIP 공유",v -> share());
        shareButton.setEnabled(false);

        ScrollView scroll = new ScrollView(this);
        status = new TextView(this);
        status.setTextColor(Color.WHITE);
        status.setTextSize(15);
        status.setTextIsSelectable(true);
        status.setPadding(0,dp(14),0,0);
        scroll.addView(status);
        root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        setContentView(root);
        show("준비 완료. 첫 버튼을 누르면 차량 내부 APK/DEX를 읽기만 합니다.");
    }

    private Button button(LinearLayout parent,String text,View.OnClickListener l) {
        Button b=new Button(this); b.setText(text); b.setAllCaps(false); b.setOnClickListener(l);
        parent.addView(b,new LinearLayout.LayoutParams(-1,-2)); return b;
    }
    private int dp(int v){return (int)(v*getResources().getDisplayMetrics().density+0.5f);}
    private void show(String s){status.setText(s);}
    private void post(String s){ui.post(() -> { if(!isFinishing()&&!isDestroyed()) show(s); });}
    private String archiveName(){return "VWID_AC_CALLER_SOURCE_"+new SimpleDateFormat("yyyyMMdd_HHmmss",Locale.US).format(new Date())+".zip";}

    private void collect() {
        if(busy) return;
        busy=true; collectButton.setEnabled(false); shareButton.setEnabled(false);
        show("설치 APK + 숨은 경로 + 공조 CALLER DEX 검색 중…\n앱 수에 따라 조금 걸릴 수 있습니다.");
        Context app=getApplicationContext();
        worker.execute(() -> {
            Uri uri=null;
            try {
                PackageCollector.Scan scan=PackageCollector.scan(app);
                if(Build.VERSION.SDK_INT<29) throw new IOException("Android 10 Downloads API required");
                ContentValues values=new ContentValues();
                values.put(MediaStore.MediaColumns.DISPLAY_NAME,archiveName());
                values.put(MediaStore.MediaColumns.MIME_TYPE,"application/zip");
                values.put(MediaStore.MediaColumns.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/VWID_HVAC");
                values.put(MediaStore.MediaColumns.IS_PENDING,1);
                uri=app.getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,values);
                if(uri==null) throw new IOException("Downloads entry creation failed");
                OutputStream out=app.getContentResolver().openOutputStream(uri,"w");
                if(out==null) throw new IOException("Cannot open destination");
                CombinedCollector.collect(app,scan,out,this::post);
                ContentValues done=new ContentValues(); done.put(MediaStore.MediaColumns.IS_PENDING,0);
                app.getContentResolver().update(uri,done,null,null);
                final Uri saved=uri;
                ui.post(() -> {
                    lastArchive=saved; busy=false; collectButton.setEnabled(true); shareButton.setEnabled(true);
                    show("CALLER 추적 완료\nDownloads/VWID_HVAC\n\n'생성한 ZIP 공유'로 이 대화에 올려주세요.");
                });
            } catch(Throwable e) {
                if(uri!=null) try{app.getContentResolver().delete(uri,null,null);}catch(Throwable ignored){}
                final String msg=e.getClass().getSimpleName()+": "+String.valueOf(e.getMessage());
                ui.post(() -> {busy=false;collectButton.setEnabled(true);shareButton.setEnabled(false);show("수집 실패: "+msg);});
            }
        });
    }

    private void share() {
        if(lastArchive==null) return;
        Intent send=new Intent(Intent.ACTION_SEND);
        send.setType("application/zip");
        send.putExtra(Intent.EXTRA_STREAM,lastArchive);
        send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try{startActivity(Intent.createChooser(send,"공조 CALLER 추적 ZIP 공유"));}
        catch(Throwable e){show("공유 화면 실패: "+e);}
    }
}
