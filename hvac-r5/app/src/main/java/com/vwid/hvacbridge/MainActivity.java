package com.vwid.hvacbridge;

import android.Manifest;
import android.app.*;
import android.os.*;
import android.content.*;
import android.content.pm.*;
import android.graphics.Color;
import android.widget.*;
import android.text.method.ScrollingMovementMethod;
import java.io.*;
import java.util.*;

public class MainActivity extends Activity {
    static final int REQ_STORAGE = 903;
    TextView out;
    String lastReport = "";

    private static final String[] KEYS = new String[]{
        "mcu","canbus","canbox","hvac","climate","carchoose","aircondition",
        "air_condition","vehicle","carservice","carinfo","ownice",
        "com.tw.","com.syu","microntek","mtcd","mtce","mcuclient","canservice"
    };

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        getSharedPreferences("hvac",0).edit().putBoolean("file_autostart",false).apply();

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(22,18,22,18);
        root.setBackgroundColor(Color.rgb(12,12,13));

        TextView title = new TextView(this);
        title.setTextColor(Color.WHITE);
        title.setTextSize(20);
        title.setText("VWID HVAC R5.3 DIAG\nNO CABLE / NO ADB");
        root.addView(title);

        Button scan = new Button(this);
        scan.setText("SCAN MCU / CAN SYSTEM + SAVE REPORT");
        root.addView(scan);

        Button copy = new Button(this);
        copy.setText("COPY REPORT");
        root.addView(copy);

