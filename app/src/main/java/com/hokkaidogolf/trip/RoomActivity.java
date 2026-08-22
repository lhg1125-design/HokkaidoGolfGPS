package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

public class RoomActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(139,66,226));
        SharedPreferences flow=getSharedPreferences("v117_flow",MODE_PRIVATE);

        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setPadding(48,72,48,48);
        root.setBackgroundColor(Color.rgb(244,249,224));

        TextView title=new TextView(this);
        title.setText("코드 입력 / 방 생성");
        title.setTextSize(28); title.setTextColor(Color.rgb(16,46,72)); title.setGravity(Gravity.CENTER);
        root.addView(title,new LinearLayout.LayoutParams(-1,-2));

        EditText code=new EditText(this);
        code.setHint("6자리 방 코드"); code.setGravity(Gravity.CENTER); code.setTextSize(24);
        code.setInputType(InputType.TYPE_CLASS_NUMBER);
        code.setText(flow.getString("room_code",""));
        LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2); cp.setMargins(0,70,0,28); root.addView(code,cp);

        Button join=new Button(this); join.setText("방 참가 후 홈으로"); root.addView(join,new LinearLayout.LayoutParams(-1,-2));
        Button create=new Button(this); create.setText("새 방 생성 후 홈으로"); LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(-1,-2); bp.setMargins(0,18,0,0); root.addView(create,bp);

        join.setOnClickListener(v->{
            String c=code.getText().toString().trim();
            if(c.length()!=6){ Toast.makeText(this,"6자리 방 코드를 입력하세요",Toast.LENGTH_SHORT).show(); return; }
            flow.edit().putString("room_code",c).putString("room_action","JOIN").apply();
            setResult(RESULT_OK); finish();
        });
        create.setOnClickListener(v->{
            String c=String.format("%06d",Math.abs((int)(System.currentTimeMillis()%1000000)));
            flow.edit().putString("room_code",c).putString("room_action","CREATE").apply();
            Toast.makeText(this,"ROOM CODE "+c,Toast.LENGTH_SHORT).show();
            setResult(RESULT_OK); finish();
        });
        setContentView(root);
    }
}
