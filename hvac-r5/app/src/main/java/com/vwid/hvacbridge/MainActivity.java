package com.vwid.hvacbridge;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.Color;
import android.net.Uri;
import android.widget.*;

public class MainActivity extends Activity {
    static final int PICK_MCU=501;
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
        st.setText("VWID HVAC Bridge R5.1\n\nNO CABLE / NO ADB\n1) Select live _MCUdebug log file\n2) Add theme-matched widget");
        root.addView(st);

        Button pick=btn("SELECT MCUDEBUG LOG + START");
        Button stop=btn("STOP FILE LISTENER");
        Button qa=btn("QA: 22° / 24° / FAN 6 / VENT 3-2");
        root.addView(pick); root.addView(stop); root.addView(qa);

        pick.setOnClickListener(v->{
            Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("text/*");
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
            startActivityForResult(i,PICK_MCU);
        });

        stop.setOnClickListener(v->{
            getSharedPreferences("hvac",0).edit().putBoolean("file_autostart",false).apply();
            stopService(new Intent(this,FileMcuService.class));
            st.append("\nFile listener stopped");
        });

        qa.setOnClickListener(v->{
            HvacState s=HvacState.fromFrame("2e 21 05 c4 16 09 0d 32 b7");
            s.save(this);
            HvacWidgetBase.updateAll(this);
            st.append("\nQA state sent");
        });
        setContentView(root);
    }

    @Override protected void onActivityResult(int req,int result,Intent data){
        super.onActivityResult(req,result,data);
        if(req==PICK_MCU && result==RESULT_OK && data!=null && data.getData()!=null){
            Uri u=data.getData();
            try{
                final int flags=data.getFlags() & (Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                getContentResolver().takePersistableUriPermission(u,flags & Intent.FLAG_GRANT_READ_URI_PERMISSION);
            }catch(Exception ignored){}
            getSharedPreferences("hvac",0).edit().putString("mcu_uri",u.toString()).putBoolean("file_autostart",true).apply();
            Intent s=new Intent(this,FileMcuService.class);
            if(Build.VERSION.SDK_INT>=26)startForegroundService(s); else startService(s);
            st.append("\nMCU file selected + listener started");
        }
    }

    Button btn(String s){ Button b=new Button(this); b.setText(s); return b; }
}
