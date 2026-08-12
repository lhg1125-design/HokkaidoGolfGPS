from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'private void roundJapanPremium(Canvas c)' not in s:
    raise SystemExit('v1.8.2 requires v1.8.1 renderer')

s=s.replace('V1.8.1 · PREMIUM COURSE ART','V1.8.2 · YARDAGE + UX')

# -----------------------------------------------------------------------------
# Home tab: make HOME available from every in-round screen without covering
# header content. The existing 4 navigation semantics are preserved and HOME is
# added as a fifth slot.
# -----------------------------------------------------------------------------
anchor='        private final RectF playerNamesBtn=new RectF();'
if anchor not in s:
    raise SystemExit('v1.8.2 playerNamesBtn anchor missing')
if 'private final RectF homeBtn=' not in s:
    s=s.replace(anchor,anchor+'\n        private final RectF homeBtn=new RectF();',1)

nav_start=s.find('        private void drawGoldenNav(Canvas c){')
nav_end=s.find('        private void drawHolePager(Canvas c,float cy){',nav_start)
if nav_start<0 or nav_end<0:
    raise SystemExit('v1.8.2 nav block missing')
nav=r'''        private void drawGoldenNav(Canvas c){
            float w=getWidth(),h=getHeight();RectF bar=new RectF(w*.035f,h*.918f,w*.965f,h*.985f);
            softShadow(c,bar,bar.height()*.36f);box(c,bar,CARD,bar.height()*.36f);
            goldText(c,"홈",homeBtn.centerX(),bar.centerY(),14.0f,INK);
            goldText(c,"코스",mapTab.centerX(),bar.centerY(),14.0f,screen==1?GREEN:INK);
            goldText(c,"입력",prev.centerX(),bar.centerY(),14.0f,screen==2?GREEN:INK);
            goldText(c,"카드",scoreTab.centerX(),bar.centerY(),14.0f,screen==3?GREEN:INK);
            goldText(c,"요약",next.centerX(),bar.centerY(),14.0f,screen==4?GREEN:INK);
        }
        private void setFourNav(float w,float h){
            float l=w*.045f,r=w*.955f,g=w*.008f,ww=(r-l-g*4)/5f;
            homeBtn.set(l,h*.925f,l+ww,h*.981f);
            mapTab.set(l+(ww+g),h*.925f,l+(ww+g)+ww,h*.981f);
            prev.set(l+2*(ww+g),h*.925f,l+2*(ww+g)+ww,h*.981f);
            scoreTab.set(l+3*(ww+g),h*.925f,l+3*(ww+g)+ww,h*.981f);
            next.set(l+4*(ww+g),h*.925f,r,h*.981f);
        }

'''
s=s[:nav_start]+nav+s[nav_end:]

# -----------------------------------------------------------------------------
# Player setup: the field use-case is 3 or 4 players. Replace the tiny
# NumberPicker with explicit 3/4 toggle buttons and put name fields in a
# ScrollView so the keyboard can never crop the active input field.
# -----------------------------------------------------------------------------
pl_start=s.find('        private int playerCount(){')
pl_end=s.find('        private void saveState(){',pl_start)
if pl_start<0 or pl_end<0:
    raise SystemExit('v1.8.2 player helper block missing')
