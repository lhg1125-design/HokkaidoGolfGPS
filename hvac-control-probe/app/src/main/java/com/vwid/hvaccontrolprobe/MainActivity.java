package com.vwid.hvaccontrolprobe;

import android.app.Activity;
import android.graphics.Color;
import android.os.*;
import android.view.View;
import android.widget.*;
import java.lang.reflect.*;
import java.util.*;

public final class MainActivity extends Activity {
    private final Handler ui = new Handler(Looper.getMainLooper());
    private TextView stateText, logText;
    private Button connectButton, readButton;
    private CheckBox armBox;
    private final ArrayList<Button> controls = new ArrayList<>();
    private TwBridge bridge;
    private HvacState state = new HvacState();
    private long rxSeq = 0;
    private long pendingToken = 0;
    private String pendingLabel = null;
    private int pendingKind = 0; // 1 fan, 2 tempL-,3 tempL+,4 tempR-,5 tempR+,6 ac,7 query
    private int pendingValue = -1;
    private int pendingRawBefore = -1;

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
        title.setText("VWID HVAC CONTROL PROBE 0.1 · VW");
        title.setTextSize(21);
        title.setTextColor(Color.WHITE);
        root.addView(title);

        TextView note = new TextView(this);
        note.setText("정차 상태 시험용. 자동 제어 없음. UI는 RX 확인 전 절대 상태를 선반영하지 않습니다.\nREAD CURRENT는 순정 VW 공조 코드의 상태요청, 제어 버튼은 순정 VW 명령표만 사용합니다.");
        note.setTextSize(13);
        note.setTextColor(Color.rgb(205,205,205));
        note.setPadding(0,dp(5),0,dp(7));
        root.addView(note);

        LinearLayout top = row();
        connectButton = button(top,"1. CONNECT", v -> connect());
        readButton = button(top,"2. READ CURRENT", v -> requestCurrent());
        armBox = new CheckBox(this);
        armBox.setText("3. ARM CONTROL");
        armBox.setTextColor(Color.rgb(255,190,115));
        armBox.setTextSize(15);
        armBox.setOnCheckedChangeListener((b,checked)->refreshButtons());
        top.addView(armBox,new LinearLayout.LayoutParams(0,-2,1));
        root.addView(top);

        stateText = new TextView(this);
        stateText.setTextSize(18);
        stateText.setTextColor(Color.WHITE);
        stateText.setPadding(0,dp(5),0,dp(5));
        stateText.setText("STATE: no live HVAC data yet");
        root.addView(stateText);

        LinearLayout fan = row();
        addControl(fan,"FAN −", v -> fan(-1));
        addControl(fan,"FAN +", v -> fan(+1));
        addControl(fan,"A/C", v -> toggleAc());
        root.addView(fan);

        LinearLayout temp = row();
        addControl(temp,"TEMP L −", v -> temp(true,false));
        addControl(temp,"TEMP L +", v -> temp(true,true));
        addControl(temp,"TEMP R −", v -> temp(false,false));
        addControl(temp,"TEMP R +", v -> temp(false,true));
        root.addView(temp);

