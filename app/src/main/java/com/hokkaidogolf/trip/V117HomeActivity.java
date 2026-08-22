package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.graphics.Color;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class V117HomeActivity extends Activity {
    @Override
    public void onCreate(Bundle b){
        super.onCreate(b);
        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setBackgroundColor(Color.rgb(245,240,225));

        TextView title=new TextView(this);
        title.setText("北海道ゴルフ GPS\nRound Start");
        title.setTextSize(28);
        title.setGravity(Gravity.CENTER);
        root.addView(title);

        Button offline=new Button(this);
        offline.setText("Offline Map");
        root.addView(offline);
        offline.setOnClickListener(v->startActivity(new Intent(this, OfflineMapActivity.class)));

        Button play=new Button(this);
        play.setText("Player / Mode Start");
        root.addView(play);
        play.setOnClickListener(v->startActivity(new Intent(this, RoundReadyActivity.class)));

        setContentView(root);
    }
}
