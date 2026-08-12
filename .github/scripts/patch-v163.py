from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.6.2 · PLAYER NAMES' not in s:
    raise SystemExit('v1.6.3 base version not found')
s=s.replace('V1.6.2 · PLAYER NAMES','V1.6.3 · PLAYER SETUP',1)

# Number selector for 1~4 players.
s=s.replace('import android.widget.LinearLayout;','import android.widget.LinearLayout;\nimport android.widget.NumberPicker;',1)

# Replace the V1.6.2 player helper/dialog block with count-aware setup.
start=s.find('        private String playerName(int i){')
end=s.find('        private void saveState(){',start)
if start<0 or end<0:
    raise SystemExit('v1.6.3 player helper block not found')
helpers=r'''        private int playerCount(){
            int n=statePrefs.getInt("player_count",previewMode?3:0);
            return Math.max(0,Math.min(4,n));
        }
        private String playerName(int i){
            String n=statePrefs.getString("player_name_"+i,"");
            if(n==null)n="";n=n.trim();
            return n.length()==2?n:("P"+(i+1));
        }
        private boolean playerNamesReady(){
            int n=playerCount();if(n<1||n>4)return false;
            for(int i=0;i<n;i++){String v=statePrefs.getString("player_name_"+i,"");if(v==null||v.trim().length()!=2)return false;}
            return statePrefs.getBoolean("player_names_set",false);
        }
        private void showPlayerNamesDialog(final boolean startAfter){
            final EditText[] fields=new EditText[4];
            final LinearLayout[] rows=new LinearLayout[4];
            LinearLayout root=new LinearLayout(ctx);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(46,14,46,8);

            TextView guide=new TextView(ctx);guide.setText("플레이어 수를 먼저 선택하면 그 수만큼 이름 슬롯이 생성됩니다. 이름은 두 글자로 입력하세요.");guide.setTextSize(15);guide.setTextColor(INK);guide.setPadding(0,0,0,12);guide.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL));root.addView(guide);

            LinearLayout countRow=new LinearLayout(ctx);countRow.setOrientation(LinearLayout.HORIZONTAL);countRow.setGravity(android.view.Gravity.CENTER_VERTICAL);countRow.setPadding(0,2,0,12);
            TextView countLab=new TextView(ctx);countLab.setText("플레이어 수");countLab.setTextSize(18);countLab.setTextColor(DEEP);countLab.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));countRow.addView(countLab,new LinearLayout.LayoutParams(0,76,1f));
            NumberPicker picker=new NumberPicker(ctx);picker.setMinValue(1);picker.setMaxValue(4);picker.setWrapSelectorWheel(false);int savedCount=playerCount();if(savedCount<1)savedCount=previewMode?3:4;picker.setValue(savedCount);countRow.addView(picker,new LinearLayout.LayoutParams(150,92));root.addView(countRow);

            TextView slotTitle=new TextView(ctx);slotTitle.setText("PLAYER SLOTS");slotTitle.setTextSize(13);slotTitle.setTextColor(GREEN);slotTitle.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));slotTitle.setPadding(0,0,0,5);root.addView(slotTitle);
            String[] demo={"가람","나래","다온","라온"};
            for(int i=0;i<4;i++){
                LinearLayout row=new LinearLayout(ctx);rows[i]=row;row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(android.view.Gravity.CENTER_VERTICAL);row.setPadding(0,6,0,6);
                TextView lab=new TextView(ctx);lab.setText("P"+(i+1));lab.setTextSize(18);lab.setTextColor(DEEP);lab.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));lab.setGravity(android.view.Gravity.CENTER_VERTICAL);row.addView(lab,new LinearLayout.LayoutParams(92,76));
                EditText ed=new EditText(ctx);fields[i]=ed;ed.setSingleLine(true);ed.setTextSize(21);ed.setTextColor(INK);ed.setHint("두 글자");ed.setSelectAllOnFocus(true);ed.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);ed.setFilters(new InputFilter[]{new InputFilter.LengthFilter(2)});ed.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));
                String saved=statePrefs.getString("player_name_"+i,"");if(saved!=null&&saved.trim().length()==2)ed.setText(saved.trim());else if(previewMode)ed.setText(demo[i]);
                row.addView(ed,new LinearLayout.LayoutParams(0,76,1f));root.addView(row);
            }
            Runnable sync=()->{int n=picker.getValue();for(int i=0;i<4;i++)rows[i].setVisibility(i<n?View.VISIBLE:View.GONE);};
            picker.setOnValueChangedListener((np,oldVal,newVal)->sync.run());sync.run();

            final AlertDialog dlg=new AlertDialog.Builder(ctx).setTitle("라운드 플레이어 설정").setView(root).setPositiveButton("저장",null).setNegativeButton("취소",null).create();
            dlg.setOnShowListener(x->dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
                int n=picker.getValue();String[] names=new String[4];
                for(int i=0;i<n;i++){names[i]=fields[i].getText().toString().trim();if(names[i].length()!=2){fields[i].setError("두 글자로 입력");fields[i].requestFocus();return;}}
                SharedPreferences.Editor ed=statePrefs.edit().putInt("player_count",n).putBoolean("player_names_set",true);
                for(int i=0;i<4;i++){if(i<n)ed.putString("player_name_"+i,names[i]);else ed.remove("player_name_"+i);}ed.apply();
                if(player>=n)player=0;dlg.dismiss();showToast(n+"명 플레이어 설정 완료");if(startAfter){screen=1;saveState();}invalidate();
            }));
            dlg.show();
        }

'''
s=s[:start]+helpers+s[end:]

