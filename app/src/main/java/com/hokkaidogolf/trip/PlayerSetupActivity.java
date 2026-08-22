package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class PlayerSetupActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(255,112,8));
        SharedPreferences flow=getSharedPreferences("v117_flow",MODE_PRIVATE);

        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(40,56,40,40);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(Color.rgb(247,249,235));

        TextView title=new TextView(this);
        title.setText("플레이어 정보");
        title.setTextSize(30);
        title.setTextColor(Color.rgb(16,46,72));
        title.setGravity(Gravity.CENTER);
        root.addView(title,new LinearLayout.LayoutParams(-1,-2));

        EditText[] names=new EditText[4];
        for(int i=0;i<4;i++){
            EditText e=new EditText(this);
            e.setHint("P"+(i+1)+" 이름");
            e.setSingleLine(true);
            e.setText(flow.getString("player_"+(i+1),""));
            e.setTextSize(20);
            LinearLayout.LayoutParams ep=new LinearLayout.LayoutParams(-1,-2);
            ep.setMargins(0,22,0,0);
            root.addView(e,ep);
            names[i]=e;
        }

        Button save=new Button(this);
        save.setText("저장 후 홈으로");
        save.setTextSize(19);
        LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,-2);
        sp.setMargins(0,34,0,0);
        root.addView(save,sp);
        save.setOnClickListener(v->{
            SharedPreferences.Editor ed=flow.edit();
            int count=0;
            for(int i=0;i<4;i++){
                String s=names[i].getText().toString().trim();
                ed.putString("player_"+(i+1),s);
                if(!s.isEmpty()) count++;
            }
            ed.putInt("player_count",count).apply();
            setResult(RESULT_OK);
            finish();
        });
        setContentView(root);
    }
}
