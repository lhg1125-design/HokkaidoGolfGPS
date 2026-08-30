package com.vwid.hvacbridge;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.Color;
import android.widget.*;

public class MainActivity extends Activity {
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
        st.setText("VWID HVAC Bridge R5\n\n1) Grant READ_LOGS once\n2) Start MCU listener\n3) Add theme-matched widget");
        root.addView(st);

        Button start=btn("Start MCU listener");
        Button stop=btn("Stop listener");
        Button qa=btn("QA: 22° / 24° / FAN 6 / VENT 3-2");
        root.addView(start); root.addView(stop); root.addView(qa);

        start.setOnClickListener(v->{
            getSharedPreferences("hvac",0).edit().putBoolean("autostart",true).apply();
            Intent s=new Intent(this,LogcatMcuService.class);
            if(Build.VERSION.SDK_INT>=26)startForegroundService(s); else startService(s);
            st.append("\nListener started");
        });
        stop.setOnClickListener(v->{
            getSharedPreferences("hvac",0).edit().putBoolean("autostart",false).apply();
            stopService(new Intent(this,LogcatMcuService.class));
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

    Button btn(String s){ Button b=new Button(this); b.setText(s); return b; }
}
