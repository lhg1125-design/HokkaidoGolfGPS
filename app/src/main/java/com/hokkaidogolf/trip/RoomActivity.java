package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class RoomActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(44,171,226));
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
        LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2); cp.setMargins(0,70,0,28); root.addView(code,cp);

        Button join=new Button(this); join.setText("방 참가"); root.addView(join,new LinearLayout.LayoutParams(-1,-2));
        Button create=new Button(this); create.setText("새 방 생성"); LinearLayout.LayoutParams bp=new LinearLayout.LayoutParams(-1,-2); bp.setMargins(0,18,0,0); root.addView(create,bp);

        join.setOnClickListener(v->startActivity(new Intent(this,RoundReadyActivity.class).putExtra("room_code",code.getText().toString())));
        create.setOnClickListener(v->startActivity(new Intent(this,RoundReadyActivity.class).putExtra("create_room",true)));
        setContentView(root);
    }
}
