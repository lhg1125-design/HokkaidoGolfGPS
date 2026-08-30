package com.vwid.hvacbridge;

import android.Manifest;
import android.app.*;
import android.os.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.widget.*;
import java.io.File;
import java.util.*;

public class MainActivity extends Activity {
    static final int REQ_STORAGE=702;
    TextView st;
    LinearLayout root;

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(28,28,28,28);
        root.setBackgroundColor(Color.rgb(12,12,13));

        st=new TextView(this);
        st.setTextColor(Color.WHITE);
        st.setTextSize(18);
        st.setText("VWID HVAC Bridge R5.2\n\nNO CABLE / NO ADB / NO FILE PICKER\n1) AUTO FIND MCUDEBUG + START\n2) Add VWID HVAC widget");
        root.addView(st);

        Button auto=btn("AUTO FIND MCUDEBUG + START");
        Button stop=btn("STOP LISTENER");
        Button qa=btn("QA: 22° / 24° / FAN 6 / VENT 3-2");
        root.addView(auto); root.addView(stop); root.addView(qa);

        auto.setOnClickListener(v->ensurePermissionAndFind());

        stop.setOnClickListener(v->{
            getSharedPreferences("hvac",0).edit().putBoolean("file_autostart",false).apply();
            stopService(new Intent(this,FileMcuService.class));
            st.append("\nListener stopped");
        });

        qa.setOnClickListener(v->{
            HvacState s=HvacState.fromFrame("2e 21 05 c4 16 09 0d 32 b7");
            s.save(this);
            HvacWidgetBase.updateAll(this);
            st.append("\nQA state sent");
        });
        setContentView(root);
    }

    private void ensurePermissionAndFind(){
        if(Build.VERSION.SDK_INT>=23 && checkSelfPermission(Manifest.permission.READ_EXTERNAL_STORAGE)!=PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},REQ_STORAGE);
        } else findAndStart();
    }

    @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] grantResults){
        super.onRequestPermissionsResult(requestCode,permissions,grantResults);
        if(requestCode==REQ_STORAGE && grantResults.length>0 && grantResults[0]==PackageManager.PERMISSION_GRANTED) findAndStart();
        else if(requestCode==REQ_STORAGE) st.append("\nStorage permission denied");
    }

    private void findAndStart(){
        st.append("\nSearching...");
        new Thread(()->{
            File best=findBestMcuLog();
            runOnUiThread(()->{
                if(best==null){
                    st.append("\nNO MCUdebug file found. Start MCUdebug logging once, then tap again.");
                } else {
                    getSharedPreferences("hvac",0).edit()
                        .putString("mcu_path",best.getAbsolutePath())
                        .putBoolean("file_autostart",true).apply();
                    Intent s=new Intent(this,FileMcuService.class);
                    if(Build.VERSION.SDK_INT>=26)startForegroundService(s); else startService(s);
                    st.append("\nFOUND + STARTED:\n"+best.getAbsolutePath());
                }
            });
        },"McuFinder").start();
    }

    private File findBestMcuLog(){
        ArrayList<File> roots=new ArrayList<>();
        File ext=android.os.Environment.getExternalStorageDirectory();
        if(ext!=null) roots.add(ext);
        roots.add(new File("/sdcard"));
        roots.add(new File("/storage/emulated/0"));
        roots.add(new File("/storage"));
        HashSet<String> seen=new HashSet<>();
        File best=null;
        long bestTime=-1;
        int[] count={0};
        for(File r:roots){
            File f=scan(r,0,seen,count);
            if(f!=null && f.lastModified()>bestTime){best=f;bestTime=f.lastModified();}
            if(count[0]>6000)break;
        }
        return best;
    }

    private File scan(File f,int depth,HashSet<String> seen,int[] count){
        if(f==null || !f.exists() || depth>5 || count[0]>6000)return null;
        try{
            String cp=f.getCanonicalPath();
            if(!seen.add(cp))return null;
        }catch(Exception ignored){}
        count[0]++;
        if(f.isFile()){
            String n=f.getName().toLowerCase(Locale.US);
            if(n.contains("mcu") && n.contains("debug") && (n.endsWith(".txt")||n.endsWith(".log")) && f.canRead()) return f;
            return null;
        }
        File[] kids;
        try{ kids=f.listFiles(); }catch(Exception e){ return null; }
        if(kids==null)return null;
        File best=null; long bt=-1;
        for(File k:kids){
            File hit=scan(k,depth+1,seen,count);
            if(hit!=null && hit.lastModified()>bt){best=hit;bt=hit.lastModified();}
            if(count[0]>6000)break;
        }
        return best;
    }

    Button btn(String s){ Button b=new Button(this); b.setText(s); return b; }
}