# Dynamic player tabs: only configured players create visible slots.
start=s.find('        private void drawPlayerTabs(Canvas c,float y){')
end=s.find('        private void metric(',start)
if start<0 or end<0:
    raise SystemExit('v1.6.3 player tabs block not found')
tabs=r'''        private void drawPlayerTabs(Canvas c,float y){
            float w=getWidth(),h=getHeight(),m=w*.055f,gap=w*.012f,avail=w-2*m,tabH=h*.034f;int[] dots={GREEN,SKY,CORAL,YELLOW};
            int n=Math.max(1,playerCount());if(player>=n)player=0;float ww=(avail-gap*(n-1))/n;
            for(int i=0;i<4;i++)playerTabs[i].setEmpty();
            for(int i=0;i<n;i++){
                float l=m+i*(ww+gap);playerTabs[i].set(l,y,l+ww,y+tabH);
                int bg=player==i?GREEN:CARD,fg=player==i?Color.WHITE:INK;
                softShadow(c,playerTabs[i],tabH*.382f);box(c,playerTabs[i],bg,tabH*.382f);
                p.setColor(dots[i]);c.drawCircle(l+ww*.15f,y+tabH*.50f,Math.max(5f,tabH*.065f),p);
                goldText(c,playerName(i),l+ww*.56f,y+tabH*.50f,20.0f,fg);
            }
        }

'''
s=s[:start]+tabs+s[end:]

# Dynamic score-input cards: 1~4 cards centered vertically.
start=s.find('        private void scoreInput(Canvas c){')
end=s.find('        private void summary(Canvas c){',start)
if start<0 or end<0:
    raise SystemExit('v1.6.3 score input block not found')
