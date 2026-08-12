package com.hokkaidogolf.trip;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public class BetaSimActivity extends Activity {
    private final int DEEP = Color.rgb(8,79,52);
    private final int GREEN = Color.rgb(24,111,68);
    private final int BG = Color.rgb(249,250,240);
    private final int INK = Color.rgb(34,55,40);
    private final int SOFT = Color.rgb(238,246,226);

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setTitle("北海道 BETA SIM");
        setContentView(buildUi());
    }

    private View buildUi(){
        float d=getResources().getDisplayMetrics().density;
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(BG);
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding((int)(22*d),(int)(26*d),(int)(22*d),(int)(30*d));
        scroll.addView(root,new ScrollView.LayoutParams(ScrollView.LayoutParams.MATCH_PARENT,ScrollView.LayoutParams.WRAP_CONTENT));

        TextView over=label("OFFSITE FIELD REHEARSAL",12,Color.rgb(73,145,91),true);root.addView(over);
        TextView title=label("北海道 BETA SIM",31,DEEP,true);title.setPadding(0,(int)(4*d),0,(int)(4*d));root.addView(title);
        TextView sub=label("내일 현장 전 리허설 · 실제 홀 거리/공략 화면을 GPS GOOD 상태로 실행",15,INK,false);sub.setPadding(0,0,0,(int)(18*d));root.addView(sub);

        TextView note=label("※ SIM은 기능 검증용입니다. 오른쪽 GPS AXIS를 원하는 위치에 탭하면 YOU가 이동하고 잔여 m가 즉시 바뀝니다. 실제 GPS 모드에서는 TEE+GREEN 저장 후 자동 계산됩니다.",13,Color.DKGRAY,false);
        note.setPadding((int)(14*d),(int)(12*d),(int)(14*d),(int)(12*d));note.setBackground(round(SOFT,18*d));root.addView(note,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT));

        section(root,"HOKKAIDO · TRIP PACK",d);
        addCourse(root,"가미시호로 · CHAMPIONS",0,0,d);
        addCourse(root,"가미시호로 · MASTERS",0,1,d);
        addCourse(root,"후라노 · PALMER",1,0,d);
        addCourse(root,"후라노 · KING",1,1,d);
        addCourse(root,"사호로 · OUT / IN",2,0,d);

        section(root,"KOREA · CHECK",d);
        addCourse(root,"로얄링스 · QUEENS",4,0,d);
        addCourse(root,"로얄링스 · KINGS",4,1,d);

        TextView tip=label("추천 리허설: 사호로 H13에서 GPS AXIS 20% → 50% → 80% 탭 · 거리 감소 확인 → 스코어 입력/카드",13,Color.rgb(90,100,90),false);
        tip.setPadding(0,(int)(16*d),0,(int)(12*d));root.addView(tip);

        Button real=button("실제 GPS 앱 열기",DEEP,Color.WHITE,d);
        real.setOnClickListener(v->{Intent i=new Intent(this,FieldGpsV09Activity.class);startActivity(i);});
        root.addView(real,params(d,62));
        return scroll;
    }

    private void section(LinearLayout root,String s,float d){
        TextView t=label(s,12,GREEN,true);t.setPadding(0,(int)(22*d),0,(int)(8*d));root.addView(t);
    }

    private void addCourse(LinearLayout root,String name,int course,int variant,float d){
        Button b=button(name,Color.WHITE,INK,d);b.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);
        b.setPadding((int)(18*d),0,(int)(18*d),0);
        b.setOnClickListener(v->launch(course,variant));
        LinearLayout.LayoutParams lp=params(d,58);lp.setMargins(0,0,0,(int)(9*d));root.addView(b,lp);
    }

    private void launch(int course,int variant){
        Intent i=new Intent(this,FieldGpsV09Activity.class);
        i.putExtra("preview",true);
        i.putExtra("previewCourse",course);
        i.putExtra("previewVariant",variant);
        i.putExtra("previewHole",1);
        i.putExtra("previewScreen",1);
        startActivity(i);
    }

    private TextView label(String s,float size,int color,boolean bold){
        TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);t.setLineSpacing(0,1.12f);t.setTypeface(Typeface.create("sans-serif-rounded",bold?Typeface.BOLD:Typeface.NORMAL));return t;
    }
    private Button button(String s,int bg,int fg,float d){
        Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(16);b.setTextColor(fg);b.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));b.setBackground(round(bg,20*d));b.setStateListAnimator(null);return b;
    }
    private GradientDrawable round(int color,float radius){GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(radius);g.setStroke(1,Color.rgb(220,227,214));return g;}
    private LinearLayout.LayoutParams params(float d,int h){return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,(int)(h*d));}
}
