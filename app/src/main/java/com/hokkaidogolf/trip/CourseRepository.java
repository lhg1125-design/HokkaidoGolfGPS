package com.hokkaidogolf.trip;

import android.content.Context;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class CourseRepository {
    private final Context context;

    public CourseRepository(Context context) {
        this.context = context.getApplicationContext();
    }

    public List<CourseInfo> loadCourses() {
        List<CourseInfo> result = new ArrayList<>();
        try {
            InputStream is = context.getAssets().open("courses/course_index.json");
            byte[] data = new byte[is.available()];
            is.read(data);
            is.close();
            JSONObject root = new JSONObject(new String(data, StandardCharsets.UTF_8));
            JSONArray courses = root.optJSONArray("courses");
            if (courses == null) return result;
            for (int i = 0; i < courses.length(); i++) {
                JSONObject c = courses.getJSONObject(i);
                result.add(new CourseInfo(
                        c.optString("id"),
                        c.optString("name"),
                        c.optString("country"),
                        c.optInt("holes", 18),
                        c.optString("pack")
                ));
            }
        } catch (Exception ignored) {
        }
        return result;
    }

    public static class CourseInfo {
        public final String id;
        public final String name;
        public final String country;
        public final int holes;
        public final String pack;

        public CourseInfo(String id, String name, String country, int holes, String pack) {
            this.id = id;
            this.name = name;
            this.country = country;
            this.holes = holes;
            this.pack = pack;
        }
    }
}
