from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.12.4 · HOLE STEP' not in s:
    raise SystemExit('v1.13.0 requires v1.12.4 hole-step build')
s=s.replace('V1.12.4 · HOLE STEP','V1.13.0 · CONCEPT ART SKIN',1)

# -----------------------------------------------------------------------------
# 1) Bundle the same rounded display language used by the approved concept art.
# Jua = Korean/UI, M PLUS Rounded = Japanese course/title strings.
# -----------------------------------------------------------------------------
field='''        private final Bitmap v12Home,v12Course,v12Score;'''
if field not in s:
    raise SystemExit('v1.13.0 bitmap field anchor missing')
s=s.replace(field,field+'\n        private Typeface conceptKoV1130,conceptJpV1130;',1)

ctor='''            v12Score=BitmapFactory.decodeResource(getResources(),R.drawable.v12_score_ui);'''
if ctor not in s:
    raise SystemExit('v1.13.0 constructor asset anchor missing')
s=s.replace(ctor,ctor+'''\n            try{conceptKoV1130=Typeface.createFromAsset(c.getAssets(),"fonts/Jua-Regular.ttf");}catch(Exception e){conceptKoV1130=Typeface.create("sans-serif-rounded",Typeface.BOLD);}\n            try{conceptJpV1130=Typeface.createFromAsset(c.getAssets(),"fonts/MPLUSRounded1c-ExtraBold.ttf");}catch(Exception e){conceptJpV1130=Typeface.create("sans-serif-rounded",Typeface.BOLD);}''',1)

helper_anchor='''        private void text(Canvas c,String s,float x,float y,float z,int col,boolean bold){'''
idx=s.find(helper_anchor)
if idx<0:
    raise SystemExit('v1.13.0 text helper anchor missing')
helper=r'''        private Typeface conceptTypefaceV1130(String s,boolean bold){
            boolean jp=false,hangul=false;
            if(s!=null){
                for(int i=0;i<s.length();i++){
                    char ch=s.charAt(i);
                    if(ch>=0xAC00&&ch<=0xD7AF)hangul=true;
                    if((ch>=0x3040&&ch<=0x30FF)||(ch>=0x31F0&&ch<=0x31FF))jp=true;
                }
            }
            Typeface base=(jp&&!hangul)?conceptJpV1130:conceptKoV1130;
            if(base==null)base=Typeface.create("sans-serif-rounded",bold?Typeface.BOLD:Typeface.NORMAL);
            return Typeface.create(base,bold?Typeface.BOLD:Typeface.NORMAL);
        }

'''
s=s[:idx]+helper+s[idx:]

old='''        private void text(Canvas c,String s,float x,float y,float z,int col,boolean bold,Paint.Align a){p.setShader(null);p.setStyle(Paint.Style.FILL);p.setColor(col);p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);p.setTypeface(Typeface.create("sans-serif-rounded",bold?Typeface.BOLD:Typeface.NORMAL));p.setTextAlign(a);c.drawText(s,x,y,p);}'''
new='''        private void text(Canvas c,String s,float x,float y,float z,int col,boolean bold,Paint.Align a){p.setShader(null);p.setStyle(Paint.Style.FILL);p.setColor(col);p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);p.setTypeface(conceptTypefaceV1130(s,bold));p.setTextAlign(a);c.drawText(s,x,y,p);}'''
if old not in s:
    raise SystemExit('v1.13.0 text renderer body anchor missing')
s=s.replace(old,new,1)

oldfit='''        private void textFit(Canvas c,String s,float x,float y,float right,float z,int col,boolean bold){p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);while(p.measureText(s)>right-x && z>6.5f){z-=.25f;p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);}text(c,s,x,y,z,col,bold);}'''
newfit='''        private void textFit(Canvas c,String s,float x,float y,float right,float z,int col,boolean bold){p.setTypeface(conceptTypefaceV1130(s,bold));p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);while(p.measureText(s)>right-x && z>5.4f){z-=.25f;p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);}text(c,s,x,y,z,col,bold);}'''
if oldfit not in s:
    raise SystemExit('v1.13.0 textFit anchor missing')
s=s.replace(oldfit,newfit,1)

