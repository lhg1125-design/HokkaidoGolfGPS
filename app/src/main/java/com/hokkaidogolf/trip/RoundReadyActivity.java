package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;

public class RoundReadyActivity extends Activity {
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        Button btn=new Button(this);
        btn.setText("ROUND START");
        btn.setOnClickListener(v -> startActivity(new Intent(this, FieldGpsV09Activity.class)));
        setContentView(btn);
    }
}
