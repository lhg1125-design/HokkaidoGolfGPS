from pathlib import Path

java=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=java.read_text()

MARK='V1.13.6 REALTIME WEATHER'
if MARK in s:
    print('realtime weather already applied')
    raise SystemExit(0)

# Imports required for a lightweight keyless HTTPS weather fetch.
anchor='import android.view.View;'
imports='''import android.view.View;\nimport java.io.BufferedReader;\nimport java.io.InputStreamReader;\nimport java.net.HttpURLConnection;\nimport java.net.URL;\nimport org.json.JSONObject;'''
if 'import java.net.HttpURLConnection;' not in s:
    if anchor not in s: raise SystemExit('view import anchor missing')
    s=s.replace(anchor,imports,1)

# Live-weather state belongs to GolfView and is updated off the UI thread.
field_anchor='        private String toastText=""; private long toastAt=0;'
fields='''        private String toastText=""; private long toastAt=0;\n        // V1.13.6 REALTIME WEATHER\n        private volatile float liveTempC=Float.NaN, liveWindMs=Float.NaN;\n        private volatile int liveWindDeg=-1, liveWeatherCode=-1;\n        private volatile long liveWeatherAt=0;\n        private volatile boolean liveWeatherLoading=false;\n        private volatile double liveWeatherLat=999,liveWeatherLon=999;'''
if field_anchor not in s: raise SystemExit('weather field anchor missing')
s=s.replace(field_anchor,fields,1)

# Trigger refresh from the actual device GPS fix. 10-minute refresh or >1 km movement.
loc_anchor='            location=l; lastFixElapsed=SystemClock.elapsedRealtime();'
loc_new='''            location=l; lastFixElapsed=SystemClock.elapsedRealtime();\n            maybeRefreshWeatherV1136(l);'''
if loc_anchor not in s: raise SystemExit('location update anchor missing')
s=s.replace(loc_anchor,loc_new,1)

def replace_method(src, signature, body):
    start=src.find(signature)
    if start<0: raise SystemExit('missing method '+signature)
    brace=src.find('{',start)
    depth=0
    end=None
    for i in range(brace,len(src)):
        if src[i]=='{': depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0:
                end=i+1
                break
    if end is None: raise SystemExit('unbalanced method '+signature)
    return src[:start]+body+src[end:]

weather_body=r'''        private void drawApprovedWeatherGpsV1136(Canvas c,float w,float h){
            RectF r=new RectF(w*.580f,h*.004f,w*.978f,h*.052f);
            softShadow(c,r,18);box(c,r,Color.rgb(255,255,248),18);

            float ix=r.left+r.width()*.10f, iy=r.top+r.height()*.34f;
            drawLiveWeatherIconV1136(c,ix,iy,liveWeatherCode);
            String temp=Float.isNaN(liveTempC)?"--°":Math.round(liveTempC)+"°";
            String cond=weatherTextV1136(liveWeatherCode);
            text(c,temp,r.left+r.width()*.22f,r.top+r.height()*.40f,15.0f,INK,true);
            text(c,cond,r.left+r.width()*.35f,r.top+r.height()*.36f,6.2f,Color.rgb(75,90,73),true);

            String wd=windDirV1136(liveWindDeg);
            String ws=Float.isNaN(liveWindMs)?"-- m/s":String.format(java.util.Locale.US,"%.1f m/s",liveWindMs);
            text(c,"➜  "+wd,r.left+r.width()*.08f,r.top+r.height()*.78f,9.4f,Color.rgb(58,115,132),true);
            text(c,ws,r.left+r.width()*.25f,r.top+r.height()*.78f,10.4f,INK,true);

            boolean good=gpsUsable();
            text(c,"GPS",r.left+r.width()*.66f,r.top+r.height()*.34f,10.5f,DEEP,true);
            int bars=1;
            if(location!=null){float a=location.getAccuracy();bars=a<=5?4:(a<=8?3:(a<=12?2:1));}
            for(int i=0;i<4;i++){
                float bh=4+i*4;
                RectF br=new RectF(r.left+r.width()*(.80f+i*.045f),r.top+r.height()*.36f-bh,r.left+r.width()*(.83f+i*.045f),r.top+r.height()*.36f);
                box(c,br,i<bars?Color.rgb(73,166,104):Color.rgb(207,218,205),3);
            }
            text(c,good?"GOOD":"WAIT",r.left+r.width()*.70f,r.top+r.height()*.79f,8.0f,good?Color.rgb(70,153,95):Color.rgb(190,122,62),true);
        }'''
s=replace_method(s,'        private void drawApprovedWeatherGpsV1136(Canvas c,float w,float h){',weather_body)

