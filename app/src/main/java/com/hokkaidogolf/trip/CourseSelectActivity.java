package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.List;

public class CourseSelectActivity extends Activity {
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().setStatusBarColor(Color.rgb(18,132,74));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(40, 56, 40, 40);
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(Color.rgb(247,249,235));

        TextView title = new TextView(this);
        title.setText("골프장 선택");
        title.setTextSize(30);
        title.setTextColor(Color.rgb(16,46,72));
        title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(-1,-2));

        CourseRepository repo = new CourseRepository(this);
        List<CourseRepository.CourseInfo> courses = repo.loadCourses();
        SharedPreferences flow = getSharedPreferences("v117_flow", MODE_PRIVATE);
        SharedPreferences state = getSharedPreferences("state_v09", MODE_PRIVATE);

        for (int n = 0; n < courses.size(); n++) {
            CourseRepository.CourseInfo c = courses.get(n);
            final int index = n;
            Button btn = new Button(this);
            btn.setAllCaps(false);
            btn.setText(c.name + "\n" + c.country + " · " + c.holes + " Holes");
            btn.setTextSize(19);
            LinearLayout.LayoutParams bp = new LinearLayout.LayoutParams(-1, -2);
            bp.setMargins(0, 28, 0, 0);
            root.addView(btn, bp);
            btn.setOnClickListener(v -> {
                flow.edit()
                        .putString("course_id", c.id)
                        .putString("course_name", c.name)
                        .putString("course_pack", c.pack)
                        .putInt("course_index", index)
                        .apply();
                state.edit().putInt("selected", index).putInt("variant", 0).apply();
                setResult(RESULT_OK);
                finish();
            });
        }

        setContentView(root);
    }
}
