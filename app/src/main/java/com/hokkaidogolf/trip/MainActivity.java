package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

public class MainActivity extends Activity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        startActivity(new Intent(this, V117HomeActivity.class));
        finish();
    }
}
