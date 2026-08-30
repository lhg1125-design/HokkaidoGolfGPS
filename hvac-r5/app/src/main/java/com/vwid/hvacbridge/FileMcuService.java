package com.vwid.hvacbridge;

import android.app.*;
import android.content.*;
import android.os.*;
import java.io.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.util.regex.*;

public class FileMcuService extends Service {
    private volatile boolean run;
    private Thread th;
    private static final int ID=2106;
    private static final Pattern P=Pattern.compile("(?i)(2e\\s+21\\s+05(?:\\s+[0-9a-f]{2}){6})");
    private String lastRaw="";

    @Override public void onCreate(){
        super.onCreate();
        if(Build.VERSION.SDK_INT>=26){
            NotificationChannel ch=new NotificationChannel("hvac_file","VWID HVAC File Listener",NotificationManager.IMPORTANCE_MIN);
            getSystemService(NotificationManager.class).createNotificationChannel(ch);
        }
        Notification.Builder nb=Build.VERSION.SDK_INT>=26?new Notification.Builder(this,"hvac_file"):new Notification.Builder(this);
        startForeground(ID,nb.setSmallIcon(android.R.drawable.stat_notify_sync_noanim)
            .setContentTitle("VWID HVAC Bridge R5.2").setContentText("MCU debug listener active").build());
    }

    @Override public int onStartCommand(Intent i,int flags,int id){
        if(th==null){ run=true; th=new Thread(this::loop,"McuFileTail"); th.start(); }
        return START_STICKY;
    }

    private void loop(){
        while(run){
            try{
                String path=getSharedPreferences("hvac",0).getString("mcu_path","");
                if(!path.isEmpty()) scanFile(new File(path));
            }catch(Exception e){
                android.util.Log.e("VWID-HVAC","file listener",e);
            }
            try{Thread.sleep(500);}catch(InterruptedException ignored){}
        }
    }

    private void scanFile(File f) throws Exception {
        if(!f.exists()||!f.canRead())return;
        FileInputStream in=new FileInputStream(f);
        FileChannel ch=in.getChannel();
        long size=ch.size();
        ch.position(Math.max(0,size-262144));
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        byte[] buf=new byte[8192];
        int n;
        while((n=in.read(buf))>0) out.write(buf,0,n);
        in.close();

        String txt=new String(out.toByteArray(),StandardCharsets.UTF_8);
        Matcher m=P.matcher(txt);
        String newest=null;
        while(m.find()) newest=m.group(1);
        if(newest!=null && !newest.equalsIgnoreCase(lastRaw)){
            try{
                HvacState s=HvacState.fromFrame(newest);
                s.save(this);
                HvacWidgetBase.updateAll(this);
                lastRaw=newest;
            }catch(Exception ignored){}
        }
    }

    @Override public void onDestroy(){ run=false; th=null; super.onDestroy(); }
    @Override public IBinder onBind(Intent i){return null;}
}
