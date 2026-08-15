from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'roundMasterMappedV1160' in s:
    print('V1.16.0 master renderer already applied')
    raise SystemExit(0)
if 'fullHoleBitmapV1102' not in s or 'verifiedMetersV190' not in s:
    raise SystemExit('V1.16.0 requires full-hole source + verified distance pipeline')

legacy='        private void roundKorea(Canvas c){'
if legacy not in s:
    raise SystemExit('V1.16.0 roundKorea anchor missing')
s=s.replace(legacy,'        private void roundKoreaLegacyV1160(Canvas c){',1)

anchor='        private void roundKoreaLegacyV1160(Canvas c){'
idx=s.find(anchor)
if idx<0:
    raise SystemExit('V1.16.0 renamed Korea renderer missing')

helpers=r'''
        // MASTER TEMPLATE RENDERER V1.16.0
        // One built-in design renderer + external/source yardage bitmaps.
        // New courses only need source images and structured yardage data.
        private int masterRemainV1160(int totalM){
            GeoRef g=greenCenterRef(hole);
            if(g!=null && gpsUsable())return Math.max(0,Math.round(distance(location,g.lat,g.lon)));
            int r=navRemainV1110(totalM);return r>=0?r:Math.max(0,totalM);
        }
        private int masterDeltaV1160(int pl){
            int d=0;for(int h0=1;h0<=18;h0++){int pa=parForHole(h0);d+=getStroke(pl,h0,pa)-pa;}return d;
        }
        private String masterInitialV1160(String n,int pl){
            if(n==null)n="";String t=n.trim();
            if(t.contains("희권"))return "HK";if(t.contains("경집"))return "KJ";if(t.contains("시형"))return "SY";if(t.contains("중수"))return "JS";
            if(t.length()>=2 && t.charAt(0)<128 && t.charAt(1)<128)return t.substring(0,2).toUpperCase();
            return t.length()>0?t.substring(0,1):("P"+(pl+1));
        }
        private void masterTextV1160(Canvas c,String s,float x,float y,float z,int color,Paint.Align a,boolean outline){
            p.setShader(null);p.clearShadowLayer();p.setTextAlign(a);p.setTextSize(z);p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));
            if(outline){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(Math.max(2f,z*.10f));p.setStrokeJoin(Paint.Join.ROUND);p.setColor(Color.rgb(18,20,14));c.drawText(s,x,y,p);}
            p.setStyle(Paint.Style.FILL);p.setColor(color);c.drawText(s,x,y,p);p.setStrokeJoin(Paint.Join.MITER);
        }
        private void masterWoodV1160(Canvas c,RectF r){
            LinearGradient g=new LinearGradient(r.left,r.top,r.left,r.bottom,Color.rgb(139,82,34),Color.rgb(92,49,18),Shader.TileMode.CLAMP);
            p.setShader(g);c.drawRoundRect(r,26,26,p);p.setShader(null);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.rgb(63,34,15));c.drawRoundRect(r,26,26,p);
            p.setStrokeWidth(1.2f);p.setColor(Color.argb(75,255,213,149));
            for(int k=0;k<8;k++){float y=r.top+24+k*20;c.drawLine(r.left+20,y,r.right-20,y+(k%2==0?4:-4),p);}
            p.setStyle(Paint.Style.FILL);
        }
        private void masterScorePanelV1160(Canvas c){
            RectF q=new RectF(18,477,220,1320);
            p.setColor(Color.rgb(10,80,15));c.drawRoundRect(q,28,28,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4);p.setColor(Color.rgb(5,43,8));c.drawRoundRect(q,28,28,p);p.setStyle(Paint.Style.FILL);
            masterTextV1160(c,"PAR",106,542,31,Color.WHITE,Paint.Align.RIGHT,true);
            masterTextV1160(c,""+currentPar(),114,542,31,Color.rgb(255,190,35),Paint.Align.LEFT,true);
            masterTextV1160(c,"H"+hole,119,620,70,Color.WHITE,Paint.Align.CENTER,true);
            float[] yy={760,910,1060,1210};
            int[] ac={Color.rgb(28,105,219),Color.rgb(35,139,72),Color.rgb(255,158,20),Color.rgb(136,48,205)};
            String[] demo={"희권","경집","시형","중수"};int[] dd={3,5,-1,8};
            for(int pl=0;pl<4;pl++){
                String nm=previewMode?demo[pl]:playerName(pl);if(nm==null||nm.trim().isEmpty())nm="P"+(pl+1);
                int delta=previewMode?dd[pl]:masterDeltaV1160(pl);float cy=yy[pl];
                p.setColor(ac[pl]);c.drawCircle(70,cy,28,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.WHITE);c.drawCircle(70,cy,26,p);p.setStyle(Paint.Style.FILL);
                masterTextV1160(c,masterInitialV1160(nm,pl),70,cy+8,22,Color.WHITE,Paint.Align.CENTER,false);
                masterTextV1160(c,nm,132,cy-8,28,Color.WHITE,Paint.Align.LEFT,true);
                int sc=delta<0?Color.rgb(38,150,255):(delta>0?Color.rgb(255,78,69):Color.WHITE);
                masterTextV1160(c,(delta>0?"+":"")+delta,166,cy+45,40,sc,Paint.Align.CENTER,true);
            }
        }
        private void masterTargetButtonV1160(Canvas c){
            RectF b=new RectF(638,1261,908,1388);
            LinearGradient g=new LinearGradient(b.left,b.top,b.left,b.bottom,Color.rgb(249,222,173),Color.rgb(224,168,74),Shader.TileMode.CLAMP);
            p.setShader(g);c.drawRoundRect(b,48,48,p);p.setShader(null);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.rgb(136,87,38));c.drawRoundRect(b,48,48,p);p.setStyle(Paint.Style.FILL);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);p.setColor(Color.rgb(25,23,17));c.drawCircle(705,1325,22,p);c.drawCircle(705,1325,7,p);c.drawLine(671,1325,683,1325,p);c.drawLine(727,1325,739,1325,p);c.drawLine(705,1291,705,1303,p);c.drawLine(705,1347,705,1359,p);p.setStyle(Paint.Style.FILL);
            masterTextV1160(c,"타겟",805,1337,34,Color.rgb(25,23,17),Paint.Align.CENTER,false);
        }
        private void masterRulerV1160(Canvas c,int totalM){
            int top=Math.max(250,((Math.max(1,totalM)+49)/50)*50);float x=798,y0=655,y1=1165;
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);p.setColor(Color.rgb(78,72,53));c.drawLine(x,y0,x,y1,p);
            for(int v=top;v>=50;v-=50){
                float y=y1-(v/(float)top)*(y1-y0);c.drawLine(x,y,x+18,y,p);
                masterTextV1160(c,v+"m",832,y+7,20,Color.rgb(42,40,31),Paint.Align.LEFT,false);
            }
            p.setStyle(Paint.Style.FILL);
            if(top>=200){
                float y=y1-(200f/top)*(y1-y0);RectF tag=new RectF(650,y-29,781,y+29);
                p.setColor(Color.rgb(31,92,196));c.drawRoundRect(tag,27,27,p);
                p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.WHITE);c.drawRoundRect(tag,27,27,p);p.setStyle(Paint.Style.FILL);
                masterTextV1160(c,"200m",715,y+9,25,Color.WHITE,Paint.Align.CENTER,true);
                p.setColor(Color.WHITE);c.drawCircle(x,y,13,p);p.setColor(Color.rgb(255,140,30));c.drawCircle(x,y,7,p);
            }
        }
        private void roundMasterMappedV1160(Canvas c){
            float w=getWidth(),h=getHeight(),sx=w/941f,sy=h/1672f;
            int par=currentPar(),totalM=verifiedMetersV190(),remain=masterRemainV1160(totalM);
            Bitmap course=fullHoleBitmapV1102();
            c.save();c.scale(sx,sy);
            c.drawColor(Color.rgb(246,236,207));
            RectF head=new RectF(0,0,941,156);LinearGradient hg=new LinearGradient(0,0,941,156,Color.rgb(8,48,146),Color.rgb(12,87,199),Shader.TileMode.CLAMP);p.setShader(hg);c.drawRect(head,p);p.setShader(null);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(7);p.setStrokeCap(Paint.Cap.SQUARE);p.setColor(Color.WHITE);c.drawLine(64,55,38,78,p);c.drawLine(38,78,64,101,p);p.setStyle(Paint.Style.FILL);p.setStrokeCap(Paint.Cap.BUTT);
            masterTextV1160(c,ko[selected],90,64,38,Color.WHITE,Paint.Align.LEFT,false);
            masterTextV1160(c,variants[selected][variant]+" · H"+hole+" · PAR "+par,91,126,28,Color.WHITE,Paint.Align.LEFT,false);
            masterTextV1160(c,gpsStatusShort(),866,72,24,Color.WHITE,Paint.Align.RIGHT,false);

            RectF board=new RectF(18,156,923,350);masterWoodV1160(c,board);
            p.setColor(Color.argb(100,35,18,7));c.drawRect(318,170,321,330,p);c.drawRect(620,170,623,330,p);
            GeoRef gc=greenCenterRef(hole),gf=getRef("gf",hole),gb=getRef("gb",hole);Distances ds=distances3(gf,gc,gb);
            String fv=ds.front>=0?ds.front+"m":"--";String cv=ds.center>=0?ds.center+"m":(totalM>0?totalM+"m":"--");String bv=ds.back>=0?ds.back+"m":"--";
            String[] val={fv,cv,bv};String[] lab={"FRONT","CENTER","BACK"};int[] col={Color.rgb(29,145,255),Color.WHITE,Color.rgb(255,82,74)};float[] cx={166,470,775};
            for(int i=0;i<3;i++){masterTextV1160(c,val[i],cx[i],260,58,col[i],Paint.Align.CENTER,true);masterTextV1160(c,lab[i],cx[i],313,27,Color.WHITE,Paint.Align.CENTER,true);}

            masterScorePanelV1160(c);

            RectF bubble=new RectF(714,397,918,575);p.setColor(Color.rgb(255,248,224));c.drawRoundRect(bubble,28,28,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.rgb(34,31,24));c.drawRoundRect(bubble,28,28,p);p.setStyle(Paint.Style.FILL);
            Path tail=new Path();tail.moveTo(720,527);tail.lineTo(692,580);tail.lineTo(748,548);tail.close();p.setColor(Color.rgb(255,248,224));c.drawPath(tail,p);
            masterTextV1160(c,"남은 거리",816,442,25,Color.rgb(31,30,24),Paint.Align.CENTER,false);masterTextV1160(c,remain+"m",816,507,47,Color.rgb(25,25,20),Paint.Align.CENTER,false);masterTextV1160(c,"핀까지",816,555,23,Color.rgb(31,30,24),Paint.Align.CENTER,false);

            RectF slot=new RectF(248,360,650,1450);
            if(course!=null){
                RectF dst=fitCenterV1102(course,slot);Paint bp=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);c.drawBitmap(course,null,dst,bp);
            }else{
                p.setColor(Color.rgb(222,235,205));c.drawRoundRect(slot,30,30,p);masterTextV1160(c,"COURSE SOURCE",slot.centerX(),slot.centerY(),26,Color.rgb(35,90,50),Paint.Align.CENTER,false);
            }
            masterRulerV1160(c,totalM);masterTargetButtonV1160(c);
            c.restore();

            courseRect.set(248*sx,360*sy,650*sx,1450*sy);
            mapLaunch.set(638*sx,1261*sy,908*sx,1388*sy);
            greenSave.setEmpty();teeSave.setEmpty();autoBtn.setEmpty();prev.setEmpty();next.setEmpty();mapTab.setEmpty();scoreTab.setEmpty();
            setFourNav(w,h);drawGoldenNav(c);
        }
        private void roundKorea(Canvas c){
            if(selected==4){roundMasterMappedV1160(c);return;}
            roundKoreaLegacyV1160(c);
        }

'''
s=s[:idx]+helpers+s[idx:]

p.write_text(s)
print('V1.16.0 MASTER TEMPLATE RENDERER: Royal Links uses one built-in UI renderer + raw official hole source bitmaps; no per-hole UI image generation')
