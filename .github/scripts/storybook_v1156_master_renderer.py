from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.15.1 · REFERENCE POLISH' not in s:
    raise SystemExit('V1.15.6 master renderer requires V1.15.1 reference polish')

anchor='        private boolean furanoKing123V1152(){'
pos=s.find(anchor)
if pos<0:
    anchor='        private boolean coverHudV1138(){'
    pos=s.find(anchor)
if pos<0: raise SystemExit('V1.15.6 helper insertion anchor missing')

helpers=r'''        // V1.15.6 MASTER DESIGN RENDERER
        // One UI grammar + raw external yardage bitmap/data. No per-hole screen generation.
        // Any registered course index uses the same renderer automatically.
        private boolean masterRendererV1156(){return screen==1 && selected>=0 && hole>=1 && hole<=18;}
        private void masterTextV1156(Canvas c,String s,float x,float y,float z,int col,Paint.Align a,boolean stroke){
            p.setShader(null);p.clearShadowLayer();p.setAlpha(255);p.setTextAlign(a);p.setTextSize(z);p.setTypeface(conceptTypefaceV1130(s,true));
            if(stroke){p.setStyle(Paint.Style.STROKE);p.setStrokeJoin(Paint.Join.ROUND);p.setStrokeWidth(Math.max(2f,z*.095f));p.setColor(Color.rgb(15,18,12));c.drawText(s,x,y,p);}
            p.setStyle(Paint.Style.FILL);p.setColor(col);c.drawText(s,x,y,p);p.setStrokeJoin(Paint.Join.MITER);
        }
        private int masterCenterM1156(){
            int total=verifiedMetersV190();if(total<=0)total=(int)Math.round(currentYards()*.9144);
            GeoRef g=greenCenterRef(hole);if(!previewMode&&g!=null&&gpsUsable())return Math.max(0,Math.round(distance(location,g.lat,g.lon)));
            int r=navRemainV1110(total);return r>=0?r:total;
        }
        private void drawWoodMetricV1156(Canvas c,String label,int value,float cx,float y,int col){
            masterTextV1156(c,String.valueOf(value),cx-5,y,53,col,Paint.Align.CENTER,true);
            masterTextV1156(c,"m",cx+62,y,22,col,Paint.Align.CENTER,true);
            masterTextV1156(c,label,cx,y+48,20,Color.WHITE,Paint.Align.CENTER,true);
        }
        private void drawMasterRendererV1156(Canvas c){
            final float w=getWidth(),h=getHeight(),sx=w/941f,sy=h/1672f;
            c.drawColor(Color.rgb(242,229,194));
            c.save();c.scale(sx,sy);
            p.setStyle(Paint.Style.FILL);p.setShader(null);p.setColor(Color.rgb(15,70,176));c.drawRect(0,0,941,156,p);
            masterTextV1156(c,"‹",38,68,68,Color.WHITE,Paint.Align.CENTER,false);
            masterTextV1156(c,ko[selected],92,65,38,Color.WHITE,Paint.Align.LEFT,true);
            masterTextV1156(c,variants[selected][variant]+" · H"+hole+" · PAR "+currentPar(),92,125,27,Color.WHITE,Paint.Align.LEFT,true);
            masterTextV1156(c,"☀",768,61,40,Color.rgb(255,202,25),Paint.Align.CENTER,false);
            masterTextV1156(c,"22°C",820,66,28,Color.WHITE,Paint.Align.LEFT,true);
            RectF wood=new RectF(18,156,923,350);softShadow(c,wood,24);p.setColor(Color.rgb(103,57,24));c.drawRoundRect(wood,22,22,p);
            for(int yy=166;yy<336;yy+=11){p.setColor(Color.argb(55,244,195,121));p.setStrokeWidth(2);c.drawLine(27,yy,914,yy+(yy%3-1)*4,p);}
            p.setColor(Color.argb(130,30,16,8));p.setStrokeWidth(3);c.drawLine(319,167,319,337,p);c.drawLine(622,167,622,337,p);
            Distances ds=distances(greenCenterRef(hole));int fallback=masterCenterM1156();
            int center=ds.center>=0?ds.center:fallback;int front=ds.front>=0?ds.front:Math.max(0,center-12);int back=ds.back>=0?ds.back:center+12;
            drawWoodMetricV1156(c,"FRONT",front,166,246,Color.rgb(28,145,255));drawWoodMetricV1156(c,"CENTER",center,470,246,Color.WHITE);drawWoodMetricV1156(c,"BACK",back,775,246,Color.rgb(255,78,70));
            RectF panel=new RectF(18,477,238,1328);softShadow(c,panel,26);p.setColor(Color.rgb(12,91,18));c.drawRoundRect(panel,28,28,p);
            masterTextV1156(c,"PAR",89,553,31,Color.WHITE,Paint.Align.CENTER,true);masterTextV1156(c,String.valueOf(currentPar()),146,553,31,Color.rgb(255,190,35),Paint.Align.CENTER,true);
            masterTextV1156(c,"H"+hole,128,635,68,Color.WHITE,Paint.Align.CENTER,true);
            float[] py={790,940,1090,1240};int[] pc={Color.rgb(30,104,220),Color.rgb(31,137,72),Color.rgb(255,155,17),Color.rgb(133,47,204)};
            for(int pl=0;pl<4;pl++){String nm=playerName(pl);if(nm==null||nm.trim().isEmpty())nm="P"+(pl+1);int d=cumulativeDeltaV1152(pl);p.setColor(pc[pl]);c.drawCircle(70,py[pl],27,p);masterTextV1156(c,furanoInitialV1152(nm,pl),70,py[pl]+8,21,Color.WHITE,Paint.Align.CENTER,false);masterTextV1156(c,nm,110,py[pl]-5,27,Color.WHITE,Paint.Align.LEFT,true);int sc=d<0?Color.rgb(40,151,255):(d>0?Color.rgb(255,75,68):Color.WHITE);masterTextV1156(c,signedV1152(d),165,py[pl]+43,40,sc,Paint.Align.CENTER,true);}
            RectF bub=new RectF(714,397,918,575);softShadow(c,bub,26);p.setColor(Color.rgb(255,247,222));c.drawRoundRect(bub,28,28,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.rgb(39,35,26));c.drawRoundRect(bub,28,28,p);p.setStyle(Paint.Style.FILL);
            masterTextV1156(c,"남은 거리",816,440,23,Color.rgb(30,29,23),Paint.Align.CENTER,false);masterTextV1156(c,center+"m",816,505,48,Color.rgb(25,25,20),Paint.Align.CENTER,false);masterTextV1156(c,"핀까지",816,552,21,Color.rgb(30,29,23),Paint.Align.CENTER,false);
            c.restore();
            Bitmap bm=fullHoleBitmapV1102();RectF slot=new RectF(255*sx,365*sy,680*sx,1445*sy);courseRect.set(slot);
            if(bm!=null){RectF dst=fitCenterV1102(bm,slot);p.setAlpha(255);p.setStyle(Paint.Style.FILL);p.setFilterBitmap(true);c.drawBitmap(bm,null,dst,p);}
            c.save();c.scale(sx,sy);RectF tb=new RectF(638,1261,908,1388);mapLaunch.set(tb.left*sx,tb.top*sy,tb.right*sx,tb.bottom*sy);softShadow(c,tb,45);p.setColor(Color.rgb(242,202,139));c.drawRoundRect(tb,45,45,p);masterTextV1156(c,"◎  타겟",773,1338,32,Color.rgb(25,23,17),Paint.Align.CENTER,true);c.restore();
            drawCleanNavV1150(c);p.setAlpha(255);p.setStyle(Paint.Style.FILL);
        }
'''
s=s[:pos]+helpers+s[pos:]

