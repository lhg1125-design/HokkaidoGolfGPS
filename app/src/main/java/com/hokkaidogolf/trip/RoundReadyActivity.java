package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

public class RoundReadyActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(0,157,80));
        SharedPreferences flow=getSharedPreferences("v117_flow",MODE_PRIVATE);

        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(44,72,44,44);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(Color.rgb(247,249,235));

        TextView title=new TextView(this);
        title.setText("라운드 준비");
        title.setTextSize(30);
        title.setTextColor(Color.rgb(16,46,72));
        title.setGravity(Gravity.CENTER);
        root.addView(title,new LinearLayout.LayoutParams(-1,-2));

        String course=flow.getString("course_name","");
        String mode=flow.getString("mode","");
        String room=flow.getString("room_code","");
        int players=flow.getInt("player_count",0);

        TextView summary=new TextView(this);
        summary.setText("COURSE  "+(course.isEmpty()?"미선택":course)+"\n\nPLAYER  "+players+"명\n\nMODE  "+(mode.isEmpty()?"미선택":mode)+"\n\nROOM  "+(room.isEmpty()?"미설정":room));
        summary.setTextSize(19);
        summary.setTextColor(Color.rgb(48,64,55));
        LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,-2); sp.setMargins(0,48,0,40); root.addView(summary,sp);

        Button btn=new Button(this);
        btn.setText("ROUND START");
        btn.setTextSize(20);
        root.addView(btn,new LinearLayout.LayoutParams(-1,-2));
        btn.setOnClickListener(v->{
            if(course.isEmpty()){
                Toast.makeText(this,"골프장을 먼저 선택하세요",Toast.LENGTH_SHORT).show();
                finish();
                return;
            }
            Intent i=new Intent(this,FieldGpsV09Activity.class);
            i.putExtra("course_id",flow.getString("course_id",""));
            i.putExtra("course_pack",flow.getString("course_pack",""));
            startActivity(i);
        });
        setContentView(root);
    }
}