score_input=r'''        private void scoreInput(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;int par=currentPar();int n=Math.max(1,playerCount());if(player>=n)player=0;
            c.drawBitmap(v12Course,null,new RectF(0,0,w,h),p);
            RectF cover=new RectF(0,h*.105f,w,h*.915f);box(c,cover,BG,0);
            RectF head=new RectF(0,h*.035f,w,h*.145f);gradient(c,head,DEEP,GREEN,0);
            text(c,"스코어 입력",m,h*.078f,29,Color.WHITE,true);
            text(c,ko[selected]+" / H"+hole+" / PAR "+par,m,h*.112f,14,Color.rgb(218,242,222),true);
            playerNamesBtn.set(w*.70f,h*.065f,w*.945f,h*.118f);goldButton(c,playerNamesBtn,Color.argb(50,255,255,255),"플레이어 설정",Color.WHITE,14.5f);
            drawHolePager(c,h*.150f);

            float rowH=h*.157f,gap=h*.018f,areaTop=h*.195f,areaH=h*.680f;
            float used=n*rowH+(n-1)*gap;if(used>areaH){rowH=(areaH-gap*(n-1))/n;used=n*rowH+(n-1)*gap;}
            float top=areaTop+(areaH-used)/2f;int[] dots={GREEN,SKY,CORAL,YELLOW};
            for(int i=0;i<4;i++){inputStrokeMinus[i].setEmpty();inputStrokePlus[i].setEmpty();inputPuttMinus[i].setEmpty();inputPuttPlus[i].setEmpty();}
            for(int pl=0;pl<n;pl++){
                float y=top+pl*(rowH+gap);RectF card=new RectF(m,y,w-m,y+rowH);
                softShadow(c,card,28);box(c,card,CARD,28);
                RectF tag=new RectF(card.left+14,card.top+14,card.left+126,card.top+56);box(c,tag,dots[pl],18);
                goldText(c,playerName(pl),tag.centerX(),tag.centerY(),18f,Color.WHITE);
                int st=getStroke(pl,hole,par),pu=getPutt(pl,hole),delta=st-par;
                String rel=delta==0?"E":(delta>0?"+"+delta:""+delta);
                goldText(c,rel,card.left+164,card.top+35,16.5f,delta>0?CORAL:(delta<0?GREEN:INK));
                text(c,"타수",card.left+115,card.top+78,13,Color.GRAY,true);
                goldText(c,""+st,card.left+226,card.top+92,34f,INK);
                text(c,"퍼트",card.left+420,card.top+78,13,Color.GRAY,true);
                goldText(c,""+pu,card.left+535,card.top+92,34f,INK);
                inputStrokeMinus[pl].set(card.left+96,card.bottom-58,card.left+164,card.bottom-10);
                inputStrokePlus[pl].set(card.left+282,card.bottom-58,card.left+350,card.bottom-10);
                inputPuttMinus[pl].set(card.left+408,card.bottom-58,card.left+476,card.bottom-10);
                inputPuttPlus[pl].set(card.right-92,card.bottom-58,card.right-24,card.bottom-10);
                goldButton(c,inputStrokeMinus[pl],SOFT,"−",INK,23f);goldButton(c,inputStrokePlus[pl],Color.rgb(229,244,218),"+",GREEN,23f);
                goldButton(c,inputPuttMinus[pl],SOFT,"−",INK,23f);goldButton(c,inputPuttPlus[pl],Color.rgb(226,245,250),"+",BLUE,23f);
            }
            setFourNav(w,h);drawGoldenNav(c);
        }

'''
s=s[:start]+score_input+s[end:]

# Rebuild scorecard as a count-aware table. Only configured names are drawn.
start=s.find('        private void score(Canvas c){')
end=s.find('        private void saveRef(',start)
if start<0 or end<0:
    raise SystemExit('v1.6.3 scorecard block not found')
