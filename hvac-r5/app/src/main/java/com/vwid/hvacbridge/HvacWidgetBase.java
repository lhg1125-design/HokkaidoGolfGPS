package com.vwid.hvacbridge;
import android.appwidget.*;import android.content.*;import android.widget.*;import android.content.ComponentName;

public abstract class HvacWidgetBase extends AppWidgetProvider {
    abstract HvacRenderer.Theme theme();
    @Override public void onUpdate(Context c,AppWidgetManager m,int[] ids){for(int id:ids) updateOne(c,m,id,theme());}
    static void updateOne(Context c,AppWidgetManager m,int id,HvacRenderer.Theme t){RemoteViews rv=new RemoteViews(c.getPackageName(),R.layout.widget_hvac);rv.setImageViewBitmap(R.id.hvacImage,HvacRenderer.render(HvacState.load(c),t));m.updateAppWidget(id,rv);}
    public static void updateAll(Context c){AppWidgetManager m=AppWidgetManager.getInstance(c); updateProvider(c,m,HvacWidgetLightBrown.class,HvacRenderer.Theme.LIGHT_BROWN);updateProvider(c,m,HvacWidgetDeepRed.class,HvacRenderer.Theme.DEEP_RED);updateProvider(c,m,HvacWidgetDarkLavender.class,HvacRenderer.Theme.DARK_LAVENDER);}
    private static void updateProvider(Context c,AppWidgetManager m,Class<?> k,HvacRenderer.Theme t){int[]ids=m.getAppWidgetIds(new ComponentName(c,k));for(int id:ids)updateOne(c,m,id,t);}
}
