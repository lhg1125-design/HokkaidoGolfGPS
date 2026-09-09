package com.vwid.hvaccontrolprobe;

import android.app.Activity;
import android.graphics.Color;
import android.os.*;
import android.view.View;
import android.widget.*;
import java.lang.reflect.*;
import java.text.SimpleDateFormat;
import java.util.*;

public final class MainActivity extends Activity {
    private TextView stateText, modelText, logText;
    private Button connectButton, queryButton;
    private TwBridge bridge;
    private HvacState state = new HvacState();

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();
        bridge = new TwBridge(this::onBridgeEvent);
        refreshButtons();
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18), dp(12), dp(18), dp(12));
        root.setBackgroundColor(Color.rgb(15,16,18));

        TextView title = new TextView(this);
        title.setText("VWID HVAC MODEL TRACE 0.2");
        title.setTextSize(21);
        title.setTextColor(Color.WHITE);
        root.addView(title);

        TextView note = new TextView(this);
        note.setText("차량 제어 명령은 보내지 않습니다. 현재 Ownice/CanBox 모델 응답과 HVAC RX만 수집합니다.\n물리 FAN 버튼은 차량→CAN→헤드유닛 RX이므로 Android TX 프레임이 보이지 않는 것이 정상일 수 있습니다.");
        note.setTextSize(13);
        note.setTextColor(Color.rgb(205,205,205));
        note.setPadding(0,dp(5),0,dp(7));
        root.addView(note);

        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        connectButton = button(row,"1. CONNECT + MODEL QUERY",v -> connect());
        queryButton = button(row,"2. QUERY AGAIN",v -> queryModel());
        root.addView(row);

        modelText = new TextView(this);
        modelText.setText("MODEL: waiting");
        modelText.setTextSize(18);
        modelText.setTextColor(Color.rgb(255,190,115));
        modelText.setPadding(0,dp(6),0,dp(3));
        root.addView(modelText);

        stateText = new TextView(this);
        stateText.setText("STATE: waiting live HVAC RX");
        stateText.setTextSize(17);
        stateText.setTextColor(Color.WHITE);
        stateText.setPadding(0,dp(2),0,dp(5));
        root.addView(stateText);

        ScrollView scroll = new ScrollView(this);
        logText = new TextView(this);
        logText.setTextSize(13);
        logText.setTextColor(Color.rgb(190,205,215));
        logText.setTextIsSelectable(true);
        scroll.addView(logText);
        root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        setContentView(root);
    }

    private Button button(LinearLayout parent,String text,View.OnClickListener l) {
        Button b=new Button(this);
        b.setText(text); b.setAllCaps(false); b.setOnClickListener(l);
        parent.addView(b,new LinearLayout.LayoutParams(0,-2,1));
        return b;
    }
    private int dp(int v){return (int)(v*getResources().getDisplayMetrics().density+0.5f);}

    private void refreshButtons() {
        boolean connected=bridge!=null && bridge.isConnected();
        if(connectButton!=null) connectButton.setEnabled(!connected);
        if(queryButton!=null) queryButton.setEnabled(connected);
    }

    private void connect() {
        append("CONNECT requested");
        connectButton.setEnabled(false);
        bridge.connect();
    }

    private void queryModel() {
        if(bridge==null || !bridge.isConnected()) return;
        int rc=bridge.queryModel();
        append("MODEL QUERY · TWUtil.write(0x010A,0x00FF) · rc="+rc);
    }

    private void onBridgeEvent(TwBridge.Event e) {
        runOnUiThread(() -> {
            switch(e.kind) {
                case TwBridge.Event.CONNECTED:
                    append("CONNECTED · open rc="+e.rc+" · RX-debug rc="+e.extra);
                    refreshButtons();
                    int rc=bridge.queryModel();
                    append("AUTO MODEL QUERY · TWUtil.write(0x010A,0x00FF) · rc="+rc);
                    break;
                case TwBridge.Event.MODEL:
                    modelText.setText("MODEL: "+e.text);
                    append("MODEL RESPONSE · "+e.text);
                    break;
                case TwBridge.Event.RX_STATE:
                    HvacState parsed=HvacState.fromPayload(e.payload);
                    if(parsed.valid) {
                        state=parsed;
                        stateText.setText(state.summary()+"\nRX: "+e.text);
                        append("LIVE HVAC RX · "+e.text);
                    }
                    break;
                case TwBridge.Event.RAW_EVENT:
                    append(e.text);
                    break;
                case TwBridge.Event.ERROR:
                    append("ERROR · "+e.text);
                    refreshButtons();
                    break;
            }
        });
    }

    private void append(String s) {
        String old=logText.getText().toString();
        String line=new SimpleDateFormat("HH:mm:ss.SSS",Locale.US).format(new Date())+"  "+s;
        if(old.length()>13000) old=old.substring(old.length()-9500);
        logText.setText(old.length()==0?line:old+"\n"+line);
    }

    @Override protected void onDestroy() {
        if(bridge!=null) bridge.close();
        super.onDestroy();
    }

    static final class HvacState {
        boolean valid,ac,auto,dual;
        int fan,tempRawL,tempRawR,heatL,heatR;
        float tempL,tempR;
        static HvacState fromPayload(byte[] p) {
            HvacState s=new HvacState();
            if(p==null || p.length<5) return s;
            int d1=p[0]&255,d2=p[1]&255,d3=p[2]&255,d4=p[3]&255,d5=p[4]&255;
            s.valid=true;
            s.ac=(d1&0x40)!=0; s.auto=(d1&0x18)!=0; s.dual=(d1&0x04)!=0;
            s.fan=d2&15; s.tempRawL=d3; s.tempRawR=d4;
            s.tempL=(d3+35)/2f; s.tempR=(d4+35)/2f;
            s.heatL=(d5>>4)&15; s.heatR=d5&15;
            return s;
        }
        String summary() {
            return String.format(Locale.US,"STATE  FAN %d   TEMP L %.1f°   TEMP R %.1f°   A/C %s   AUTO %s   DUAL %s   HEAT %d/%d",
                fan,tempL,tempR,ac?"ON":"OFF",auto?"ON":"OFF",dual?"ON":"OFF",heatL,heatR);
        }
    }

    static final class TwBridge {
        interface Listener { void event(Event e); }
        static final class Event {
            static final int CONNECTED=1, ERROR=2, MODEL=3, RX_STATE=4, RAW_EVENT=5;
            final int kind,rc,extra; final String text; final byte[] payload;
            Event(int kind,String text,int rc,int extra,byte[] payload){this.kind=kind;this.text=text;this.rc=rc;this.extra=extra;this.payload=payload;}
            static Event text(int kind,String text){return new Event(kind,text,0,0,null);}
        }

        private final Listener listener;
        private HandlerThread thread;
        private Handler handler;
        private Object tw;
        private Class<?> cls;
        private Method write2,write3,removeHandler,stop,close;
        private volatile boolean connected=false;
        private final byte[] stream=new byte[4096];
        private int streamLen=0;

        TwBridge(Listener listener){this.listener=listener;}
        boolean isConnected(){return connected;}

        void connect() {
            if(thread!=null) return;
            thread=new HandlerThread("VWID-HVAC-MODEL-TRACE",android.os.Process.THREAD_PRIORITY_DISPLAY);
            thread.start();
            handler=new Handler(thread.getLooper()) {
                @Override public void handleMessage(Message msg){onMessage(msg);}
            };
            handler.post(this::doConnect);
        }

        private void doConnect() {
            try {
                cls=Class.forName("android.tw.john.TWUtil");
                try {
                    Constructor<?> c=cls.getDeclaredConstructor(); c.setAccessible(true); tw=c.newInstance();
                } catch(NoSuchMethodException e) {
                    Constructor<?> c=cls.getDeclaredConstructor(int.class); c.setAccessible(true); tw=c.newInstance(0x11);
                }
                short[] events={(short)0x010A,(short)0x0501,(short)0x050D};
                Object orc=cls.getMethod("open",short[].class).invoke(tw,(Object)events);
                int openRc=orc instanceof Number?((Number)orc).intValue():0;
                if(openRc!=0) throw new IllegalStateException("TWUtil.open rc="+openRc);
                cls.getMethod("start").invoke(tw);
                cls.getMethod("addHandler",String.class,Handler.class).invoke(tw,"VWIDHVACMODELTRACE",handler);
                write2=cls.getMethod("write",int.class,int.class);
                write3=cls.getMethod("write",int.class,int.class,int.class);
                removeHandler=cls.getMethod("removeHandler",String.class);
                stop=cls.getMethod("stop");
                close=cls.getMethod("close");
                Object rr=write3.invoke(tw,0x050D,1,1);
                int debugRc=rr instanceof Number?((Number)rr).intValue():0;
                connected=true;
                listener.event(new Event(Event.CONNECTED,"connected",openRc,debugRc,null));
            } catch(Throwable e) {
                connected=false;
                listener.event(Event.text(Event.ERROR,rootMessage(e)));
            }
        }

        int queryModel() {
            if(!connected || tw==null || write2==null) return -999;
            try {
                Object r=write2.invoke(tw,0x010A,0x00FF);
                return r instanceof Number?((Number)r).intValue():0;
            } catch(Throwable e) {
                listener.event(Event.text(Event.ERROR,"model query failed: "+rootMessage(e)));
                return -998;
            }
        }

        private void onMessage(Message msg) {
            try {
                if(msg.what==0x010A) {
                    String obj=describeObj(msg.obj);
                    String text=String.format(Locale.US,"what=010A arg1=%d(0x%X) arg2=%d(0x%X) obj=%s",msg.arg1,msg.arg1,msg.arg2,msg.arg2,obj);
                    listener.event(Event.text(Event.MODEL,text));
                    return;
                }
                if(msg.what==0x0501) {
                    String text=String.format(Locale.US,"EVENT 0501 arg1=%d(0x%X) arg2=%d obj=%s",msg.arg1,msg.arg1,msg.arg2,describeObj(msg.obj));
                    listener.event(Event.text(Event.RAW_EVENT,text));
                    if(msg.arg1==0x21 && msg.obj instanceof byte[]) {
                        byte[] p=(byte[])msg.obj;
                        listener.event(new Event(Event.RX_STATE,"0501/21 "+hex(p,0,p.length),0,0,Arrays.copyOf(p,p.length)));
                    }
                    return;
                }
                if(msg.what!=0x050D) {
                    listener.event(Event.text(Event.RAW_EVENT,String.format(Locale.US,"EVENT what=%04X arg1=%d arg2=%d obj=%s",msg.what,msg.arg1,msg.arg2,describeObj(msg.obj))));
                    return;
                }
                if(!(msg.obj instanceof byte[])) {
                    listener.event(Event.text(Event.RAW_EVENT,"MCUdebug non-byte obj="+describeObj(msg.obj)));
                    return;
                }
                byte[] raw=(byte[])msg.obj;
                if(raw.length==0) return;
                int kind=raw[0]&255;
                String label=kind==1?"RX":kind==2?"TX":kind==3?"TEXT":"K"+kind;
                listener.event(Event.text(Event.RAW_EVENT,"MCUdebug "+label+" · "+hex(raw,1,Math.max(0,raw.length-1))));
                if(kind==1 && raw.length>1) feed(raw,1,raw.length-1);
            } catch(Throwable e) {
                listener.event(Event.text(Event.ERROR,"handler: "+rootMessage(e)));
            }
        }

        private void feed(byte[] b,int off,int len) {
            if(len<=0) return;
            if(len>stream.length){off+=len-stream.length;len=stream.length;}
            if(streamLen+len>stream.length) streamLen=0;
            System.arraycopy(b,off,stream,streamLen,len); streamLen+=len;
            while(streamLen>=4) {
                int st=0; while(st<streamLen && (stream[st]&255)!=0x2E) st++;
                if(st>0) remove(st);
                if(streamLen<4) return;
                int dl=stream[2]&255,total=dl+4;
                if(dl>96 || total<5){remove(1);continue;}
                if(streamLen<total) return;
                int sum=0; for(int i=0;i<total;i++) sum+=stream[i]&255;
                if((sum&255)!=0x2D){remove(1);continue;}
                if((stream[1]&255)==0x21 && dl>=5) {
                    byte[] p=Arrays.copyOfRange(stream,3,3+dl);
                    listener.event(new Event(Event.RX_STATE,hex(stream,0,total),0,0,p));
                }
                remove(total);
            }
        }

        private void remove(int n) {
            if(n>=streamLen){streamLen=0;return;}
            System.arraycopy(stream,n,stream,0,streamLen-n); streamLen-=n;
        }

        void close() {
            connected=false;
            try{if(tw!=null&&write3!=null)write3.invoke(tw,0x050D,1,0);}catch(Throwable ignored){}
            try{if(tw!=null&&removeHandler!=null)removeHandler.invoke(tw,"VWIDHVACMODELTRACE");}catch(Throwable ignored){}
            try{if(tw!=null&&stop!=null)stop.invoke(tw);}catch(Throwable ignored){}
            try{if(tw!=null&&close!=null)close.invoke(tw);}catch(Throwable ignored){}
            if(thread!=null){thread.quitSafely();thread=null;}
        }

        private static String describeObj(Object o) {
            if(o==null) return "null";
            if(o instanceof byte[]) return "byte["+((byte[])o).length+"] "+hex((byte[])o,0,((byte[])o).length);
            return o.getClass().getName()+" «"+String.valueOf(o)+"»";
        }
        private static String hex(byte[] b,int o,int l) {
            StringBuilder s=new StringBuilder(); int end=Math.min(b.length,o+l);
            for(int i=o;i<end;i++){if(s.length()>0)s.append(' ');s.append(String.format(Locale.US,"%02X",b[i]&255));}
            return s.toString();
        }
        private static String rootMessage(Throwable t) {
            while(t instanceof InvocationTargetException && ((InvocationTargetException)t).getCause()!=null) t=((InvocationTargetException)t).getCause();
            return t.getClass().getSimpleName()+": "+String.valueOf(t.getMessage());
        }
    }
}