# Helpers inserted immediately before the weather-card renderer.
insert_at=s.find('        private void drawApprovedWeatherGpsV1136(Canvas c,float w,float h){')
if insert_at<0: raise SystemExit('weather renderer insertion point missing')
helpers=r'''        private void maybeRefreshWeatherV1136(final Location l){
            if(l==null||liveWeatherLoading)return;
            long now=System.currentTimeMillis();
            float moved=Float.MAX_VALUE;
            if(liveWeatherLat<900){
                float[] out=new float[1];
                Location.distanceBetween(liveWeatherLat,liveWeatherLon,l.getLatitude(),l.getLongitude(),out);
                moved=out[0];
            }
            if(now-liveWeatherAt<10*60*1000L && moved<1000f)return;
            liveWeatherLoading=true;
            final double lat=l.getLatitude(),lon=l.getLongitude();
            new Thread(() -> {
                HttpURLConnection con=null;
                try{
                    String u="https://api.open-meteo.com/v1/forecast?latitude="+lat+"&longitude="+lon+"&current=temperature_2m,weather_code,wind_speed_10m,wind_direction_10m&wind_speed_unit=ms&timezone=auto";
                    con=(HttpURLConnection)new URL(u).openConnection();
                    con.setConnectTimeout(6000);con.setReadTimeout(6000);con.setRequestMethod("GET");
                    int rc=con.getResponseCode();if(rc<200||rc>=300)throw new Exception("HTTP "+rc);
                    BufferedReader br=new BufferedReader(new InputStreamReader(con.getInputStream()));
                    StringBuilder sb=new StringBuilder();String line;while((line=br.readLine())!=null)sb.append(line);br.close();
                    JSONObject cur=new JSONObject(sb.toString()).getJSONObject("current");
                    liveTempC=(float)cur.getDouble("temperature_2m");
                    liveWindMs=(float)cur.getDouble("wind_speed_10m");
                    liveWindDeg=(int)Math.round(cur.getDouble("wind_direction_10m"));
                    liveWeatherCode=cur.getInt("weather_code");
                    liveWeatherLat=lat;liveWeatherLon=lon;liveWeatherAt=System.currentTimeMillis();
                    postInvalidate();
                }catch(Exception ignored){
                    // Never substitute fake weather values. Keep '--' or last valid data.
                }finally{
                    if(con!=null)con.disconnect();liveWeatherLoading=false;
                }
            },"weather-v1136").start();
        }

        private String windDirV1136(int deg){
            if(deg<0)return "--";
            String[] d={"N","NE","E","SE","S","SW","W","NW"};
            return d[((int)Math.round((deg%360)/45.0))%8];
        }
        private String weatherTextV1136(int code){
            if(code<0)return liveWeatherLoading?"갱신중":"--";
            if(code==0)return "맑음";
            if(code<=3)return "구름";
            if(code==45||code==48)return "안개";
            if(code>=51&&code<=67)return "비";
            if(code>=71&&code<=77)return "눈";
            if(code>=80&&code<=82)return "소나기";
            if(code>=95)return "뇌우";
            return "흐림";
        }
        private void drawLiveWeatherIconV1136(Canvas c,float x,float y,int code){
            if(code<0||code<=1){
                p.setColor(Color.rgb(246,190,51));c.drawCircle(x,y,7,p);
                p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);p.setColor(Color.rgb(228,171,34));
                for(int i=0;i<8;i++){double a=i*Math.PI/4;float x1=(float)(x+11*Math.cos(a)),y1=(float)(y+11*Math.sin(a)),x2=(float)(x+15*Math.cos(a)),y2=(float)(y+15*Math.sin(a));c.drawLine(x1,y1,x2,y2,p);}p.setStyle(Paint.Style.FILL);return;
            }
            p.setColor(Color.rgb(215,226,229));c.drawCircle(x-5,y+1,7,p);c.drawCircle(x+3,y-2,9,p);c.drawRoundRect(new RectF(x-12,y,x+13,y+8),5,5,p);
            if((code>=51&&code<=67)||(code>=80&&code<=82)||code>=95){p.setColor(Color.rgb(75,166,211));p.setStrokeWidth(2);for(int i=-6;i<=6;i+=6)c.drawLine(x+i,y+11,x+i-2,y+15,p);}
            if(code>=71&&code<=77){p.setColor(Color.WHITE);c.drawCircle(x-5,y+13,2,p);c.drawCircle(x+3,y+15,2,p);}
        }

'''
s=s[:insert_at]+helpers+s[insert_at:]
java.write_text(s)

manifest=Path('app/src/main/AndroidManifest.xml')
m=manifest.read_text()
if 'android.permission.INTERNET' not in m:
    m=m.replace('<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />','<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />\n    <uses-permission android:name="android.permission.INTERNET" />',1)
manifest.write_text(m)

print('applied V1.13.6 realtime weather/wind from GPS coordinates; GPS quality remains native realtime')
