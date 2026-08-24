package com.hokkaidogolf.trip;

import android.content.Context;
import android.content.SharedPreferences;

public class RoundStateStore {
    private static final String PREF = "round_state_v1137";
    private final SharedPreferences pref;

    public RoundStateStore(Context context) {
        pref = context.getSharedPreferences(PREF, Context.MODE_PRIVATE);
    }

    public void save(String json) {
        pref.edit().putString("last_round", json).apply();
    }

    public String load() {
        return pref.getString("last_round", null);
    }

    public void clear() {
        pref.edit().remove("last_round").apply();
    }
}
