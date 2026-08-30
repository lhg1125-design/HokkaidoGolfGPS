package com.vwid.hvacbridge;

import android.Manifest;
import android.app.*;
import android.os.*;
import android.content.*;
import android.content.pm.*;
import android.graphics.Color;
import android.widget.*;
import java.io.*;
import java.util.zip.*;

public class MainActivity extends Activity {
    static final int REQ_STORAGE=904;
    TextView out;
    final String[] targets = new String[]{
        "com.tw.carchoose",
        "com.tw.service",
        "com.tw.core",
        "com.tw.jar1",
        "com.tw.service.xt"
    };

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(24,20,24,20);
        root.setBackgroundColor(Color.rgb(12,12,13));

        TextView title=new TextView(this);
        title.setTextColor(Color.WHITE);
        title.setTextSize(20);
        title.setText("VWID HVAC R5.4 EXTRACT\nMCU/CAN SYSTEM APK EXPORTER");
        root.addView(title);

        Button go=new Button(this);
        go.setText("EXPORT MCU SYSTEM APKs TO ONE ZIP");
        root.addView(go);

        out=new TextView(this);
        out.setTextColor(Color.rgb(225,225,225));
        out.setTextSize(15);
        out.setText("Exports:\ncom.tw.carchoose\ncom.tw.service\ncom.tw.core\ncom.tw.jar1\ncom.tw.service.xt\n\nOutput: Download/VWID_HVAC_SYSTEM_APKS_R5_4.zip");
        ScrollView sv=new ScrollView(this);
        sv.addView(out);
        root.addView(sv,new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,0,1f));

        go.setOnClickListener(v->ensureAndExport());
        setContentView(root);
    }

    private void ensureAndExport(){
        if(Build.VERSION.SDK_INT>=23 &&
           checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)!=PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            },REQ_STORAGE);
        } else exportNow();
    }

    @Override public void onRequestPermissionsResult(int req,String[] p,int[] g){
        super.onRequestPermissionsResult(req,p,g);
        if(req==REQ_STORAGE) exportNow();
    }

    private void exportNow(){
        out.setText("Exporting...\n");
        new Thread(()->{
            String result=doExport();
            runOnUiThread(()->out.setText(result));
        },"HVAC-APK-EXPORT").start();
    }

    private String doExport(){
        StringBuilder log=new StringBuilder();
        File dir=Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
        if(!dir.exists()) dir.mkdirs();
        File zipFile=new File(dir,"VWID_HVAC_SYSTEM_APKS_R5_4.zip");

        try{
            ZipOutputStream zos=new ZipOutputStream(new BufferedOutputStream(new FileOutputStream(zipFile,false)));
            PackageManager pm=getPackageManager();

            for(String pkg:targets){
                log.append("\n[").append(pkg).append("]\n");
                try{
                    PackageInfo pi=pm.getPackageInfo(pkg,0);
                    ApplicationInfo ai=pi.applicationInfo;
                    log.append("version=").append(pi.versionName).append("\n");
                    log.append("source=").append(ai.sourceDir).append("\n");

                    addFile(zos,new File(ai.sourceDir),pkg+"/base.apk",log);

                    if(ai.splitSourceDirs!=null){
                        for(int i=0;i<ai.splitSourceDirs.length;i++){
                            String p=ai.splitSourceDirs[i];
                            addFile(zos,new File(p),pkg+"/split_"+i+".apk",log);
                        }
                    }
                }catch(Exception e){
                    log.append("ERROR ").append(e).append("\n");
                }
            }

            ZipEntry info=new ZipEntry("VWID_HVAC_R5_4_MANIFEST.txt");
            zos.putNextEntry(info);
            byte[] meta=log.toString().getBytes("UTF-8");
            zos.write(meta);
            zos.closeEntry();
            zos.finish();
            zos.close();

            log.append("\nDONE\n")
               .append(zipFile.getAbsolutePath())
               .append("\nSIZE=").append(zipFile.length()).append(" bytes");
        }catch(Exception e){
            log.append("\nEXPORT FAILED: ").append(e);
        }
        return log.toString();
    }

    private void addFile(ZipOutputStream zos,File src,String entryName,StringBuilder log) throws Exception{
        if(!src.exists()){
            log.append("MISSING ").append(src.getAbsolutePath()).append("\n");
            return;
        }
        if(!src.canRead()){
            log.append("NOT READABLE ").append(src.getAbsolutePath()).append("\n");
            return;
        }

        ZipEntry e=new ZipEntry(entryName);
        e.setTime(src.lastModified());
        zos.putNextEntry(e);
        FileInputStream in=new FileInputStream(src);
        byte[] buf=new byte[65536];
        int n;
        long total=0;
        while((n=in.read(buf))>0){
            zos.write(buf,0,n);
            total+=n;
        }
        in.close();
        zos.closeEntry();
        log.append("OK ").append(entryName).append(" ").append(total).append(" bytes\n");
    }
}
