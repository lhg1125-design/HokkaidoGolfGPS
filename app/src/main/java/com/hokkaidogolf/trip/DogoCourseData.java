package com.hokkaidogolf.trip;

import android.content.Context;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Immutable loader for the Step-1 Dogo hard-pass dataset.
 * Source of truth: assets/courses/dogo_cc_v1.json.
 */
public final class DogoCourseData {
    public static final String ASSET_PATH = "courses/dogo_cc_v1.json";

    public static final class Hole {
        public final int hole;
        public final String course;
        public final int par;
        public final int hdcp;
        public final int regularM;
        public final String mapAsset;

        Hole(int hole, String course, int par, int hdcp, int regularM, String mapAsset) {
            this.hole = hole;
            this.course = course;
            this.par = par;
            this.hdcp = hdcp;
            this.regularM = regularM;
            this.mapAsset = mapAsset;
        }
    }

    private final List<Hole> holes;
    private final int totalPar;
    private final int outRegularM;
    private final int inRegularM;
    private final int totalRegularM;

    private DogoCourseData(List<Hole> holes, int totalPar, int outRegularM, int inRegularM, int totalRegularM) {
        this.holes = Collections.unmodifiableList(holes);
        this.totalPar = totalPar;
        this.outRegularM = outRegularM;
        this.inRegularM = inRegularM;
        this.totalRegularM = totalRegularM;
    }

    public static DogoCourseData load(Context context) {
        try (InputStream in = context.getAssets().open(ASSET_PATH)) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            for (int n; (n = in.read(buf)) >= 0; ) out.write(buf, 0, n);
            JSONObject root = new JSONObject(out.toString(StandardCharsets.UTF_8.name()));
            JSONObject layout = root.getJSONObject("layout");
            JSONArray arr = root.getJSONArray("holes");
            ArrayList<Hole> holes = new ArrayList<>(arr.length());
            for (int i = 0; i < arr.length(); i++) {
                JSONObject h = arr.getJSONObject(i);
                holes.add(new Hole(
                        h.getInt("hole"),
                        h.getString("course"),
                        h.getInt("par"),
                        h.getInt("hdcp"),
                        h.getInt("regularM"),
                        h.getString("mapAsset")
                ));
            }
            DogoCourseData data = new DogoCourseData(
                    holes,
                    layout.getInt("par"),
                    layout.getInt("outRegularM"),
                    layout.getInt("inRegularM"),
                    layout.getInt("totalRegularM")
            );
            data.validateOrThrow();
            return data;
        } catch (Exception e) {
            throw new IllegalStateException("Failed to load Dogo course data", e);
        }
    }

    public Hole hole(int number) {
        if (number < 1 || number > holes.size()) throw new IllegalArgumentException("hole=" + number);
        return holes.get(number - 1);
    }

    public List<Hole> holes() { return holes; }
    public int totalPar() { return totalPar; }
    public int outRegularM() { return outRegularM; }
    public int inRegularM() { return inRegularM; }
    public int totalRegularM() { return totalRegularM; }

    /**
     * Hard-pass rules: exactly 18 holes, sequential H1..H18, OUT=H1..H9, IN=H10..H18,
     * PAR 72 and Regular totals 3139/3083/6222. This intentionally prevents H1-copy regressions.
     */
    public void validateOrThrow() {
        if (holes.size() != 18) throw new IllegalStateException("Dogo must have 18 holes");
        int out = 0, in = 0, par = 0;
        for (int i = 0; i < holes.size(); i++) {
            Hole h = holes.get(i);
            int expected = i + 1;
            if (h.hole != expected) throw new IllegalStateException("Hole sequence mismatch at " + expected);
            String expectedCourse = expected <= 9 ? "OUT" : "IN";
            if (!expectedCourse.equals(h.course)) throw new IllegalStateException("Course side mismatch H" + expected);
            if (h.par < 3 || h.par > 5) throw new IllegalStateException("Invalid PAR H" + expected);
            if (h.regularM <= 0) throw new IllegalStateException("Invalid Regular distance H" + expected);
            String expectedAsset = String.format("dogo-h%02d-MASTER-LOCK-CLEAN.png", expected);
            if (!expectedAsset.equals(h.mapAsset)) throw new IllegalStateException("Map asset mismatch H" + expected);
            par += h.par;
            if (expected <= 9) out += h.regularM; else in += h.regularM;
        }
        if (par != 72 || par != totalPar) throw new IllegalStateException("PAR total mismatch: " + par);
        if (out != 3139 || out != outRegularM) throw new IllegalStateException("OUT Regular mismatch: " + out);
        if (in != 3083 || in != inRegularM) throw new IllegalStateException("IN Regular mismatch: " + in);
        if (out + in != 6222 || out + in != totalRegularM) throw new IllegalStateException("Total Regular mismatch: " + (out + in));
    }
}