        ScrollView scroll = new ScrollView(this);
        logText = new TextView(this);
        logText.setTextSize(13);
        logText.setTextColor(Color.rgb(190,205,215));
        logText.setTextIsSelectable(true);
        scroll.addView(logText);
        root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        setContentView(root);
    }

    private LinearLayout row() {
        LinearLayout r = new LinearLayout(this);
        r.setOrientation(LinearLayout.HORIZONTAL);
        return r;
    }
    private Button button(LinearLayout parent,String text,View.OnClickListener l) {
        Button b = new Button(this);
        b.setText(text); b.setAllCaps(false); b.setOnClickListener(l);
        parent.addView(b,new LinearLayout.LayoutParams(0,-2,1));
        return b;
    }
    private void addControl(LinearLayout parent,String text,View.OnClickListener l) {
        Button b=button(parent,text,l); controls.add(b);
    }
    private int dp(int v){return (int)(v*getResources().getDisplayMetrics().density+0.5f);}

    private void refreshButtons() {
        boolean connected = bridge != null && bridge.isConnected();
        if(connectButton!=null) connectButton.setEnabled(!connected);
        if(readButton!=null) readButton.setEnabled(connected);
        boolean arm = connected && armBox!=null && armBox.isChecked() && state.valid;
        for(Button b:controls) b.setEnabled(arm);
    }

    private void connect() {
        append("CONNECT requested");
        connectButton.setEnabled(false);
        bridge.connect();
    }

    private void requestCurrent() {
        if(!bridge.isConnected()) return;
        long before=rxSeq;
        int rc=bridge.requestCurrent();
        String pred=legacyFrame(0x90,0x21,0x00);
        append("READ CURRENT TX · TWUtil write(0x0501,0x90,[21 00]) · rc="+rc+" · expected-wire="+pred);
        beginPending("READ CURRENT",7,-1,-1,before);
    }

    private void fan(int delta) {
        if(!canControl()) return;
        int target=Math.max(0,Math.min(7,state.fan+delta));
        if(target==state.fan){append("FAN already at limit "+target);return;}
        int rc=bridge.sendControl(0xB7,target);
        append("CONTROL TX FAN → "+target+" · cmd=B7 val="+hex2(target)+" · rc="+rc+" · expected-wire="+legacyFrame(0xC6,0xB7,target));
        beginPending("FAN → "+target,1,target,state.fan,rxSeq);
    }

    private void temp(boolean left,boolean up) {
        if(!canControl()) return;
        int cmd=left?0xB8:0xB9;
        int val=up?1:0;
        int rawBefore=left?state.tempRawL:state.tempRawR;
        String label=(left?"TEMP L ":"TEMP R ")+(up?"+":"−");
        int rc=bridge.sendControl(cmd,val);
        append("CONTROL TX "+label+" · cmd="+hex2(cmd)+" val="+hex2(val)+" · rc="+rc+" · expected-wire="+legacyFrame(0xC6,cmd,val));
        beginPending(label,left?(up?3:2):(up?5:4),val,rawBefore,rxSeq);
    }

    private void toggleAc() {
        if(!canControl()) return;
        int desired=state.ac?0:1;
        int rc=bridge.sendControl(0xBD,desired);
        append("CONTROL TX A/C → "+(desired==1?"ON":"OFF")+" · cmd=BD val="+hex2(desired)+" · rc="+rc+" · expected-wire="+legacyFrame(0xC6,0xBD,desired));
        beginPending("A/C → "+(desired==1?"ON":"OFF"),6,desired,state.ac?1:0,rxSeq);
    }

    private boolean canControl() {
        if(!bridge.isConnected() || !armBox.isChecked() || !state.valid) {
            append("BLOCKED: CONNECT + live state + ARM required");
            return false;
        }
        return true;
    }

    private void beginPending(String label,int kind,int value,int rawBefore,long beforeSeq) {
        pendingToken++;
        long token=pendingToken;
        pendingLabel=label; pendingKind=kind; pendingValue=value; pendingRawBefore=rawBefore;
        ui.postDelayed(() -> {
            if(token!=pendingToken || pendingLabel==null) return;
            append("NO CONFIRM within 1500 ms · "+pendingLabel+" · UI state NOT guessed");
            clearPending();
        },1500L);
    }

    private void clearPending() {
        pendingToken++;
        pendingLabel=null; pendingKind=0; pendingValue=-1; pendingRawBefore=-1;
    }

    private void onBridgeEvent(TwBridge.Event e) {
        runOnUiThread(() -> {
            if(e.kind==TwBridge.Event.CONNECTED) {
                append("CONNECTED · open rc="+e.rc+" · RX-debug rc="+e.extra);
                refreshButtons();
            } else if(e.kind==TwBridge.Event.ERROR) {
                append("ERROR · "+e.text);
                refreshButtons();
            } else if(e.kind==TwBridge.Event.TX_RAW) {
                append("MCUdebug TX · "+e.text);
            } else if(e.kind==TwBridge.Event.RX_STATE) {
                rxSeq++;
                HvacState parsed=HvacState.fromPayload(e.payload);
                if(parsed.valid) {
                    state=parsed;
                    stateText.setText(state.summary()+"\nRX: "+e.text);
                    append("LIVE RX · "+e.text);
                    verifyPending();
                    refreshButtons();
                } else append("RX state payload unsupported · "+e.text);
            } else if(e.kind==TwBridge.Event.INFO) {
                append(e.text);
            }
        });
    }

    private void verifyPending() {
        if(pendingLabel==null) return;
        boolean ok=false;
        switch(pendingKind) {
            case 1: ok=state.fan==pendingValue; break;
            case 2: ok=state.tempRawL<pendingRawBefore; break;
            case 3: ok=state.tempRawL>pendingRawBefore; break;
            case 4: ok=state.tempRawR<pendingRawBefore; break;
            case 5: ok=state.tempRawR>pendingRawBefore; break;
            case 6: ok=(state.ac?1:0)==pendingValue; break;
            case 7: ok=true; break;
        }
        if(ok) {
            append("CONFIRMED BY LIVE RX · "+pendingLabel);
            clearPending();
        }
    }

    private void append(String s) {
        String old=logText.getText().toString();
        String line=new java.text.SimpleDateFormat("HH:mm:ss.SSS",Locale.US).format(new Date())+"  "+s;
        if(old.length()>9000) old=old.substring(old.length()-7000);
        logText.setText(old.length()==0?line:old+"\n"+line);
    }

    @Override protected void onDestroy() {
        if(bridge!=null) bridge.close();
        super.onDestroy();
    }

    private static String legacyFrame(int what,int a,int b) {
        int[] x={0x2E,what&255,0x02,a&255,b&255,0};
        int sum=0; for(int i=0;i<5;i++)sum+=x[i];
        x[5]=(0x2D-(sum&255))&255;
        StringBuilder s=new StringBuilder();
        for(int i=0;i<x.length;i++){if(i>0)s.append(' ');s.append(hex2(x[i]));}
        return s.toString();
    }
    private static String hex2(int x){return String.format(Locale.US,"%02X",x&255);}

    static final class HvacState {
        boolean valid,power,ac,auto,dual;
        int fan,tempRawL,tempRawR,heatL,heatR;
        float tempL,tempR;
        static HvacState fromPayload(byte[] p) {
            HvacState s=new HvacState();
            if(p==null || p.length<5)return s;
            int d1=p[0]&255,d2=p[1]&255,d3=p[2]&255,d4=p[3]&255,d5=p[4]&255;
            s.valid=true; s.power=(d1&0x80)!=0; s.ac=(d1&0x40)!=0; s.auto=(d1&0x18)!=0; s.dual=(d1&0x04)!=0;
            s.fan=d2&15; s.tempRawL=d3; s.tempRawR=d4; s.tempL=(d3+35)/2f; s.tempR=(d4+35)/2f;
            s.heatL=(d5>>4)&15; s.heatR=d5&15;
            return s;
        }
        String summary(){return String.format(Locale.US,"STATE  FAN %d   TEMP L %.1f°   TEMP R %.1f°   A/C %s   AUTO %s   DUAL %s   HEAT %d/%d",fan,tempL,tempR,ac?"ON":"OFF",auto?"ON":"OFF",dual?"ON":"OFF",heatL,heatR);}
    }

    static final class TwBridge {
        interface Listener { void event(Event e); }
        static final class Event {
            static final int CONNECTED=1,ERROR=2,TX_RAW=3,RX_STATE=4,INFO=5;
            final int kind,rc,extra; final String text; final byte[] payload;
            Event(int k,String t,int r,int x,byte[] p){kind=k;text=t;rc=r;extra=x;payload=p;}
            static Event of(int k,String t){return new Event(k,t,0,0,null);}
        }
        private final Listener listener;
        private HandlerThread thread;
        private Handler handler;
        private Object tw; private Class<?> cls;
        private Method write3,write4,removeHandler,stop,close;
        private volatile boolean connected=false;
        private final byte[] stream=new byte[4096]; private int streamLen=0;
        TwBridge(Listener l){listener=l;}
        boolean isConnected(){return connected;}

        void connect() {
            if(thread!=null)return;
            thread=new HandlerThread("VWID-HVAC-PROBE",android.os.Process.THREAD_PRIORITY_DISPLAY); thread.start();
            handler=new Handler(thread.getLooper()){
                @Override public void handleMessage(Message msg){onMessage(msg);}
            };
            handler.post(this::doConnect);
        }

        private void doConnect() {
            try {
                cls=Class.forName("android.tw.john.TWUtil");
                try { Constructor<?> c=cls.getDeclaredConstructor(); c.setAccessible(true); tw=c.newInstance(); }
                catch(NoSuchMethodException e){ Constructor<?> c=cls.getDeclaredConstructor(int.class); c.setAccessible(true); tw=c.newInstance(0x11); }
                short[] events={(short)0x010A,(short)0x0501,(short)0x050D};
                Method open=cls.getMethod("open",short[].class);
                Object orc=open.invoke(tw,(Object)events);
                int openRc=orc instanceof Number?((Number)orc).intValue():0;
                if(openRc!=0)throw new IllegalStateException("TWUtil.open rc="+openRc);
                cls.getMethod("start").invoke(tw);
                cls.getMethod("addHandler",String.class,Handler.class).invoke(tw,"VWIDHVACPROBE",handler);
                write3=cls.getMethod("write",int.class,int.class,int.class);
                write4=cls.getMethod("write",int.class,int.class,int.class,Object.class);
                removeHandler=cls.getMethod("removeHandler",String.class);
                stop=cls.getMethod("stop"); close=cls.getMethod("close");
                Object r=write3.invoke(tw,0x050D,1,1);
                int debugRc=r instanceof Number?((Number)r).intValue():0;
                connected=true;
                listener.event(new Event(Event.CONNECTED,"connected",openRc,debugRc,null));
            } catch(Throwable e) {
                connected=false;
                listener.event(Event.of(Event.ERROR,e.getClass().getSimpleName()+": "+String.valueOf(rootMessage(e))));
            }
        }

        int requestCurrent(){return writeLegacy(0x90,0x21,0);}
        int sendControl(int cmd,int value){return writeLegacy(0xC6,cmd,value);}
        private int writeLegacy(int what,int a,int b) {
            if(!connected||tw==null||write4==null)return -999;
            try {
                Object r=write4.invoke(tw,0x0501,what,2,new byte[]{(byte)a,(byte)b});
                return r instanceof Number?((Number)r).intValue():0;
            } catch(Throwable e){listener.event(Event.of(Event.ERROR,"write failed: "+rootMessage(e)));return -998;}
        }

        private void onMessage(Message msg) {
            try {
                if(msg.what==0x0501 && msg.arg1==0x21 && msg.obj instanceof byte[]) {
                    byte[] p=(byte[])msg.obj;
                    listener.event(new Event(Event.RX_STATE,"0501/21 payload "+hex(p,0,p.length),0,0,Arrays.copyOf(p,p.length)));
                    return;
                }
                if(msg.what!=0x050D || !(msg.obj instanceof byte[]))return;
                byte[] raw=(byte[])msg.obj; if(raw.length<2)return;
                int kind=raw[0]&255;
                if(kind==2) listener.event(Event.of(Event.TX_RAW,hex(raw,1,raw.length-1)));
                else if(kind==1) feed(raw,1,raw.length-1);
            }catch(Throwable e){listener.event(Event.of(Event.ERROR,"handler: "+rootMessage(e)));}
        }

        private void feed(byte[] b,int off,int len) {
            if(len<=0)return;
            if(len>stream.length){off+=len-stream.length;len=stream.length;}
            if(streamLen+len>stream.length)streamLen=0;
            System.arraycopy(b,off,stream,streamLen,len);streamLen+=len;
            while(streamLen>=4){
                int st=0;while(st<streamLen&&(stream[st]&255)!=0x2E)st++;
                if(st>0)remove(st); if(streamLen<4)return;
                int dl=stream[2]&255,total=dl+4;
                if(dl>96||total<5){remove(1);continue;}
                if(streamLen<total)return;
                int sum=0;for(int i=0;i<total;i++)sum+=stream[i]&255;
                if((sum&255)!=0x2D){remove(1);continue;}
                int cmd=stream[1]&255;
                String frame=hex(stream,0,total);
                if(cmd==0x21 && dl>=5) {
                    byte[] p=Arrays.copyOfRange(stream,3,3+dl);
                    listener.event(new Event(Event.RX_STATE,frame,0,0,p));
                }
                remove(total);
            }
        }
        private void remove(int n){if(n>=streamLen){streamLen=0;return;}System.arraycopy(stream,n,stream,0,streamLen-n);streamLen-=n;}

        void close() {
            connected=false;
            try{if(tw!=null&&write3!=null)write3.invoke(tw,0x050D,1,0);}catch(Throwable ignored){}
            try{if(tw!=null&&removeHandler!=null)removeHandler.invoke(tw,"VWIDHVACPROBE");}catch(Throwable ignored){}
            try{if(tw!=null&&stop!=null)stop.invoke(tw);}catch(Throwable ignored){}
            try{if(tw!=null&&close!=null)close.invoke(tw);}catch(Throwable ignored){}
            if(thread!=null){thread.quitSafely();thread=null;}
        }
        private static String hex(byte[] b,int o,int l){StringBuilder s=new StringBuilder();int end=Math.min(b.length,o+l);for(int i=o;i<end;i++){if(s.length()>0)s.append(' ');s.append(String.format(Locale.US,"%02X",b[i]&255));}return s.toString();}
        private static String rootMessage(Throwable t){while(t instanceof InvocationTargetException&&((InvocationTargetException)t).getCause()!=null)t=((InvocationTargetException)t).getCause();return String.valueOf(t.getMessage());}
    }
}
