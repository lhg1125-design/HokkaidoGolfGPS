package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;

public class ModeSelectActivity extends Activity {
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        Button btn=new Button(this);
        btn.setText("MASTER / FOLLOWER / GALLERY");
        btn.setOnClickListener(v -> startActivity(new Intent(this, RoundReadyActivity.class)));
        setContentView(btn);
    }
}