players=r'''        private int playerCount(){
            int n=statePrefs.getInt("player_count",previewMode?3:3);
            return n==4?4:3;
        }
        private String playerName(int i){
            int cnt=playerCount();if(i>=cnt)return "";
            String n=statePrefs.getString("player_name_"+i,"");if(n==null)n="";n=n.trim();
            return n.length()==2?n:("P"+(i+1));
        }
        private boolean playerNamesReady(){
            int n=playerCount();
            for(int i=0;i<n;i++){String v=statePrefs.getString("player_name_"+i,"");if(v==null||v.trim().length()!=2)return false;}
            return statePrefs.getBoolean("player_names_set",false);
        }
        private void stylePlayerCountButton(android.widget.Button b,boolean on){
            android.graphics.drawable.GradientDrawable gd=new android.graphics.drawable.GradientDrawable();
            gd.setColor(on?GREEN:Color.rgb(241,245,235));gd.setCornerRadius(28*getResources().getDisplayMetrics().density);
            gd.setStroke((int)(1.2f*getResources().getDisplayMetrics().density),on?GREEN:Color.rgb(215,222,211));
            b.setBackground(gd);b.setTextColor(on?Color.WHITE:INK);b.setTextSize(18);b.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));
        }
        private void showPlayerNamesDialog(final boolean startAfter){
            final EditText[] fields=new EditText[4];final LinearLayout[] rows=new LinearLayout[4];
            final int[] count={playerCount()};float d=getResources().getDisplayMetrics().density;

            LinearLayout root=new LinearLayout(ctx);root.setOrientation(LinearLayout.VERTICAL);root.setPadding((int)(22*d),(int)(10*d),(int)(22*d),(int)(24*d));
            TextView guide=new TextView(ctx);guide.setText("인원 선택 후 이름을 입력하세요. 라운드 중에도 다시 수정할 수 있습니다.");guide.setTextSize(15);guide.setTextColor(INK);guide.setPadding(0,0,0,(int)(12*d));guide.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL));root.addView(guide);

            TextView countLab=new TextView(ctx);countLab.setText("플레이어 인원");countLab.setTextSize(15);countLab.setTextColor(DEEP);countLab.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));countLab.setPadding(0,0,0,(int)(8*d));root.addView(countLab);
            LinearLayout toggles=new LinearLayout(ctx);toggles.setOrientation(LinearLayout.HORIZONTAL);toggles.setPadding(0,0,0,(int)(14*d));
            android.widget.Button b3=new android.widget.Button(ctx);b3.setText("3명");b3.setAllCaps(false);
            android.widget.Button b4=new android.widget.Button(ctx);b4.setText("4명");b4.setAllCaps(false);
            LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(0,(int)(56*d),1f);tp.setMargins(0,0,(int)(6*d),0);toggles.addView(b3,tp);
            LinearLayout.LayoutParams tp2=new LinearLayout.LayoutParams(0,(int)(56*d),1f);tp2.setMargins((int)(6*d),0,0,0);toggles.addView(b4,tp2);root.addView(toggles);

            String[] demo={"가람","나래","다온","라온"};
            for(int i=0;i<4;i++){
                LinearLayout row=new LinearLayout(ctx);rows[i]=row;row.setOrientation(LinearLayout.VERTICAL);row.setPadding(0,(int)(6*d),0,(int)(8*d));
                TextView lab=new TextView(ctx);lab.setText("PLAYER "+(i+1));lab.setTextSize(13);lab.setTextColor(GREEN);lab.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));lab.setPadding((int)(2*d),0,0,(int)(4*d));row.addView(lab);
                EditText ed=new EditText(ctx);fields[i]=ed;ed.setSingleLine(true);ed.setTextSize(21);ed.setTextColor(INK);ed.setHint("이름 2글자");ed.setHintTextColor(Color.rgb(145,155,145));ed.setSelectAllOnFocus(true);ed.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);ed.setFilters(new InputFilter[]{new InputFilter.LengthFilter(2)});ed.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));ed.setPadding((int)(16*d),(int)(6*d),(int)(16*d),(int)(6*d));ed.setMinHeight((int)(58*d));
                android.graphics.drawable.GradientDrawable eg=new android.graphics.drawable.GradientDrawable();eg.setColor(Color.WHITE);eg.setCornerRadius(18*d);eg.setStroke((int)(1.2f*d),Color.rgb(215,224,211));ed.setBackground(eg);
                String saved=statePrefs.getString("player_name_"+i,"");if(saved!=null&&saved.trim().length()==2)ed.setText(saved.trim());else if(previewMode)ed.setText(demo[i]);
                row.addView(ed,new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,(int)(60*d)));root.addView(row);
            }
            final Runnable sync=()->{for(int i=0;i<4;i++)rows[i].setVisibility(i<count[0]?View.VISIBLE:View.GONE);stylePlayerCountButton(b3,count[0]==3);stylePlayerCountButton(b4,count[0]==4);};
            b3.setOnClickListener(v->{count[0]=3;sync.run();});b4.setOnClickListener(v->{count[0]=4;sync.run();});sync.run();

            android.widget.ScrollView scroll=new android.widget.ScrollView(ctx);scroll.setFillViewport(true);scroll.addView(root);
            final AlertDialog dlg=new AlertDialog.Builder(ctx).setTitle("라운드 플레이어 설정").setView(scroll).setPositiveButton("저장",null).setNegativeButton("취소",null).create();
            dlg.setOnShowListener(x->{
                if(dlg.getWindow()!=null){dlg.getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);dlg.getWindow().setLayout((int)(getResources().getDisplayMetrics().widthPixels*.94f),android.view.WindowManager.LayoutParams.WRAP_CONTENT);}
                dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
                    int n=count[0];String[] names=new String[4];
                    for(int i=0;i<n;i++){names[i]=fields[i].getText().toString().trim();if(names[i].length()!=2){fields[i].setError("두 글자로 입력");fields[i].requestFocus();return;}}
                    SharedPreferences.Editor ed=statePrefs.edit().putInt("player_count",n).putBoolean("player_names_set",true);
                    for(int i=0;i<4;i++){if(i<n)ed.putString("player_name_"+i,names[i]);else ed.remove("player_name_"+i);}ed.apply();
                    if(player>=n)player=0;dlg.dismiss();showToast(n+"명 플레이어 설정 완료");if(startAfter){screen=1;saveState();}invalidate();
                });
            });
            dlg.show();
        }

'''
s=s[:pl_start]+players+s[pl_end:]

