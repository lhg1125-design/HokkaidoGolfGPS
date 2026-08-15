from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.15.1 · REFERENCE POLISH' not in s:
    raise SystemExit('V1.15.2 requires V1.15.1 reference polish')
if 'V1.15.2 · FURANO KING123 GOLDEN' not in s:
    s=s.replace('V1.15.1 · REFERENCE POLISH','V1.15.1 · REFERENCE POLISH / V1.15.2 · FURANO KING123 GOLDEN',1)

if 'import android.graphics.Bitmap;' not in s:
    s=s.replace('import android.graphics.Canvas;','import android.graphics.Bitmap;\nimport android.graphics.BitmapFactory;\nimport android.graphics.Canvas;',1)
elif 'import android.graphics.BitmapFactory;' not in s:
    s=s.replace('import android.graphics.Bitmap;','import android.graphics.Bitmap;\nimport android.graphics.BitmapFactory;',1)

field='        private Typeface conceptKoV1130,conceptJpV1130;'
if field not in s: raise SystemExit('V1.15.2 typeface field anchor missing')
if 'furanoKingH1BaseV1152' not in s:
    s=s.replace(field,field+'\n        private Bitmap furanoKingH1BaseV1152,furanoKingH2BaseV1152,furanoKingH3BaseV1152;',1)

helper_anchor='        private boolean coverHudV1138(){'
pos=s.find(helper_anchor)
if pos<0: raise SystemExit('V1.15.2 helper anchor missing')
helpers=r'''        private boolean furanoKing123V1152(){
            return screen==1 && selected==1 && variant==1 && hole>=1 && hole<=3 && getHeight()>=getWidth()*1.55f;
        }
        private Bitmap furanoKingBaseV1152(){
            if(hole==1){if(furanoKingH1BaseV1152==null)furanoKingH1BaseV1152=BitmapFactory.decodeResource(getResources(),R.drawable.furano_king_h1_base_v1152);return furanoKingH1BaseV1152;}
            if(hole==2){if(furanoKingH2BaseV1152==null)furanoKingH2BaseV1152=BitmapFactory.decodeResource(getResources(),R.drawable.furano_king_h2_base_v1152);return furanoKingH2BaseV1152;}
            if(furanoKingH3BaseV1152==null)furanoKingH3BaseV1152=BitmapFactory.decodeResource(getResources(),R.drawable.furano_king_h3_base_v1152);return furanoKingH3BaseV1152;
        }
        private void masterTextV1152(Canvas c,String s,float x,float y,float z,int fill,Paint.Align align,boolean outline){
            p.setShader(null);p.clearShadowLayer();p.setTextAlign(align);p.setTextSize(z);p.setTypeface(conceptTypefaceV1130(s,true));
            if(outline){p.setStyle(Paint.Style.STROKE);p.setStrokeJoin(Paint.Join.ROUND);p.setStrokeWidth(Math.max(2.2f,z*.105f));p.setColor(Color.rgb(12,18,10));c.drawText(s,x,y,p);}
            p.setStyle(Paint.Style.FILL);p.setColor(fill);c.drawText(s,x,y,p);p.setStrokeJoin(Paint.Join.MITER);
        }
        private String furanoInitialV1152(String n,int pl){
            if(n==null)n="";String t=n.trim();
            if(t.contains("희권"))return "HK";if(t.contains("경집"))return "KJ";if(t.contains("시형"))return "SY";if(t.contains("중수"))return "JS";
            if(t.length()>=2 && t.charAt(0)<128 && t.charAt(1)<128)return t.substring(0,2).toUpperCase();
            if(t.length()>0)return t.substring(0,1);return "P"+(pl+1);
        }
        private int cumulativeDeltaV1152(int pl){
            int d=0;for(int h0=1;h0<=18;h0++){int pa=parForHole(h0);d+=getStroke(pl,h0,pa)-pa;}return d;
        }
        private String signedV1152(int v){return v>0?"+"+v:""+v;}
        private int furanoRemainV1152(int totalM){
            if(previewMode)return totalM;GeoRef g=greenCenterRef(hole);if(g!=null&&gpsUsable())return Math.max(0,Math.round(distance(location,g.lat,g.lon)));
            int r=navRemainV1110(totalM);return r>=0?r:totalM;
        }
        private RectF furanoCourseMasterRectV1152(){
            if(hole==1)return new RectF(267.41f,365f,672.59f,1422f);
            if(hole==2)return new RectF(302.20f,365f,637.80f,1422f);
            return new RectF(339.20f,365f,600.80f,1422f);
        }
        private void drawFuranoKing123V1152(Canvas c){
            float w=getWidth(),h=getHeight(),sx=w/941f,sy=h/1672f;Bitmap bg=furanoKingBaseV1152();
            p.setShader(null);p.clearShadowLayer();p.setAlpha(255);p.setStyle(Paint.Style.FILL);c.drawBitmap(bg,null,new RectF(0,0,w,h),p);
            RectF mr=furanoCourseMasterRectV1152();courseRect.set(mr.left*sx,mr.top*sy,mr.right*sx,mr.bottom*sy);
            mapLaunch.set(638f*sx,1261f*sy,908f*sx,1388f*sy);greenSave.setEmpty();teeSave.setEmpty();autoBtn.setEmpty();prev.setEmpty();next.setEmpty();mapTab.setEmpty();scoreTab.setEmpty();
            int totalM=(int)Math.round(currentYards()*.9144);int remain=furanoRemainV1152(totalM);
            c.save();c.scale(sx,sy);
            masterTextV1152(c,remain+"m",816,500,48,Color.rgb(25,25,20),Paint.Align.CENTER,false);
            float[] yy={760f,910f,1060f,1210f};int[] ac={Color.rgb(28,105,219),Color.rgb(35,139,72),Color.rgb(255,158,20),Color.rgb(136,48,205)};
            String[] demoN={"희권","경집","시형","중수"};int[] demoD={3,5,-1,8};
            for(int pl=0;pl<4;pl++){
                String nm=previewMode?demoN[pl]:playerName(pl);if(nm==null||nm.trim().isEmpty())nm="P"+(pl+1);int delta=previewMode?demoD[pl]:cumulativeDeltaV1152(pl);float cy=yy[pl];
                p.setStyle(Paint.Style.FILL);p.setColor(Color.argb(70,0,0,0));c.drawCircle(73,cy+4,31,p);p.setColor(ac[pl]);c.drawCircle(70,cy,29,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.rgb(245,250,232));c.drawCircle(70,cy,27,p);p.setStyle(Paint.Style.FILL);
                masterTextV1152(c,furanoInitialV1152(nm,pl),70,cy+9,24,Color.WHITE,Paint.Align.CENTER,false);
                float nz=nm.length()>3?25f:30f;masterTextV1152(c,nm,132,cy-8,nz,Color.WHITE,Paint.Align.LEFT,true);
                int sc=delta<0?Color.rgb(40,151,255):(delta>0?Color.rgb(255,79,70):Color.WHITE);masterTextV1152(c,signedV1152(delta),166,cy+45,42,sc,Paint.Align.CENTER,true);
            }
            float q=totalM<=0?0f:Math.max(0f,Math.min(1f,1f-remain/(float)totalM));float px=mr.centerX(),py=mr.bottom-q*mr.height();
            p.setColor(Color.argb(70,0,0,0));c.drawCircle(px+4,py+6,17,p);p.setColor(Color.WHITE);c.drawCircle(px,py,15,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.rgb(31,103,57));c.drawCircle(px,py,15,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(31,103,57));c.drawCircle(px,py,4,p);
            if(hasTarget){float tx=targetX/sx,ty=targetY/sy;p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);p.setColor(Color.rgb(244,91,55));c.drawCircle(tx,ty,20,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(244,91,55));c.drawCircle(tx,ty,6,p);}
            c.restore();p.setAlpha(255);p.setStyle(Paint.Style.FILL);
        }
'''
if 'private void drawFuranoKing123V1152' not in s:
    s=s[:pos]+helpers+s[pos:]

