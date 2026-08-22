package com.hokkaidogolf.trip;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.graphics.Color;

public class OfflineMapActivity extends Activity {
 @Override public void onCreate(Bundle b){
  super.onCreate(b);
  TextView v=new TextView(this);
  StringBuilder s=new StringBuilder("Offline Map\nCourse Select\n\n");
  for(int i=1;i<=18;i++) s.append("H").append(i).append("  ");
  v.setText(s.toString());
  v.setTextSize(22);
  v.setTextColor(Color.DKGRAY);
  setContentView(v);
 }
}