# -----------------------------------------------------------------------------
# 2) Concept-art palette. Warm cream paper, lively green, sky blue and orange.
# -----------------------------------------------------------------------------
oldcol='''        private final int BG=Color.rgb(249,250,240),INK=Color.rgb(34,55,40),GREEN=Color.rgb(24,111,68),DEEP=Color.rgb(8,79,52),\n                SKY=Color.rgb(96,196,230),BLUE=Color.rgb(75,166,211),CORAL=Color.rgb(255,126,92),YELLOW=Color.rgb(255,208,64),\n                CARD=Color.WHITE,SOFT=Color.rgb(241,245,235),AMBER=Color.rgb(184,126,30);'''
newcol='''        private final int BG=Color.rgb(253,252,235),INK=Color.rgb(54,80,54),GREEN=Color.rgb(87,159,98),DEEP=Color.rgb(31,99,58),\n                SKY=Color.rgb(73,181,237),BLUE=Color.rgb(73,181,237),CORAL=Color.rgb(247,126,86),YELLOW=Color.rgb(252,203,62),\n                CARD=Color.rgb(255,254,243),SOFT=Color.rgb(240,242,227),AMBER=Color.rgb(196,136,53);'''
if oldcol not in s:
    raise SystemExit('v1.13.0 palette anchor missing')
s=s.replace(oldcol,newcol,1)

s=s.replace('''RectF range=new RectF(m,h*.073f,w-m,h*.126f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),18);sheen(c,range,18);''',
            '''RectF range=new RectF(m,h*.073f,w-m,h*.126f);gradient(c,range,Color.rgb(34,126,72),Color.rgb(87,159,98),18);sheen(c,range,18);''',1)
s=s.replace('''p.setColor(Color.rgb(229,240,221));c.drawRoundRect(stage,21,21,p);''',
            '''p.setColor(Color.rgb(242,248,223));c.drawRoundRect(stage,24,24,p);''',1)
# Sky header + green distance strip = same sky/grass hierarchy as the concept art.
s=s.replace('''RectF head=new RectF(0,0,w,h*.070f);gradient(c,head,DEEP,GREEN,0);''',
            '''RectF head=new RectF(0,0,w,h*.070f);gradient(c,head,Color.rgb(48,164,229),Color.rgb(91,190,228),0);''',1)

# Direct GPS point stays orange and pulsing, now matching the concept accent.
s=s.replace('''            int orange=Color.rgb(255,132,35);''','''            int orange=Color.rgb(247,126,52);''',1)
s=s.replace('''            p.setColor(Color.argb((int)(32+42*pulse),255,132,35));''','''            p.setColor(Color.argb((int)(36+54*pulse),247,126,52));''',1)

# -----------------------------------------------------------------------------
# 3) HOME: use the approved illustrated hero literally, then continue the same
# visual world with five wooden signboards. This preserves the current 5-course
# field-test data without reverting to the old flat list UI.
# -----------------------------------------------------------------------------
hs=s.find('        private void home(Canvas c){')
he=s.find('        private void drawKoreaFlag(Canvas c,RectF r){',hs)
if hs<0 or he<0:
    raise SystemExit('v1.13.0 final home block boundary missing')
