package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.LinearLayout;

import java.util.List;

public class CourseSelectActivity extends Activity {
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);

        CourseRepository repo = new CourseRepository(this);
        List<CourseRepository.CourseInfo> courses = repo.loadCourses();

        for (CourseRepository.CourseInfo c : courses) {
            Button btn = new Button(this);
            btn.setText(c.name + "\n" + c.country + " · " + c.holes + " Holes");
            btn.setOnClickListener(v -> {
                Intent i = new Intent(this, FieldGpsV09Activity.class);
                i.putExtra("course_id", c.id);
                i.putExtra("course_pack", c.pack);
                startActivity(i);
            });
            root.addView(btn);
        }

        setContentView(root);
    }
}
