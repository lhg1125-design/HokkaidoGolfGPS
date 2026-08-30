package com.vwid.hvacbridge;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.UserManager;
import java.util.Map;

public final class HvacStore {
    private HvacStore(){}

    public static SharedPreferences prefs(Context c) {
        Context app=c.getApplicationContext();

        if(Build.VERSION.SDK_INT>=24) {
            Context dp=app.createDeviceProtectedStorageContext();
            SharedPreferences out=dp.getSharedPreferences("hvac",0);

            if(isUserUnlocked(app) && !out.getBoolean("_dp_migrated",false)) {
                try {
                    SharedPreferences legacy=app.getSharedPreferences("hvac",0);
                    SharedPreferences.Editor e=out.edit();
                    for(Map.Entry<String,?> x:legacy.getAll().entrySet()) {
                        if(out.contains(x.getKey())) continue;
                        Object v=x.getValue();
                        if(v instanceof String) e.putString(x.getKey(),(String)v);
                        else if(v instanceof Integer) e.putInt(x.getKey(),(Integer)v);
                        else if(v instanceof Long) e.putLong(x.getKey(),(Long)v);
                        else if(v instanceof Float) e.putFloat(x.getKey(),(Float)v);
                        else if(v instanceof Boolean) e.putBoolean(x.getKey(),(Boolean)v);
                    }
                    e.putBoolean("_dp_migrated",true).commit();
                } catch(Throwable ignored) {}
            }
            return out;
        }

        return app.getSharedPreferences("hvac",0);
    }

    private static boolean isUserUnlocked(Context c) {
        if(Build.VERSION.SDK_INT<24) return true;
        try {
            UserManager um=(UserManager)c.getSystemService(Context.USER_SERVICE);
            return um==null || um.isUserUnlocked();
        } catch(Throwable e) {
            return true;
        }
    }
}
