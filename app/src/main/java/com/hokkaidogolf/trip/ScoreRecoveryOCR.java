package com.hokkaidogolf.trip;

import android.graphics.Bitmap;

public class ScoreRecoveryOCR {
    public static class Result {
        public boolean success;
        public String rawText;
        public float confidence;
    }

    public Result analyze(Bitmap bitmap) {
        Result result = new Result();
        result.success = false;
        result.rawText = "";
        result.confidence = 0f;
        return result;
    }
}
