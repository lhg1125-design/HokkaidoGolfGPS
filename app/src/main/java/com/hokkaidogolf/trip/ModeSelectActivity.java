package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class ModeSelectActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(45,119,238));
        SharedPreferences flow=getSharedPreferences("v117_flow",MODE_PRIVATE);

        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(40,56,40,40);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(Color.rgb(247,249,235));

        TextView title=new TextView(this);
        title.setText("참여 방식 선택");
        title.setTextSize(30);
        title.setTextColor(Color.rgb(16,46,72));
        title.setGravity(Gravity.CENTER);
        root.addView(title,new LinearLayout.LayoutParams(-1,-2));

        addMode(root,flow,"MASTER","방 생성 및 플레이 관리");
        addMode(root,flow,"FOLLOWER","MASTER 방 참가");
        addMode(root,flow,"GALLERY","관전 모드");
        setContentView(root);
    }

    private void addMode(LinearLayout root, SharedPreferences flow, String mode, String sub){
        Button b=new Button(this);
        b.setAllCaps(false);
        b.setText(mode+"\n"+sub);
        b.setTextSize(19);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);
        lp.setMargins(0,28,0,0);
        root.addView(b,lp);
        b.setOnClickListener(v->{
            flow.edit().putString("mode",mode).apply();
            setResult(RESULT_OK);
            finish();
        });
    }
}