# -----------------------------------------------------------------------------
# Yardage-first renderer. Scenic art remains as a premium reference strip, while
# the actual interaction surface is a hole-dependent 2D yardage guide. The 2D
# guide itself does NOT need GPS. GPS only supplies live distance/calibration.
# -----------------------------------------------------------------------------
marker='        private void roundJapanPremium(Canvas c){'
pos=s.find(marker)
if pos<0: raise SystemExit('v1.8.2 Japan method missing')
helpers=r'''        private void drawHazardBarV182(Canvas c,float y1,float y2){
            float w=getWidth(),m=w*.045f,g=w*.018f;float ww=(w-2*m-g)/2f;
            hazardBunkerBtn.set(m,y1,m+ww,y2);hazardWaterBtn.set(m+ww+g,y1,w-m,y2);
            boolean ready=previewMode || (location!=null && location.getAccuracy()<=12 && fixAgeSec()<=15);
            int bBg=ready?Color.rgb(252,236,185):Color.rgb(226,229,221),wBg=ready?Color.rgb(216,241,250):Color.rgb(226,229,221);
            goldButton(c,hazardBunkerBtn,bBg,"BUNKER GPS",DEEP,11.8f);goldButton(c,hazardWaterBtn,wBg,"WATER GPS",DEEP,11.8f);
        }
        private float holeCenterX(RectF r,float t,int seed){
            float a=(float)Math.sin(seed*.73+t*3.4)*r.width()*.105f;
            float b=(float)Math.sin(seed*.31+t*6.1)*r.width()*.045f;
            return r.centerX()+a+b;
        }
        private void drawHoleYardageV182(Canvas c,RectF r,int par,int officialM){
            int seed=selected*97+variant*41+hole*17;float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/420.0));
            gradient(c,r,Color.rgb(226,243,213),Color.rgb(192,228,183),28);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.5f);p.setColor(Color.argb(60,30,90,50));
            for(int d=100;d<=250;d+=50){if(officialM<=d)continue;float frac=1f-d/(float)Math.max(1,officialM);float yy=r.bottom-24-frac*(r.height()-66);c.drawLine(r.left+14,yy,r.right-14,yy,p);text(c,d+"m",r.left+18,yy-4,6.4f,Color.rgb(85,115,90),true);}
            p.setStyle(Paint.Style.FILL);
            int n=8;float[] lx=new float[n],rx=new float[n],yy=new float[n];
            for(int i=0;i<n;i++){float t=i/(float)(n-1);yy[i]=r.bottom-24-t*(r.height()-70);float cx=holeCenterX(r,t,seed);float wid=r.width()*(.105f+.030f*(float)Math.sin(seed*.19+t*2.7)+.025f*t);lx[i]=cx-wid;rx[i]=cx+wid;}
            Path fair=new Path();fair.moveTo(lx[0],yy[0]);for(int i=1;i<n;i++)fair.lineTo(lx[i],yy[i]);for(int i=n-1;i>=0;i--)fair.lineTo(rx[i],yy[i]);fair.close();
            p.setColor(Color.rgb(79,167,82));c.drawPath(fair,p);stripes(c,fair,r,(SystemClock.uptimeMillis()%2500)/2500f);
            float gx=holeCenterX(r,1f,seed),gy=r.top+30;p.setColor(Color.rgb(66,153,72));c.drawOval(new RectF(gx-34,gy-13,gx+38,gy+16),p);p.setColor(INK);p.setStrokeWidth(3);c.drawLine(gx+4,gy+4,gx+4,gy-25,p);Path fl=new Path();fl.moveTo(gx+4,gy-25);fl.lineTo(gx+28+5*pulse,gy-19);fl.lineTo(gx+4,gy-11);fl.close();p.setColor(CORAL);c.drawPath(fl,p);
            float tx=holeCenterX(r,0f,seed),ty=r.bottom-20;p.setColor(DEEP);c.drawCircle(tx,ty,7,p);text(c,"TEE",tx,ty+22,6.3f,DEEP,true,Paint.Align.CENTER);
            Hazard[] hz=hazardsForHole();
            for(int i=0;i<hz.length;i++){Hazard z=hz[i];float x=r.left+z.x*r.width(),y=r.bottom-z.y*r.height();int cc=z.type.equals("WATER")?BLUE:YELLOW;p.setColor(Color.argb(235,255,255,255));c.drawCircle(x,y,19,p);p.setColor(cc);c.drawCircle(x,y,13,p);goldText(c,z.type.equals("WATER")?"W":"B",x,y,8.2f,z.type.equals("WATER")?Color.WHITE:DEEP);}
            if(hasTarget){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(CORAL);c.drawCircle(targetX,targetY,12+4*pulse,p);p.setStyle(Paint.Style.FILL);p.setColor(CORAL);c.drawCircle(targetX,targetY,4,p);TargetInfo ti=targetInfo(r,officialM);String tl=ti.gps?("GPS "+ti.toTarget+"m"):("공략 약 "+ti.toTarget+"m");speech(c,Math.max(r.left+8,Math.min(targetX-80,r.right-158)),Math.max(r.top+8,targetY-48),tl,ti.gps?DEEP:CORAL);}
            text(c,"2D YARDAGE GUIDE · H"+hole,r.left+14,r.top+20,7.0f,DEEP,true);
            GeoRef gr=greenCenterRef(hole),tr=getRef("t",hole);String link=(gpsUsable()&&gr!=null)?"GPS DIST LINKED":"GPS는 거리값만 연동";pill(c,new RectF(r.right-155,r.top+9,r.right-10,r.top+37),Color.argb(225,255,255,255),link,(gpsUsable()&&gr!=null)?GREEN:Color.GRAY,6.0f);
        }

'''
s=s[:pos]+helpers+s[pos:]

