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
# Keep the yardage screen hierarchy already approved in V1.12.4.
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

# Give the direct GPS position a more playful concept-art pulse while retaining
# the exact same geometry/progress calculation.
s=s.replace('''            int orange=Color.rgb(255,132,35);''','''            int orange=Color.rgb(247,126,52);''',1)
s=s.replace('''            p.setColor(Color.argb((int)(32+42*pulse),255,132,35));''','''            p.setColor(Color.argb((int)(36+54*pulse),247,126,52));''',1)

p.write_text(s)
print('applied v1.13.0 concept-art skin + bundled rounded KR/JP typography')