        ScrollView sv = new ScrollView(this);
        out = new TextView(this);
        out.setTextColor(Color.rgb(224,224,224));
        out.setTextSize(14);
        out.setText("Tap SCAN.\nResult will also be saved to Download/VWID_HVAC_DIAG_R5_3.txt");
        out.setTextIsSelectable(true);
        out.setMovementMethod(new ScrollingMovementMethod());
        sv.addView(out);
        root.addView(sv,new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,0,1f));

        scan.setOnClickListener(v -> ensurePermissionAndScan());
        copy.setOnClickListener(v -> {
            if(lastReport.isEmpty()) return;
            ClipboardManager cm=(ClipboardManager)getSystemService(CLIPBOARD_SERVICE);
            cm.setPrimaryClip(ClipData.newPlainText("VWID HVAC DIAG",lastReport));
            Toast.makeText(this,"Report copied",Toast.LENGTH_SHORT).show();
        });

        setContentView(root);
    }

    private void ensurePermissionAndScan(){
        if(Build.VERSION.SDK_INT>=23 &&
            checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)!=PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            },REQ_STORAGE);
        } else runScan();
    }

    @Override public void onRequestPermissionsResult(int req,String[] p,int[] g){
        super.onRequestPermissionsResult(req,p,g);
        if(req==REQ_STORAGE) runScan();
    }

    private void runScan(){
        out.setText("Scanning Ownice system...\n");
        new Thread(() -> {
            String report = buildReport();
            lastReport = report;
            String saved = saveReport(report);
            runOnUiThread(() -> out.setText(report + "\n\nSAVED: " + saved));
        },"HVAC-DIAG").start();
    }

    private String buildReport(){
        StringBuilder r=new StringBuilder(65536);
        r.append("VWID HVAC R5.3 DIAG\n");
        r.append("================================================\n");
        r.append("MODEL=").append(Build.MANUFACTURER).append(" ").append(Build.MODEL).append("\n");
        r.append("PRODUCT=").append(Build.PRODUCT).append("\n");
        r.append("DEVICE=").append(Build.DEVICE).append("\n");
        r.append("HARDWARE=").append(Build.HARDWARE).append("\n");
        r.append("BOARD=").append(Build.BOARD).append("\n");
        r.append("ANDROID=").append(Build.VERSION.RELEASE).append(" SDK=").append(Build.VERSION.SDK_INT).append("\n");
        r.append("FINGERPRINT=").append(Build.FINGERPRINT).append("\n\n");

        r.append("[1] PACKAGE / COMPONENT CANDIDATES\n");
        r.append("------------------------------------------------\n");
        scanPackages(r);

        r.append("\n[2] GETPROP CANDIDATES\n");
        r.append("------------------------------------------------\n");
        execFiltered(r,new String[]{"getprop"});

        r.append("\n[3] BINDER SERVICE LIST CANDIDATES\n");
        r.append("------------------------------------------------\n");
        execFiltered(r,new String[]{"service","list"});

        r.append("\n[4] PROCESS CANDIDATES\n");
        r.append("------------------------------------------------\n");
        execFiltered(r,new String[]{"ps","-A"});

        r.append("\n[5] /dev CANDIDATES\n");
        r.append("------------------------------------------------\n");
        scanDev(r,new File("/dev"));
        scanDev(r,new File("/dev/socket"));

        r.append("\n[6] SYSTEM APK PATH CANDIDATES\n");
        r.append("------------------------------------------------\n");
        String[] roots={"/system/app","/system/priv-app","/vendor/app","/product/app","/system_ext/app","/oem/app"};
        for(String s:roots) scanApkTree(r,new File(s),0);

        return r.toString();
    }

    private boolean hit(String s){
        if(s==null) return false;
        String x=s.toLowerCase(Locale.US);
        for(String k:KEYS) if(x.contains(k)) return true;
        return false;
    }

    private void scanPackages(StringBuilder r){
        try{
            PackageManager pm=getPackageManager();
            int flags=PackageManager.GET_ACTIVITIES|PackageManager.GET_SERVICES|
                PackageManager.GET_RECEIVERS|PackageManager.GET_PROVIDERS|
                PackageManager.GET_PERMISSIONS|PackageManager.GET_META_DATA;
            List<PackageInfo> list=pm.getInstalledPackages(flags);
            int count=0;
            for(PackageInfo pi:list){
                ApplicationInfo ai=pi.applicationInfo;
                String label="";
                try{ label=String.valueOf(pm.getApplicationLabel(ai)); }catch(Exception ignored){}
                boolean candidate=hit(pi.packageName)||hit(label)||(ai!=null && hit(ai.sourceDir));
                candidate |= anyHit(pi.activities)||anyHit(pi.services)||anyHit(pi.receivers)||anyHit(pi.providers);
                if(!candidate) continue;
                count++;
                r.append("\n# ").append(count).append(" ").append(pi.packageName).append("\n");
                r.append("label=").append(label).append("\n");
                r.append("version=").append(pi.versionName).append(" code=").append(pi.versionCode).append("\n");
                if(ai!=null){
                    boolean sys=(ai.flags & ApplicationInfo.FLAG_SYSTEM)!=0;
                    boolean upd=(ai.flags & ApplicationInfo.FLAG_UPDATED_SYSTEM_APP)!=0;
                    r.append("system=").append(sys).append(" updatedSystem=").append(upd).append("\n");
                    r.append("sourceDir=").append(ai.sourceDir).append("\n");
                    r.append("nativeLib=").append(ai.nativeLibraryDir).append("\n");
                }
                appendComponents(r,"ACT",pi.activities);
                appendComponents(r,"SVC",pi.services);
                appendComponents(r,"RCV",pi.receivers);
                appendComponents(r,"PRV",pi.providers);
                if(pi.requestedPermissions!=null){
                    for(String p:pi.requestedPermissions){
                        if(hit(p) || p.contains("SYSTEM") || p.contains("DUMP") || p.contains("WRITE_SECURE") ||
                           p.contains("READ_LOGS") || p.contains("SIGNATURE")){
                            r.append("PERM ").append(p).append("\n");
                        }
                    }
                }
            }
            r.append("\npackageCandidateCount=").append(count).append("\n");
        }catch(Exception e){
            r.append("PACKAGE_SCAN_ERROR ").append(e).append("\n");
        }
    }

    private boolean anyHit(ComponentInfo[] a){
        if(a==null) return false;
        for(ComponentInfo c:a) if(c!=null && hit(c.name)) return true;
        return false;
    }

    private void appendComponents(StringBuilder r,String tag,ComponentInfo[] a){
        if(a==null) return;
        int n=0;
        for(ComponentInfo c:a){
            if(c==null) continue;
            if(n++>250){ r.append(tag).append(" ...TRUNCATED\n"); break; }
            r.append(tag).append(" ").append(c.name)
             .append(" exported=").append(c.exported);
            if(c.permission!=null) r.append(" perm=").append(c.permission);
            r.append("\n");
        }
    }

    private void execFiltered(StringBuilder r,String[] cmd){
        try{
            Process p=Runtime.getRuntime().exec(cmd);
            BufferedReader br=new BufferedReader(new InputStreamReader(p.getInputStream()));
            String line; int hits=0, total=0;
            while((line=br.readLine())!=null && total++<8000){
                if(hit(line)){
                    r.append(line).append("\n");
                    hits++;
                }
            }
            BufferedReader er=new BufferedReader(new InputStreamReader(p.getErrorStream()));
            String e; int ec=0;
            while((e=er.readLine())!=null && ec++<20) r.append("ERR ").append(e).append("\n");
            r.append("hits=").append(hits).append("\n");
        }catch(Exception e){
            r.append("EXEC_ERROR ").append(Arrays.toString(cmd)).append(" ").append(e).append("\n");
        }
    }

    private void scanDev(StringBuilder r,File root){
        try{
            File[] fs=root.listFiles();
            if(fs==null){ r.append(root).append(" unreadable\n"); return; }
            for(File f:fs){
                String n=f.getName().toLowerCase(Locale.US);
                if(hit(n)||n.startsWith("tty")||n.contains("uart")||n.contains("serial")||n.contains("smd")){
                    r.append(f.getAbsolutePath())
                     .append(" R=").append(f.canRead())
                     .append(" W=").append(f.canWrite())
                     .append("\n");
                }
            }
        }catch(Exception e){ r.append("DEV_ERROR ").append(root).append(" ").append(e).append("\n"); }
    }

    private void scanApkTree(StringBuilder r,File f,int depth){
        if(f==null||!f.exists()||depth>3) return;
        try{
            if(f.isFile()){
                if(hit(f.getAbsolutePath())) r.append(f.getAbsolutePath()).append("\n");
                return;
            }
            if(hit(f.getName())) r.append("DIR ").append(f.getAbsolutePath()).append("\n");
            File[] kids=f.listFiles();
            if(kids==null) return;
            for(File k:kids) scanApkTree(r,k,depth+1);
        }catch(Exception ignored){}
    }

    private String saveReport(String report){
        try{
            File dir=Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
            if(!dir.exists()) dir.mkdirs();
            File f=new File(dir,"VWID_HVAC_DIAG_R5_3.txt");
            FileOutputStream os=new FileOutputStream(f,false);
            os.write(report.getBytes("UTF-8"));
            os.close();
            return f.getAbsolutePath();
        }catch(Exception e){
            try{
                File f=new File(getExternalFilesDir(null),"VWID_HVAC_DIAG_R5_3.txt");
                FileOutputStream os=new FileOutputStream(f,false);
                os.write(report.getBytes("UTF-8"));
                os.close();
                return f.getAbsolutePath()+" (fallback)";
            }catch(Exception e2){
                return "SAVE_FAILED "+e2;
            }
        }
    }
}
