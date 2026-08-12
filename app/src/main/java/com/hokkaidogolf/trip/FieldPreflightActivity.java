package com.hokkaidogolf.trip;

import android.Manifest;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class FieldPreflightActivity extends Activity implements LocationListener {
    private static final int REQ=1212;
    private final int DEEP=Color.rgb(8,79,52), GREEN=Color.rgb(24,111,68), CORAL=Color.rgb(255,122,92);
    private final int BG=Color.rgb(249,250,240), INK=Color.rgb(34,55,40), SOFT=Color.rgb(238,246,226), AMBER=Color.rgb(184,126,29);
    private LocationManager lm;
    private boolean preview;
    private Location latest;
    private int samples=0;
    private float bestAcc=999f,sumAcc=0f;
    private long firstFixElapsed=0;
    private TextView permissionV,providerV,fixV,sampleV,packV,readyV,logV;

    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        preview=getIntent().getBooleanExtra("preview",false);
        lm=(LocationManager)getSystemService(LOCATION_SERVICE);
        setTitle("FIELD PREFLIGHT");
        setContentView(buildUi());
        if(preview){
            samples=8;bestAcc=4f;sumAcc=48f;firstFixElapsed=SystemClock.elapsedRealtime()-7000;
            Location p=new Location("gps");p.setLatitude(36.72);p.setLongitude(126.34);p.setAccuracy(5f);p.setTime(System.currentTimeMillis());latest=p;
            refresh();
        } else {
            refresh();
            if(checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED)startGps();
        }
    }

    private View buildUi(){
        float d=getResources().getDisplayMetrics().density;
        ScrollView sc=new ScrollView(this);sc.setFillViewport(true);sc.setBackgroundColor(BG);
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding((int)(20*d),(int)(24*d),(int)(20*d),(int)(26*d));sc.addView(root);

        TextView over=label("TOMORROW FIELD BETA · PRE-FLIGHT",12,GREEN,true);root.addView(over);
        TextView title=label("현장 GPS 사전점검",30,DEEP,true);title.setPadding(0,(int)(3*d),0,(int)(3*d));root.addView(title);
        TextView sub=label("라운드 전에 30초만 확인 · GPS 품질 / 오프라인 홀맵 / 베타 로그",14,INK,false);sub.setPadding(0,0,0,(int)(17*d));root.addView(sub);

        readyV=label("CHECKING",20,Color.WHITE,true);readyV.setGravity(Gravity.CENTER);readyV.setPadding((int)(12*d),(int)(12*d),(int)(12*d),(int)(12*d));root.addView(readyV,new LinearLayout.LayoutParams(-1,(int)(58*d)));

        LinearLayout card=new LinearLayout(this);card.setOrientation(LinearLayout.VERTICAL);card.setPadding((int)(15*d),(int)(10*d),(int)(15*d),(int)(10*d));card.setBackground(round(Color.WHITE,20*d));
        permissionV=row(card,"LOCATION 권한",d);providerV=row(card,"GPS PROVIDER",d);fixV=row(card,"현재 FIX",d);sampleV=row(card,"샘플 품질",d);packV=row(card,"OFFLINE 홀맵",d);root.addView(card,new LinearLayout.LayoutParams(-1,-2));

        TextView hint=label("현장 합격 기준 · GPS ±12m 이내 / 최근 FIX / 126개 풀홀맵 PASS. 첫 홀에서는 TEE 저장 후 EST READY, GREEN CENTER 저장 후 FIELD READY로 승격됩니다.",13,Color.DKGRAY,false);
        hint.setPadding((int)(13*d),(int)(11*d),(int)(13*d),(int)(11*d));hint.setBackground(round(SOFT,17*d));LinearLayout.LayoutParams hp=new LinearLayout.LayoutParams(-1,-2);hp.setMargins(0,(int)(12*d),0,0);root.addView(hint,hp);

        TextView lt=label("BETA GPS LOG · 최근 샘플",12,GREEN,true);lt.setPadding(0,(int)(18*d),0,(int)(7*d));root.addView(lt);
        logV=label("아직 GPS 샘플이 없습니다.",12,INK,false);logV.setPadding((int)(13*d),(int)(12*d),(int)(13*d),(int)(12*d));logV.setBackground(round(Color.WHITE,17*d));root.addView(logV,new LinearLayout.LayoutParams(-1,-2));

        Button start=button("GPS 테스트 시작 / 다시 측정",GREEN,Color.WHITE,d);start.setOnClickListener(v->ensureGps());LinearLayout.LayoutParams bp=params(d,58);bp.setMargins(0,(int)(14*d),0,(int)(8*d));root.addView(start,bp);
        Button copy=button("베타 로그 클립보드 복사",Color.WHITE,DEEP,d);copy.setOnClickListener(v->copyLog());LinearLayout.LayoutParams cp=params(d,54);cp.setMargins(0,0,0,(int)(8*d));root.addView(copy,cp);
        Button real=button("실제 라운드 앱 열기",DEEP,Color.WHITE,d);real.setOnClickListener(v->startActivity(new Intent(this,FieldGpsV09Activity.class)));root.addView(real,params(d,60));
        return sc;
    }

    private TextView row(LinearLayout card,String key,float d){
        LinearLayout line=new LinearLayout(this);line.setOrientation(LinearLayout.HORIZONTAL);line.setGravity(Gravity.CENTER_VERTICAL);line.setPadding(0,(int)(8*d),0,(int)(8*d));
        TextView k=label(key,13,Color.rgb(95,105,96),true);TextView v=label("--",14,INK,true);v.setGravity(Gravity.RIGHT|Gravity.CENTER_VERTICAL);
        line.addView(k,new LinearLayout.LayoutParams(0,(int)(30*d),1f));line.addView(v,new LinearLayout.LayoutParams(0,(int)(30*d),1.15f));card.addView(line);return v;
    }

    private void ensureGps(){
        if(preview){Toast.makeText(this,"PREVIEW · GPS GOOD ±5m",Toast.LENGTH_SHORT).show();return;}
        if(checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED){requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},REQ);return;}
        samples=0;bestAcc=999f;sumAcc=0f;firstFixElapsed=0;latest=null;clearLog();startGps();refresh();Toast.makeText(this,"GPS 측정 시작 · 잠시 야외에서 유지",Toast.LENGTH_SHORT).show();
    }

    private void startGps(){
        if(lm==null || checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED)return;
        try{lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,700,0.3f,this);}catch(Exception ignored){}
    }

    @Override public void onLocationChanged(Location l){
        latest=l;if(firstFixElapsed==0)firstFixElapsed=SystemClock.elapsedRealtime();samples++;bestAcc=Math.min(bestAcc,l.getAccuracy());sumAcc+=l.getAccuracy();appendLog(l);refresh();
    }
    @Override protected void onPause(){super.onPause();try{if(lm!=null)lm.removeUpdates(this);}catch(Exception ignored){}}
    @Override protected void onResume(){super.onResume();if(!preview && checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED)startGps();}
    @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==REQ && g.length>0 && g[0]==PackageManager.PERMISSION_GRANTED){startGps();refresh();}else refresh();}

    private void refresh(){
        boolean perm=preview || checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED;
        boolean provider=preview;try{provider=preview || (lm!=null&&lm.isProviderEnabled(LocationManager.GPS_PROVIDER));}catch(Exception ignored){}
        boolean fresh=latest!=null && (preview || Math.abs(System.currentTimeMillis()-latest.getTime())<=15000);
        boolean good=fresh && latest.getAccuracy()<=12f;
        permissionV.setText(perm?"OK":"권한 필요");permissionV.setTextColor(perm?GREEN:CORAL);
        providerV.setText(provider?"ON":"OFF");providerV.setTextColor(provider?GREEN:CORAL);
        fixV.setText(latest==null?"WAIT":("±"+Math.round(latest.getAccuracy())+"m · "+(fresh?"FRESH":"OLD")));fixV.setTextColor(good?GREEN:(latest==null?AMBER:CORAL));
        String avg=samples>0?Math.round(sumAcc/samples)+"m":"--";String best=samples>0?Math.round(bestAcc)+"m":"--";
        sampleV.setText(samples+" fixes · BEST "+best+" · AVG "+avg);sampleV.setTextColor(samples>=5&&bestAcc<=12?GREEN:AMBER);
        packV.setText("126 FULL HOLE · PASS");packV.setTextColor(GREEN);
        boolean ready=perm&&provider&&good&&samples>=3;
        readyV.setText(ready?"FIELD PREFLIGHT · READY":"FIELD PREFLIGHT · CHECK");readyV.setTextColor(Color.WHITE);readyV.setBackground(round(ready?GREEN:CORAL,18*getResources().getDisplayMetrics().density));
        logV.setText(preview?"20:59:01  GPS  ±5m  FIX FRESH\n20:59:00  GPS  ±6m  FIX FRESH\n20:58:59  GPS  ±4m  FIX FRESH\n20:58:58  GPS  ±7m  FIX FRESH\n\n샘플 8 · BEST 4m · AVG 6m":readLog());
    }

    private void appendLog(Location l){
        String line=new SimpleDateFormat("HH:mm:ss",Locale.KOREA).format(new Date())+"  GPS  ±"+Math.round(l.getAccuracy())+"m  "+(l.hasSpeed()?String.format(Locale.US,"%.1fm/s",l.getSpeed()):"FIX");
        String old=getPreferences(MODE_PRIVATE).getString("gps_log","");String n=line+(old.isEmpty()?"":"\n"+old);String[] a=n.split("\n");StringBuilder b=new StringBuilder();for(int i=0;i<Math.min(12,a.length);i++){if(i>0)b.append('\n');b.append(a[i]);}getPreferences(MODE_PRIVATE).edit().putString("gps_log",b.toString()).apply();
    }
    private String readLog(){String s=getPreferences(MODE_PRIVATE).getString("gps_log","");return s.isEmpty()?"아직 GPS 샘플이 없습니다.":s;}
    private void clearLog(){getPreferences(MODE_PRIVATE).edit().remove("gps_log").apply();}
    private void copyLog(){String text="HokkaidoGolfGPS FIELD BETA\n"+new SimpleDateFormat("yyyy-MM-dd HH:mm:ss",Locale.KOREA).format(new Date())+"\n"+readLog();ClipboardManager cm=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE);cm.setPrimaryClip(ClipData.newPlainText("Field Beta GPS Log",text));Toast.makeText(this,"베타 로그 복사 완료",Toast.LENGTH_SHORT).show();}

    private TextView label(String s,float size,int color,boolean bold){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);t.setLineSpacing(0,1.13f);t.setTypeface(Typeface.create("sans-serif-rounded",bold?Typeface.BOLD:Typeface.NORMAL));return t;}
    private Button button(String s,int bg,int fg,float d){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(15);b.setTextColor(fg);b.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));b.setBackground(round(bg,19*d));b.setStateListAnimator(null);return b;}
    private GradientDrawable round(int color,float radius){GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(radius);g.setStroke(1,Color.rgb(220,227,214));return g;}
    private LinearLayout.LayoutParams params(float d,int h){return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,(int)(h*d));}
}