jp_start=s.find('        private void roundJapanPremium(Canvas c){')
jp_end=s.find('        private void roundKorea(Canvas c){',jp_start)
if jp_start<0 or jp_end<0: raise SystemExit('v1.8.2 Japan block bounds missing')
japan=r'''        private void roundJapanPremium(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;int par=currentPar();int officialM=currentOfficialM();
            c.drawColor(BG);
            RectF head=new RectF(0,0,w,h*.128f);gradient(c,head,DEEP,GREEN,0);
            text(c,"LIVE COURSE · GPS 캐디",m,h*.040f,10.0f,Color.rgb(215,241,222),true);
            text(c,ko[selected],m,h*.079f,20.0f,Color.WHITE,true);
            text(c,variants[selected][variant]+" · H"+hole,m,h*.111f,10.5f,Color.rgb(218,242,222),true);
            pill(c,new RectF(w*.735f,h*.021f,w*.94f,h*.056f),Color.rgb(235,247,229),gpsStatusShort(),gpsColor(),6.9f);
            pill(c,new RectF(w*.735f,h*.072f,w*.94f,h*.111f),Color.argb(55,255,255,255),"PAR "+par,Color.WHITE,10.5f);

            GeoRef green=greenCenterRef(hole),gf=getRef("gf",hole),gb=getRef("gb",hole);Distances ds=distances3(gf,green,gb);
            RectF range=new RectF(m,h*.141f,w-m,h*.207f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),24);sheen(c,range,24);
            metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.154f);
            metric(c,ds.center>=0?"CENTER":"OFFICIAL",ds.center>=0?ds.center+"m":officialM+"m",w*.50f,h*.154f);
            metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.154f);
            pill(c,new RectF(m,h*.215f,w*.29f,h*.244f),gpsBg(),gpsStatusShort(),gpsColor(),6.5f);
            pill(c,new RectF(w*.31f,h*.215f,w*.70f,h*.244f),CARD,"2D MAP + PREMIUM SCENE",GREEN,5.9f);
            autoBtn.set(w*.72f,h*.215f,w-m,h*.244f);pill(c,autoBtn,autoHole?Color.rgb(229,244,218):CARD,autoHole?"AUTO ON":"AUTO OFF",autoHole?GREEN:Color.GRAY,6.2f);

            RectF scenic=new RectF(m,h*.254f,w-m,h*.330f);drawPremiumCourseArt(c,scenic);
            text(c,"SCENIC REFERENCE · 홀 형상은 아래 2D MAP",m,h*.344f,6.7f,Color.GRAY,true);
            drawHolePager(c,h*.362f);
            text(c,"H"+hole+" · PAR "+par+" · REG "+officialM+"m",w*.50f,h*.367f,8.0f,DEEP,true,Paint.Align.CENTER);
            courseRect.set(m,h*.382f,w-m,h*.590f);drawHoleYardageV182(c,courseRect,par,officialM);
            drawHazardBarV182(c,h*.599f,h*.634f);

            RectF strategy=new RectF(m,h*.646f,w-m,h*.696f);softShadow(c,strategy,18);box(c,strategy,CARD,18);
            text(c,"공략 포인트",m+14,h*.665f,8.2f,GREEN,true);textFit(c,strategyNote(),m+14,h*.688f,w*.70f,7.8f,INK,true);
            pill(c,new RectF(w*.72f,h*.655f,w-m-10,h*.684f),Color.rgb(236,246,228),hazardSourceLabel(),GREEN,5.6f);

            boolean capReady=previewMode || (location!=null && location.getAccuracy()<=12 && fixAgeSec()<=15);
            int gBg=capReady?(green==null?CORAL:DEEP):Color.rgb(150,160,150),tBg=capReady?(getRef("t",hole)==null?Color.rgb(53,139,94):DEEP):Color.rgb(150,160,150);
            greenSave.set(m,h*.708f,w*.38f,h*.755f);teeSave.set(w*.405f,h*.708f,w*.65f,h*.755f);mapLaunch.set(w*.675f,h*.708f,w-m,h*.755f);
            goldButton(c,greenSave,gBg,greenSaveLabel(),Color.WHITE,12.2f);goldButton(c,teeSave,tBg,getRef("t",hole)==null?"TEE 저장":"TEE OK",Color.WHITE,12.2f);goldButton(c,mapLaunch,CARD,"외부 지도",INK,12.2f);

            drawPlayerTabs(c,h*.772f);int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);
            RectF quick=new RectF(m,h*.816f,w-m,h*.900f);softShadow(c,quick,20);box(c,quick,CARD,20);
            text(c,"타수",m+16,h*.840f,8.2f,Color.GRAY,true);goldText(c,""+stroke,w*.28f,h*.861f,22f,INK);
            minus.set(m+70,h*.837f,m+128,h*.890f);plus.set(w*.355f,h*.837f,w*.435f,h*.890f);goldButton(c,minus,SOFT,"−",INK,17f);goldButton(c,plus,Color.rgb(229,244,218),"+",GREEN,17f);
            text(c,"퍼트",w*.52f,h*.840f,8.2f,Color.GRAY,true);goldText(c,""+putt,w*.69f,h*.861f,22f,INK);
            pm.set(w*.535f,h*.837f,w*.605f,h*.890f);pp.set(w*.82f,h*.837f,w*.90f,h*.890f);goldButton(c,pm,SOFT,"−",INK,17f);goldButton(c,pp,Color.rgb(226,245,250),"+",BLUE,17f);
            setFourNav(w,h);drawGoldenNav(c);
        }

'''
s=s[:jp_start]+japan+s[jp_end:]