round_sig='        private void round(Canvas c){'
if round_sig not in s: raise SystemExit('V1.15.2 round anchor missing')
if 'if(furanoKing123V1152())' not in s:
    s=s.replace(round_sig,round_sig+'\n            if(furanoKing123V1152()){drawFuranoKing123V1152(c);return;}',1)

touch='            if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();'
if touch not in s: raise SystemExit('V1.15.2 touch anchor missing')
if 'V1152 golden touch' not in s:
    block=r'''
            // V1152 golden touch: four visible tabs + course target only.
            if(screen==1 && selected==1 && variant==1 && hole>=1 && hole<=3 && getHeight()>=getWidth()*1.55f){
                float w=getWidth(),h=getHeight(),sx=w/941f,sy=h/1672f;
                RectF n0=new RectF(18*sx,1458*sy,244*sx,1652*sy),n1=new RectF(244*sx,1458*sy,470*sx,1652*sy),n2=new RectF(470*sx,1458*sy,696*sx,1652*sy),n3=new RectF(696*sx,1458*sy,923*sx,1652*sy);
                if(x<105*sx&&y<105*sy){screen=0;saveState();invalidate();return true;}
                if(n0.contains(x,y)){screen=2;invalidate();return true;}
                if(n1.contains(x,y)){invalidate();return true;}
                if(n2.contains(x,y)||mapLaunch.contains(x,y)){showToast("코스 위 목표 지점을 터치하세요");invalidate();return true;}
                if(n3.contains(x,y)){screen=0;saveState();invalidate();return true;}
                if(courseRect.contains(x,y)){targetX=x;targetY=y;hasTarget=true;showToast("타겟 지정 완료");invalidate();return true;}
                return true;
            }
'''
    s=s.replace(touch,touch+block,1)

p.write_text(s)
print('V1.15.2 FURANO KING123 GOLDEN: only KING H1/H2/H3 use approved fixed-layout bases + verified course pixels + runtime GPS/player overlays')