home=r'''        private void home(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.052f;
            c.drawColor(BG);

            // The top of v12Home is the approved concept-art hero at full phone
            // resolution. Clip it instead of approximating the mascot/art in code.
            RectF hero=new RectF(0,0,w,h*.236f);
            c.save();c.clipRect(hero);c.drawBitmap(v12Home,null,new RectF(0,0,w,h),p);c.restore();
            p.setColor(Color.argb(26,40,91,40));c.drawRect(0,hero.bottom-3,w,hero.bottom+5,p);

            text(c,"오늘 어디서 칠까요?",m,h*.272f,16.5f,DEEP,true);
            pill(c,new RectF(w*.68f,h*.250f,w*.94f,h*.279f),Color.rgb(232,246,213),"ALL DISTANCE · m",GREEN,6.3f);

            float top=h*.292f,ch=h*.061f,gap=h*.010f;
            int[] dots={Color.rgb(87,172,86),Color.rgb(164,103,204),Color.rgb(55,151,103),CORAL,SKY};
            String[] region={"JP 01","JP 02","JP 03","KR TEST","KR OFFICIAL"};
            for(int i=0;i<5;i++){
                float y=top+i*(ch+gap);cards[i].set(m,y,w-m,y+ch);
                drawWoodCardV1130(c,cards[i],selected==i,dots[i]);
                p.setColor(dots[i]);c.drawCircle(cards[i].left+25,cards[i].centerY(),9,p);
                text(c,region[i],cards[i].left+43,y+ch*.29f,6.6f,selected==i?Color.rgb(114,67,24):Color.rgb(126,83,42),true);
                textFit(c,ko[i],cards[i].left+43,y+ch*.62f,cards[i].right-w*.30f,13.8f,Color.rgb(62,45,29),true);
                String vv=variants[i][0]+((i==0||i==1||i==4)?" / "+variants[i][1]:"");
                textFit(c,vv,cards[i].left+43,y+ch*.82f,cards[i].right-14,6.5f,Color.rgb(102,79,51),true);
                if(location!=null){
                    int dm=(int)Math.round(distanceToCourse(location,i));
                    String ds=dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km";
                    pill(c,new RectF(cards[i].right-112,y+11,cards[i].right-12,y+38),Color.argb(224,255,250,225),ds,selected==i?DEEP:Color.rgb(120,102,77),6.0f);
                }
            }

            float vy=h*.658f;
            text(c,"코스 선택",m,vy-9,8.0f,DEEP,true);
            varA.set(m,vy,w*.485f,vy+h*.042f);varB.set(w*.515f,vy,w-m,vy+h*.042f);
            if(selected>=0){
                goldButton(c,varA,variant==0?DEEP:Color.rgb(250,244,215),variants[selected][0],variant==0?Color.WHITE:Color.rgb(75,54,34),13.5f);
                goldButton(c,varB,variant==1?DEEP:Color.rgb(250,244,215),variants[selected][1],variant==1?Color.WHITE:Color.rgb(75,54,34),13.5f);
            }else{
                goldButton(c,varA,Color.rgb(244,240,221),"A COURSE",Color.GRAY,12f);
                goldButton(c,varB,Color.rgb(244,240,221),"B COURSE",Color.GRAY,12f);
            }

            start.set(m,h*.730f,w-m,h*.795f);
            gradient(c,start,selected>=0?Color.rgb(243,145,46):Color.rgb(215,213,199),selected>=0?Color.rgb(255,176,62):Color.rgb(194,192,181),30);sheen(c,start,30);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(selected>=0?Color.rgb(168,93,25):Color.rgb(165,163,153));c.drawRoundRect(start,30,30,p);p.setStyle(Paint.Style.FILL);
            goldText(c,selected>=0?"라운드 시작  >":"골프장을 먼저 선택",start.centerX(),start.centerY(),18.0f,selected>=0?Color.WHITE:Color.DKGRAY);

            pill(c,new RectF(m,h*.822f,w*.43f,h*.858f),Color.rgb(230,246,211),"COURSES OFFLINE",DEEP,7.0f);
            pill(c,new RectF(w*.57f,h*.822f,w-m,h*.858f),Color.rgb(230,246,211),location==null?"GPS WAIT":"GPS READY",location==null?CORAL:DEEP,7.0f);
            text(c,"24~26 AUG · HOKKAIDO TRIP",w/2,h*.902f,9.2f,DEEP,true,Paint.Align.CENTER);
            text(c,"GPS + 코스맵 + 스코어 · 오프라인 라운드",w/2,h*.932f,7.5f,Color.rgb(96,111,79),true,Paint.Align.CENTER);
        }

        private void drawWoodCardV1130(Canvas c,RectF r,boolean selected,int accent){
            RectF sh=new RectF(r.left,r.top+5,r.right,r.bottom+5);p.setColor(Color.argb(28,93,57,26));c.drawRoundRect(sh,24,24,p);
            gradient(c,r,selected?Color.rgb(255,225,168):Color.rgb(255,236,192),selected?Color.rgb(247,195,119):Color.rgb(249,215,157),24);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(selected?5f:3f);p.setColor(selected?Color.rgb(118,77,28):Color.rgb(155,105,49));c.drawRoundRect(r,24,24,p);
            RectF in=new RectF(r.left+7,r.top+7,r.right-7,r.bottom-7);p.setStrokeWidth(1.5f);p.setColor(Color.argb(130,188,126,55));c.drawRoundRect(in,18,18,p);p.setStyle(Paint.Style.FILL);
            if(selected){p.setColor(Color.argb(120,255,210,50));c.drawCircle(r.right-24,r.top+20,6,p);}
        }

'''
s=s[:hs]+home+s[he:]

p.write_text(s)

# Legacy activity is still compiled although V09 is the launcher.
legacy=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsActivity.java')
if legacy.exists():
    t=legacy.read_text()
    t=t.replace('c.drawOval(new RectF(x-r*.8f,y+r*.78f,x+r*.8f,y+r,p));','c.drawOval(new RectF(x-r*.8f,y+r*.78f,x+r*.8f,y+r),p);')
    t=t.replace('c.drawOval(new RectF(x-r*.8f,y+r*.78f,x+r*.8f,y+r));','c.drawOval(new RectF(x-r*.8f,y+r*.78f,x+r*.8f,y+r),p);')
    legacy.write_text(t)

print('applied v1.13.0 full concept-art skin: approved hero + wood course signs + rounded KR/JP typography')
