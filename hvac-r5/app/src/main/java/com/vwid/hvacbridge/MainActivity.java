package com.vwid.hvacbridge;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.Color;
import android.widget.*;
import java.util.Locale;

public class MainActivity extends Activity {
    TextView status;
    Handler ui = new Handler(Looper.getMainLooper());

    final Runnable refresh = new Runnable() {
        @Override public void run() {
            renderStatus();
            ui.postDelayed(this,500);
        }
    };

    @Override public void onCreate(Bundle b){
        super.onCreate(b);

        // Remove obsolete R5.8 calibration leftovers.
        getSharedPreferences("hvac",0).edit()
            .remove("ac_cal_valid")
            .remove("ac_mask")
            .remove("ac_on_status")
            .remove("ac_off_status")
            .apply();

        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(24,18,24,18);
        root.setBackgroundColor(Color.rgb(12,12,13));

        TextView title=new TextView(this);
        title.setTextColor(Color.WHITE);
        title.setTextSize(20);
        title.setText("VWID HVAC Bridge R5.11 LIVE\nOwnice TWUtil realtime MCU");
        root.addView(title);

        TextView note=new TextView(this);
        note.setTextColor(Color.rgb(190,190,190));
        note.setTextSize(14);
        note.setText("\nCONFIRMED: TEMP / FAN / AUTO / A/C / DUAL / HEATED SEAT\nA/C = D1 bit 0x40\nDUAL = D1 bit 0x04\nAIR: HOLD\nFAST TEMP RX: MCU worker + 70ms coalesced widget\n");
        root.addView(note);

        Button start=button("START LIVE MCU");
        Button stop=button("STOP LIVE MCU");
        root.addView(start);
        root.addView(stop);

        ScrollView sv=new ScrollView(this);
        status=new TextView(this);
        status.setTextColor(Color.WHITE);
        status.setTextSize(15);
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
                .putBoolean("live_autostart",false)
                .apply();
            stopService(new Intent(this,TwUtilMcuService.class));
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
        x.append("\nHVAC frames: ").append(p.getLong("live_hvac_count",0));\n        x.append("\nTEMP changes captured: ").append(p.getLong("temp_change_count",0));\n        x.append("\nTEMP raw L/R: 0x").append(String.format(Locale.US,"%02X",p.getInt("temp_raw_l",0))).append("/0x").append(String.format(Locale.US,"%02X",p.getInt("temp_raw_r",0)));
        x.append("\nLast HVAC: ").append(p.getString("live_last_hvac","-"));
        x.append("\nD1 status: 0x").append(String.format(Locale.US,"%02X",s.statusRaw));

        x.append("\n\nPARSED");
        x.append("\nDriver: ").append(HvacState.fmtTemp(s.tempL));
        x.append("   Passenger: ").append(HvacState.fmtTemp(s.tempR));
        x.append("\nFAN: ").append(s.fan);
        x.append("\nAUTO: ").append(s.auto);
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
