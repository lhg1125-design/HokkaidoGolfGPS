package com.vwid.hvacbridge;

import android.app.*;
import android.content.*;
import android.os.Build;
import android.os.IBinder;
import java.io.*;
import java.util.regex.*;

public class LogcatMcuService extends Service {
    volatile boolean run;
    Thread th;
    java.lang.Process proc;
    static final int ID=2105;
    static final Pattern P=Pattern.compile("(?i)(?:RX:\\s*)?(2e\\s+21\\s+05(?:\\s+[0-9a-f]{2}){6})");

    @Override public void onCreate(){
        super.onCreate();
        if(Build.VERSION.SDK_INT>=26){
            NotificationChannel ch=new NotificationChannel("hvac","VWID HVAC Bridge",NotificationManager.IMPORTANCE_MIN);
            getSystemService(NotificationManager.class).createNotificationChannel(ch);
        }
        Notification.Builder nb=Build.VERSION.SDK_INT>=26?new Notification.Builder(this,"hvac"):new Notification.Builder(this);
        startForeground(ID,nb.setSmallIcon(android.R.drawable.stat_notify_sync_noanim)
            .setContentTitle("VWID HVAC Bridge").setContentText("MCU listener active").build());
    }

    @Override public int onStartCommand(Intent i,int f,int id){
        if(th==null){ run=true; th=new Thread(this::loop,"McuLogcat"); th.start(); }
        return START_STICKY;
    }

    void loop(){
        try{
            proc=Runtime.getRuntime().exec(new String[]{"logcat","-v","brief"});
            BufferedReader br=new BufferedReader(new InputStreamReader(proc.getInputStream()));
            String line;
            while(run&&(line=br.readLine())!=null){
                Matcher m=P.matcher(line);
                if(m.find()){
                    try{
                        HvacState s=HvacState.fromFrame(m.group(1));
                        s.save(this);
                        HvacWidgetBase.updateAll(this);
                    }catch(Exception ignored){}
                }
            }
        }catch(Exception e){
            android.util.Log.e("VWID-HVAC","logcat listener failed",e);
        }
    }

    @Override public void onDestroy(){
        run=false;
        if(proc!=null)proc.destroy();
        th=null;
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent i){return null;}
}
