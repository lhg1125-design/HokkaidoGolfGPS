package com.hokkaidogolf.trip;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.location.LocationManager;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Toast;

/**
 * V1.17 LOCKED HOME
 * Visual pixels come from the approved Hokkaido GPS Caddie home asset.
 * This class only overlays touch hit-zones and never redraws the concept UI.
 */
public class V117HomeActivity extends Activity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(18, 132, 74));
        getWindow().setNavigationBarColor(Color.rgb(38, 72, 36));
        setContentView(new LockedHomeView());
    }

    private final class LockedHomeView extends View {
        private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
        private final Bitmap locked;

        LockedHomeView() {
            super(V117HomeActivity.this);
            int id = getResources().getIdentifier("v117_home_lock", "drawable", getPackageName());
            locked = id == 0 ? null : BitmapFactory.decodeResource(getResources(), id);
            setBackgroundColor(Color.rgb(246, 249, 231));
        }

        @Override protected void onDraw(Canvas c) {
            super.onDraw(c);
            if (locked != null) {
                c.drawBitmap(locked, null, new RectF(0, 0, getWidth(), getHeight()), p);
                return;
            }
            p.setColor(Color.rgb(18, 132, 74));
            p.setTextAlign(Paint.Align.CENTER);
            p.setTextSize(Math.max(26f, getWidth() * .055f));
            c.drawText("HOKKAIDO GOLF GPS CADDIE", getWidth() / 2f, getHeight() / 2f, p);
        }

        @Override public boolean onTouchEvent(MotionEvent e) {
            if (e.getAction() != MotionEvent.ACTION_UP) return true;
            final float nx = e.getX() / Math.max(1f, getWidth());
            final float ny = e.getY() / Math.max(1f, getHeight());

            if (nx >= .04f && nx <= .96f) {
                if (ny >= .335f && ny < .440f) return open(CourseSelectActivity.class);
                if (ny >= .440f && ny < .545f) return open(PlayerSetupActivity.class);
                if (ny >= .545f && ny < .650f) return open(ModeSelectActivity.class);
                if (ny >= .650f && ny < .755f) return open(RoomActivity.class);
                if (ny >= .755f && ny < .850f) return open(RoundReadyActivity.class);
            }

            if (ny >= .855f) {
                if (nx < .25f) return open(OfflineMapActivity.class);
                if (nx < .50f) { showGps(); return true; }
                // V1.17 spec removes the old real-time-distance shortcut.
                if (nx < .75f) return true;
                Toast.makeText(V117HomeActivity.this,
                        "스코어 관리는 GPS Play 화면과 연결됩니다.", Toast.LENGTH_SHORT).show();
                return true;
            }
            return true;
        }

        private boolean open(Class<?> cls) {
            startActivity(new Intent(V117HomeActivity.this, cls));
            return true;
        }
    }

    private void showGps() {
        boolean permission = checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
                == PackageManager.PERMISSION_GRANTED;
        LocationManager lm = (LocationManager) getSystemService(LOCATION_SERVICE);
        boolean enabled = false;
        try { enabled = lm != null && lm.isProviderEnabled(LocationManager.GPS_PROVIDER); }
        catch (Exception ignored) {}
        Toast.makeText(this, permission && enabled ? "GPS READY" : "GPS 권한/위치 서비스를 확인하세요",
                Toast.LENGTH_SHORT).show();
    }
}