# Korea: keep the premium image as a small scene strip, restore the crisp 2D
# yardage as the actual hole-changing map, and move capture buttons outside it.
old='''            courseRect.set(m,h*.278f,w-m,h*.600f);drawPremiumCourseArt(c,courseRect);drawKoreaArtOverlay(c,courseRect,par,officialM);\n            drawCapturedHazardSummary(c,courseRect);drawHazardCaptureButtons(c,courseRect);drawHolePager(c,h*.286f);'''
new='''            RectF scenic=new RectF(m,h*.278f,w-m,h*.350f);drawPremiumCourseArt(c,scenic);drawKoreaArtOverlay(c,scenic,par,officialM);\n            drawHolePager(c,h*.366f);\n            courseRect.set(m,h*.382f,w-m,h*.570f);drawKoreaYardage(c,courseRect,par,officialM);drawCapturedHazardSummary(c,courseRect);\n            drawHazardBarV182(c,h*.579f,h*.614f);'''
if old not in s:
    raise SystemExit('v1.8.2 Korea premium block anchor missing')
s=s.replace(old,new,1)
s=s.replace('RectF strategy=new RectF(m,h*.616f,w-m,h*.675f);','RectF strategy=new RectF(m,h*.625f,w-m,h*.681f);',1)
s=s.replace('text(c,"공략 / 테스트 포인트",m+14,h*.639f,8.8f,GREEN,true);','text(c,"공략 / 테스트 포인트",m+14,h*.646f,8.5f,GREEN,true);',1)
s=s.replace('textFit(c,koreaStrategyNote(),m+14,h*.662f,w-m-14,8.2f,INK,true);','textFit(c,koreaStrategyNote(),m+14,h*.671f,w-m-14,7.9f,INK,true);',1)

# HOME touch works from course/input/card/summary screens.
touch='            if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();'
if touch not in s: raise SystemExit('v1.8.2 touch anchor missing')
s=s.replace(touch,touch+'\n            if(screen!=0 && homeBtn.contains(x,y)){screen=0;hasTarget=false;saveState();invalidate();return true;}',1)

p.write_text(s)
print('applied v1.8.2 yardage-first UI + home nav + 3/4 player setup')