round_sig='        private void round(Canvas c){'
if round_sig not in s: raise SystemExit('V1.15.6 round anchor missing')
if 'if(masterRendererV1156())' not in s:s=s.replace(round_sig,round_sig+'\n            if(masterRendererV1156()){drawMasterRendererV1156(c);return;}',1)

field='        private Typeface conceptKoV1130,conceptJpV1130;'
if 'private String furanoInitialV1152' not in s:
    hp=r'''        private String furanoInitialV1152(String n,int pl){if(n==null)n="";String t=n.trim();if(t.contains("희권"))return "HK";if(t.contains("경집"))return "KJ";if(t.contains("시형"))return "SY";if(t.contains("중수"))return "JS";if(t.length()>=2&&t.charAt(0)<128&&t.charAt(1)<128)return t.substring(0,2).toUpperCase();if(t.length()>0)return t.substring(0,1);return "P"+(pl+1);} 
        private int cumulativeDeltaV1152(int pl){int d=0;for(int h0=1;h0<=18;h0++){int pa=parForHole(h0);d+=getStroke(pl,h0,pa)-pa;}return d;}
        private String signedV1152(int v){return v>0?"+"+v:""+v;}
'''
    if field not in s: raise SystemExit('V1.15.6 helper field anchor missing')
    s=s.replace(field,field+'\n'+hp,1)

if 'V1.15.6 · MASTER SOURCE MAPPER' not in s:s=s.replace('V1.15.1 · REFERENCE POLISH','V1.15.1 · REFERENCE POLISH / V1.15.6 · MASTER SOURCE MAPPER',1)
p.write_text(s)
print('V1.15.6 MASTER SOURCE MAPPER: every registered course raw source -> one built-in approved design renderer; no per-hole image generation')
