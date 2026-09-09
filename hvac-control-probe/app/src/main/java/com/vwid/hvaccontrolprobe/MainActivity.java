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
    private TextView mcuText, canboxText, configText, stateText, logText;
    private Button connectButton, queryButton;
    private TwBridge bridge;

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();
        bridge = new TwBridge(this::onBridgeEvent);
        refreshButtons();
    }

    private void buildUi() {
        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18),dp(10),dp(18),dp(10));
        root.setBackgroundColor(Color.rgb(15,16,18));

        TextView title=new TextView(this);
        title.setText("VWID HVAC CANBOX TRACE 0.4");
        title.setTextSize(21); title.setTextColor(Color.WHITE);
        root.addView(title);

        TextView note=new TextView(this);
        note.setText("차량 제어 명령 없음. 순정 CarChoose의 읽기 요청만 사용합니다.\nCanBox VERSION은 BNR/RZC/XP/BXF/JFT 업데이트 화면이 시작될 때 실제 사용하는 0x010A,0x00FF,1 요청입니다.");
        note.setTextSize(13); note.setTextColor(Color.rgb(205,205,205));
        note.setPadding(0,dp(4),0,dp(6)); root.addView(note);

        LinearLayout row=new LinearLayout(this); row.setOrientation(LinearLayout.HORIZONTAL);
        connectButton=button(row,"1. CONNECT + READ ALL",v->connect());
        queryButton=button(row,"2. QUERY AGAIN",v->queryAll());
        root.addView(row);

        mcuText=label(root,"MCU: waiting",17,Color.rgb(255,190,115));
        canboxText=label(root,"CANBOX VERSION: waiting for 0x010A arg1=1",20,Color.rgb(255,220,150));
        configText=label(root,"FEATURE CONFIG: waiting for 0x0112",17,Color.rgb(220,220,220));
        stateText=label(root,"HVAC STATE: waiting live RX",17,Color.WHITE);

        ScrollView scroll=new ScrollView(this);
        logText=new TextView(this); logText.setTextSize(13); logText.setTextColor(Color.rgb(190,205,215));
        logText.setTextIsSelectable(true); scroll.addView(logText);
        root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        setContentView(root);
    }

    private TextView label(LinearLayout root,String text,int size,int color){
        TextView t=new TextView(this); t.setText(text); t.setTextSize(size); t.setTextColor(color);
        t.setPadding(0,dp(3),0,dp(2)); root.addView(t); return t;
    }
    private Button button(LinearLayout parent,String text,View.OnClickListener l){
        Button b=new Button(this); b.setText(text); b.setAllCaps(false); b.setOnClickListener(l);
        parent.addView(b,new LinearLayout.LayoutParams(0,-2,1)); return b;
    }
    private int dp(int v){return (int)(v*getResources().getDisplayMetrics().density+0.5f);}

    private void refreshButtons(){
        boolean c=bridge!=null&&bridge.isConnected();
        if(connectButton!=null)connectButton.setEnabled(!c);
        if(queryButton!=null)queryButton.setEnabled(c);
    }
    private void connect(){append("CONNECT requested");connectButton.setEnabled(false);bridge.connect();}
    private void queryAll(){
        if(bridge==null||!bridge.isConnected())return;
        int a=bridge.queryMcu();
        int b=bridge.queryCanboxVersion();
        int c=bridge.queryConfig();
        append("READ MCU · write(0x010A,0x00FF) · rc="+a);
        append("READ CANBOX VERSION · factory write(0x010A,0x00FF,1) · rc="+b);
        append("READ FEATURE CONFIG · write(0x0112,0x00FF) · rc="+c);
    }

    private void onBridgeEvent(TwBridge.Event e){
        runOnUiThread(()->{
            switch(e.kind){
                case TwBridge.Event.CONNECTED:
                    append("CONNECTED · open rc="+e.rc+" · RX-debug rc="+e.extra); refreshButtons(); queryAll(); break;
                case TwBridge.Event.MCU:
                    mcuText.setText("MCU: "+e.text); append("MCU RESPONSE · "+e.text); break;
                case TwBridge.Event.CANBOX:
                    canboxText.setText("CANBOX VERSION: "+e.text); append("CANBOX RESPONSE · "+e.text); break;
                case TwBridge.Event.CONFIG:
                    configText.setText("FEATURE CONFIG: "+e.text); append("CONFIG RESPONSE · "+e.text); break;
                case TwBridge.Event.RX_STATE:
                    HvacState s=HvacState.fromPayload(e.payload);
                    if(s.valid){stateText.setText(s.summary()+"\nRX: "+e.text);append("LIVE HVAC RX · "+e.text);} break;
                case TwBridge.Event.RAW:
                    append(e.text); break;
                case TwBridge.Event.ERROR:
                    append("ERROR · "+e.text); refreshButtons(); break;
            }
        });
    }

    private void append(String s){
        String old=logText.getText().toString();
        String line=new SimpleDateFormat("HH:mm:ss.SSS",Locale.US).format(new Date())+"  "+s;
        if(old.length()>14000)old=old.substring(old.length()-10000);
        logText.setText(old.length()==0?line:old+"\n"+line);
    }
    @Override protected void onDestroy(){if(bridge!=null)bridge.close();super.onDestroy();}

    static final class HvacState{
        boolean valid,ac,auto,dual; int fan,tl,tr,hl,hr; float left,right;
        static HvacState fromPayload(byte[] p){
            HvacState s=new HvacState(); if(p==null||p.length<5)return s;
            int d1=p[0]&255,d2=p[1]&255,d3=p[2]&255,d4=p[3]&255,d5=p[4]&255;
            s.valid=true;s.ac=(d1&0x40)!=0;s.auto=(d1&0x18)!=0;s.dual=(d1&0x04)!=0;s.fan=d2&15;
            s.tl=d3;s.tr=d4;s.left=(d3+35)/2f;s.right=(d4+35)/2f;s.hl=(d5>>4)&15;s.hr=d5&15;return s;
        }
        String summary(){return String.format(Locale.US,"HVAC  FAN %d  L %.1f°  R %.1f°  A/C %s  AUTO %s  DUAL %s  HEAT %d/%d",fan,left,right,ac?"ON":"OFF",auto?"ON":"OFF",dual?"ON":"OFF",hl,hr);}
    }

    static final class TwBridge{
        interface Listener{void event(Event e);}
        static final class Event{
            static final int CONNECTED=1,ERROR=2,MCU=3,CANBOX=4,CONFIG=5,RX_STATE=6,RAW=7;
            final int kind,rc,extra;final String text;final byte[] payload;
            Event(int k,String t,int r,int x,byte[] p){kind=k;text=t;rc=r;extra=x;payload=p;}
            static Event text(int k,String t){return new Event(k,t,0,0,null);}
        }
        private final Listener listener; private HandlerThread thread; private Handler handler;
        private Object tw; private Class<?> cls; private Method write2,write3,removeHandler,stop,close;
        private volatile boolean connected=false; private final byte[] stream=new byte[4096]; private int streamLen=0;
        TwBridge(Listener l){listener=l;} boolean isConnected(){return connected;}

        void connect(){
            if(thread!=null)return;
            thread=new HandlerThread("VWID-HVAC-CANBOX-TRACE",android.os.Process.THREAD_PRIORITY_DISPLAY);thread.start();
            handler=new Handler(thread.getLooper()){@Override public void handleMessage(Message msg){onMessage(msg);}};
            handler.post(this::doConnect);
        }
        private void doConnect(){
            try{
                cls=Class.forName("android.tw.john.TWUtil");
                try{Constructor<?> c=cls.getDeclaredConstructor();c.setAccessible(true);tw=c.newInstance();}
                catch(NoSuchMethodException e){Constructor<?> c=cls.getDeclaredConstructor(int.class);c.setAccessible(true);tw=c.newInstance(0x11);}
                short[] events={(short)0x010A,(short)0x0112,(short)0x0501,(short)0x050D};
                Object o=cls.getMethod("open",short[].class).invoke(tw,(Object)events);
                int openRc=o instanceof Number?((Number)o).intValue():0;if(openRc!=0)throw new IllegalStateException("TWUtil.open rc="+openRc);
                cls.getMethod("start").invoke(tw);
                cls.getMethod("addHandler",String.class,Handler.class).invoke(tw,"VWIDHVACCANBOXTRACE",handler);
                write2=cls.getMethod("write",int.class,int.class);
                write3=cls.getMethod("write",int.class,int.class,int.class);
                removeHandler=cls.getMethod("removeHandler",String.class);stop=cls.getMethod("stop");close=cls.getMethod("close");
                Object rr=write3.invoke(tw,0x050D,1,1);int debugRc=rr instanceof Number?((Number)rr).intValue():0;
                connected=true;listener.event(new Event(Event.CONNECTED,"connected",openRc,debugRc,null));
            }catch(Throwable e){connected=false;listener.event(Event.text(Event.ERROR,rootMessage(e)));}
        }
        int queryMcu(){return write2Read(0x010A);}
        int queryConfig(){return write2Read(0x0112);}
        int queryCanboxVersion(){
            if(!connected||tw==null||write3==null)return -999;
            try{Object r=write3.invoke(tw,0x010A,0x00FF,1);return r instanceof Number?((Number)r).intValue():0;}
            catch(Throwable e){listener.event(Event.text(Event.ERROR,"CanBox version query failed: "+rootMessage(e)));return -998;}
        }
        private int write2Read(int what){
            if(!connected||tw==null||write2==null)return -999;
            try{Object r=write2.invoke(tw,what,0x00FF);return r instanceof Number?((Number)r).intValue():0;}
            catch(Throwable e){listener.event(Event.text(Event.ERROR,String.format(Locale.US,"read 0x%04X failed: %s",what,rootMessage(e))));return -998;}
        }

        private void onMessage(Message msg){
            try{
                if(msg.what==0x010A){
                    String obj=describeObj(msg.obj);
                    String text=String.format(Locale.US,"arg1=%d(0x%X) arg2=%d(0x%X) obj=%s",msg.arg1,msg.arg1,msg.arg2,msg.arg2,obj);
                    listener.event(Event.text(msg.arg1==1?Event.CANBOX:Event.MCU,text));return;
                }
                if(msg.what==0x0112){listener.event(Event.text(Event.CONFIG,String.format(Locale.US,"mConfig=%d (0x%X) · arg2=%d · obj=%s",msg.arg1,msg.arg1,msg.arg2,describeObj(msg.obj))));return;}
                if(msg.what==0x0501){
                    listener.event(Event.text(Event.RAW,String.format(Locale.US,"EVENT 0501 arg1=%d(0x%X) arg2=%d obj=%s",msg.arg1,msg.arg1,msg.arg2,describeObj(msg.obj))));
                    if(msg.arg1==0x21&&msg.obj instanceof byte[]){byte[] p=(byte[])msg.obj;listener.event(new Event(Event.RX_STATE,"0501/21 "+hex(p,0,p.length),0,0,Arrays.copyOf(p,p.length)));}return;
                }
                if(msg.what!=0x050D){listener.event(Event.text(Event.RAW,String.format(Locale.US,"EVENT %04X arg1=%d arg2=%d obj=%s",msg.what,msg.arg1,msg.arg2,describeObj(msg.obj))));return;}
                if(!(msg.obj instanceof byte[])){listener.event(Event.text(Event.RAW,"MCUdebug non-byte "+describeObj(msg.obj)));return;}
                byte[] raw=(byte[])msg.obj;if(raw.length==0)return;int kind=raw[0]&255;
                String label=kind==1?"RX":kind==2?"TX":kind==3?"TEXT":"K"+kind;
                listener.event(Event.text(Event.RAW,"MCUdebug "+label+" · "+hex(raw,1,Math.max(0,raw.length-1))));
                if(kind==1&&raw.length>1)feed(raw,1,raw.length-1);
            }catch(Throwable e){listener.event(Event.text(Event.ERROR,"handler: "+rootMessage(e)));}
        }
        private void feed(byte[] b,int off,int len){
            if(len<=0)return;if(len>stream.length){off+=len-stream.length;len=stream.length;}if(streamLen+len>stream.length)streamLen=0;
            System.arraycopy(b,off,stream,streamLen,len);streamLen+=len;
            while(streamLen>=4){int st=0;while(st<streamLen&&(stream[st]&255)!=0x2E)st++;if(st>0)remove(st);if(streamLen<4)return;
                int dl=stream[2]&255,total=dl+4;if(dl>96||total<5){remove(1);continue;}if(streamLen<total)return;int sum=0;for(int i=0;i<total;i++)sum+=stream[i]&255;
                if((sum&255)!=0x2D){remove(1);continue;}if((stream[1]&255)==0x21&&dl>=5){byte[] p=Arrays.copyOfRange(stream,3,3+dl);listener.event(new Event(Event.RX_STATE,hex(stream,0,total),0,0,p));}remove(total);}
        }
        private void remove(int n){if(n>=streamLen){streamLen=0;return;}System.arraycopy(stream,n,stream,0,streamLen-n);streamLen-=n;}
        void close(){connected=false;try{if(tw!=null&&write3!=null)write3.invoke(tw,0x050D,1,0);}catch(Throwable ignored){}
            try{if(tw!=null&&removeHandler!=null)removeHandler.invoke(tw,"VWIDHVACCANBOXTRACE");}catch(Throwable ignored){}try{if(tw!=null&&stop!=null)stop.invoke(tw);}catch(Throwable ignored){}
            try{if(tw!=null&&close!=null)close.invoke(tw);}catch(Throwable ignored){}if(thread!=null){thread.quitSafely();thread=null;}}
        private static String describeObj(Object o){if(o==null)return "null";if(o instanceof byte[])return "byte["+((byte[])o).length+"] "+hex((byte[])o,0,((byte[])o).length);return o.getClass().getName()+" «"+String.valueOf(o)+"»";}
        private static String hex(byte[] b,int o,int l){StringBuilder s=new StringBuilder();int end=Math.min(b.length,o+l);for(int i=o;i<end;i++){if(s.length()>0)s.append(' ');s.append(String.format(Locale.US,"%02X",b[i]&255));}return s.toString();}
        private static String rootMessage(Throwable t){while(t instanceof InvocationTargetException&&((InvocationTargetException)t).getCause()!=null)t=((InvocationTargetException)t).getCause();return t.getClass().getSimpleName()+": "+String.valueOf(t.getMessage());}
    }
}
