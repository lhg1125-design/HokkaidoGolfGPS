package com.vwid.hvacbridge;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.Color;
import android.widget.*;

public class MainActivity extends Activity {
    TextView status;
    Handler ui = new Handler(Looper.getMainLooper());

    final Runnable refresh = new Runnable() {
        @Override public void run() {
            renderStatus();
            ui.postDelayed(this, 500);
        }
    };

    @Override public void onCreate(Bundle b){
        super.onCreate(b);

        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(26,22,26,22);
        root.setBackgroundColor(Color.rgb(12,12,13));

        TextView title=new TextView(this);
        title.setTextColor(Color.WHITE);
        title.setTextSize(20);
        title.setText("VWID HVAC Bridge R5.7 LIVE\nOwnice TWUtil realtime MCU");
        root.addView(title);

        TextView note=new TextView(this);
        note.setTextColor(Color.rgb(190,190,190));
        note.setTextSize(15);
        note.setText("\nCONFIRMED: TEMP / FAN / AUTO / DUAL / HEATED SEAT\nA/C BIT FIXED: D1 0x80\nAIR MODE: HOLD\n");
        root.addView(note);

        Button start=button("START LIVE MCU");
        Button stop=button("STOP LIVE MCU");
        Button qa=button("QA WIDGET: 22° / 24° / FAN 6 / HEAT 3-2");
        root.addView(start);
        root.addView(stop);
        root.addView(qa);

        ScrollView sv=new ScrollView(this);
        status=new TextView(this);
        status.setTextColor(Color.WHITE);
        status.setTextSize(16);
        status.setTextIsSelectable(true);
        sv.addView(status);
        root.addView(sv,new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,0,1f));

        start.setOnClickListener(v -> {
            getSharedPreferences("hvac",0).edit()
                .putBoolean("live_autostart",true)
                .putString("live_error","")
                .apply();
            Intent s=new Intent(this,TwUtilMcuService.class);
            if(Build.VERSION.SDK_INT>=26) startForegroundService(s);
            else startService(s);
        });

        stop.setOnClickListener(v -> {
            getSharedPreferences("hvac",0).edit()
                .putBoolean("live_autostart",false).apply();
            stopService(new Intent(this,TwUtilMcuService.class));
        });

        qa.setOnClickListener(v -> {
            HvacState s=HvacState.fromFrame("2e 21 05 c4 16 09 0d 32 b7");
            s.save(this);
            HvacWidgetBase.updateAll(this);
            Toast.makeText(this,"QA widget state sent",Toast.LENGTH_SHORT).show();
        });

        setContentView(root);
    }

    private Button button(String s){
        Button b=new Button(this);
        b.setText(s);
        return b;
    }

    private void renderStatus(){
        SharedPreferences p=getSharedPreferences("hvac",0);
        HvacState s=HvacState.load(this);

        long t=p.getLong("live_last_update_ms",0);
        long age=t==0?-1:(System.currentTimeMillis()-t);

        StringBuilder x=new StringBuilder();
        x.append("\nBRIDGE: ").append(p.getString("live_status","IDLE"));
        x.append("\nTWUtil open rc: ").append(p.getInt("live_open_rc",-999));
        x.append("\nRX enable rc: ").append(p.getString("live_rx_enable_rc","-"));
        x.append("\nTW messages: ").append(p.getLong("live_msg_count",0));
        x.append("\nRX debug packets: ").append(p.getLong("live_rx_count",0));
        x.append("\nHVAC 2E 21 05 frames: ").append(p.getLong("live_hvac_count",0));
        x.append("\nLast HVAC: ").append(p.getString("live_last_hvac","-"));

        x.append("\n\nCONFIRMED PARSED");
        x.append("\nDriver: ").append(HvacState.fmtTemp(s.tempL));
        x.append("   Passenger: ").append(HvacState.fmtTemp(s.tempR));
        x.append("\nFAN: ").append(s.fan);
        x.append("\nHVAC POWER: ").append(s.power);\n        x.append("\nAUTO: ").append(s.auto);
        x.append("   A/C: ").append(s.ac);
        x.append("   DUAL: ").append(s.dual);
        x.append("\nHEATED SEAT L/R: ").append(s.heatL).append("/").append(s.heatR);
        x.append("\nAIR MODE: HOLD");
        x.append("\nLast update age: ").append(age<0?"-":age+" ms");

        String err=p.getString("live_error","");
        if(!err.isEmpty()) x.append("\n\nERROR:\n").append(err);

        status.setText(x.toString());
    }

    @Override protected void onResume(){
        super.onResume();
        ui.removeCallbacks(refresh);
        ui.post(refresh);
    }

    @Override protected void onPause(){
        ui.removeCallbacks(refresh);
        super.onPause();
    }
}