score=r'''        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;int n=Math.max(1,playerCount());
            c.drawBitmap(v12Score,null,new RectF(0,0,w,h),p);
            RectF header=new RectF(0,h*.035f,w,h*.128f);gradient(c,header,DEEP,GREEN,0);
            text(c,"스코어카드",m,h*.082f,29,Color.WHITE,true);
            text(c,ko[selected]+" / "+variants[selected][variant]+" · "+n+"명",m,h*.112f,14,Color.rgb(218,242,222),true);
            RectF clean=new RectF(w*.025f,h*.128f,w*.975f,h*.905f);box(c,clean,Color.rgb(249,250,240),34);

            float leftL=w*.045f,leftR=w*.495f,rightL=w*.505f,rightR=w*.955f;
            float top=h*.145f,bottom=h*.690f;
            RectF outCard=new RectF(leftL,top,leftR,bottom),inCard=new RectF(rightL,top,rightR,bottom);
            softShadow(c,outCard,30);box(c,outCard,CARD,30);softShadow(c,inCard,30);box(c,inCard,CARD,30);
            RectF outHead=new RectF(leftL+8,top+8,leftR-8,top+h*.052f),inHead=new RectF(rightL+8,top+8,rightR-8,top+h*.052f);
            box(c,outHead,DEEP,22);box(c,inHead,GREEN,22);goldText(c,"OUT · 1–9",outHead.centerX(),outHead.centerY(),18.5f,Color.WHITE);goldText(c,"IN · 10–18",inHead.centerX(),inHead.centerY(),18.5f,Color.WHITE);
            float headerY=top+h*.078f;drawScoreHeader(c,leftL,leftR,headerY,n);drawScoreHeader(c,rightL,rightR,headerY,n);

            int[] totals={0,0,0,0},puts={0,0,0,0};int parTotal=0;float firstY=top+h*.118f,rowStep=h*.0492f;
            for(int i=1;i<=18;i++){
                int pa=parForHole(i);parTotal+=pa;int row=(i-1)%9;float l=i<=9?leftL:rightL,r=i<=9?leftR:rightR,y=firstY+row*rowStep;
                if(row%2==1){RectF stripe=new RectF(l+10,y-h*.020f,r-10,y+h*.026f);box(c,stripe,Color.rgb(247,249,242),14);}
                float[] xs=scoreColumns(l,r,n);goldText(c,""+i,xs[0],y,16.8f,INK);goldText(c,""+pa,xs[1],y,16.8f,Color.GRAY);
                for(int pl=0;pl<n;pl++){int sv=getStroke(pl,i,pa);totals[pl]+=sv;puts[pl]+=getPutt(pl,i);int col=sv>pa?CORAL:(sv<pa?GREEN:INK);goldText(c,""+sv,xs[2+pl],y,18.4f,col);}
                if(i==hole){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4);p.setColor(YELLOW);c.drawRoundRect(new RectF(l+8,y-h*.025f,r-8,y+h*.029f),18,18,p);p.setStyle(Paint.Style.FILL);}
            }

            RectF summary=new RectF(w*.045f,h*.715f,w*.955f,h*.895f);gradient(c,summary,DEEP,GREEN,34);sheen(c,summary,34);
            goldText(c,"ROUND SUMMARY",summary.centerX(),h*.744f,17.5f,Color.rgb(218,242,222));
            float innerGap=w*.012f,innerPad=w*.025f,cardW=(summary.width()-innerPad*2-innerGap*(n-1))/n;
            for(int pl=0;pl<n;pl++){
                float l=summary.left+innerPad+pl*(cardW+innerGap);RectF pc=new RectF(l,h*.765f,l+cardW,h*.875f);box(c,pc,Color.argb(42,255,255,255),22);
                goldText(c,playerName(pl),pc.centerX(),h*.790f,Math.min(17.5f,n==4?15.5f:17.5f),Color.rgb(218,242,222));int delta=totals[pl]-parTotal;String rel=delta==0?"E":(delta>0?"+"+delta:""+delta);
                goldText(c,""+totals[pl],pc.centerX(),h*.830f,n==4?29f:32f,Color.WHITE);goldText(c,rel+" · 퍼트 "+puts[pl],pc.centerX(),h*.860f,n==4?12.5f:14.2f,Color.WHITE);
            }
            setFourNav(w,h);drawGoldenNav(c);
        }

        private float[] scoreColumns(float l,float r,int n){
            float ww=r-l;float[] xs=new float[2+n];xs[0]=l+ww*.075f;xs[1]=l+ww*.205f;float start=l+ww*.325f,end=r-ww*.055f,step=n==1?0:(end-start)/(n-1);for(int i=0;i<n;i++)xs[2+i]=n==1?(start+end)/2f:start+i*step;return xs;
        }
        private void drawScoreHeader(Canvas c,float l,float r,float y,int n){
            float[] xs=scoreColumns(l,r,n);goldText(c,"H",xs[0],y,15.5f,Color.GRAY);goldText(c,"PAR",xs[1],y,15.5f,Color.GRAY);for(int i=0;i<n;i++)goldText(c,playerName(i),xs[2+i],y,n==4?13.2f:15.0f,GREEN);
        }

'''
s=s[:start]+score+s[end:]

# Score-input touch loop follows configured player count.
s=s.replace('for(int pl=0;pl<4;pl++){\n                    if(inputStrokeMinus[pl].contains(x,y))','for(int pl=0;pl<Math.max(1,playerCount());pl++){\n                    if(inputStrokeMinus[pl].contains(x,y))',1)

# Name button wording becomes full player setup.
s=s.replace('"이름 수정"','"플레이어 설정"')

p.write_text(s)
print('applied v1.6.3 dynamic player count + generated name slots + linked score UI')
