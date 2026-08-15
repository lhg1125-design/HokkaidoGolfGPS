from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'masterSourceRectV1161' not in s or 'roundMasterMappedV1160' not in s:
    raise SystemExit('V1.16.2 requires V1.16.1 raw mapper')
if 'GOLDEN MASTER V1.16.2' in s:
    print('V1.16.2 golden master already applied'); raise SystemExit(0)

anchor='        private boolean masterSourceMappedV1161(){'
pos=s.find(anchor)
if pos<0: raise SystemExit('V1.16.2 insertion anchor missing')
helpers=r'''        // GOLDEN MASTER V1.16.2
        // User-approved V1.15.2/V1.15.4 Storybook chrome + runtime raw course mapping.
        // Raw official JPG bytes remain untouched; only an in-memory edge-connected
        // neutral page is made transparent for display.
        private android.graphics.Bitmap masterGoldenChromeV1162;
        private android.graphics.Bitmap masterGoldenCourseV1162;
        private android.graphics.Rect masterGoldenCropV1162;
        private String masterGoldenKeyV1162;

        private android.graphics.Bitmap goldenChromeV1162(){
            if(masterGoldenChromeV1162==null || masterGoldenChromeV1162.isRecycled()){
                masterGoldenChromeV1162=android.graphics.BitmapFactory.decodeResource(getResources(),R.drawable.master_golden_chrome_v1162);
            }
            return masterGoldenChromeV1162;
        }
        private boolean goldenNeutralV1162(int cc){
            int r=Color.red(cc),g=Color.green(cc),b=Color.blue(cc);
            int hi=Math.max(r,Math.max(g,b)),lo=Math.min(r,Math.min(g,b));
            return r>233 && g>233 && b>222 && (hi-lo)<44;
        }
        private android.graphics.Bitmap goldenCourseV1162(){
            String key=fullHoleResourceV1102();
            if(key==null)return null;
            if(key.equals(masterGoldenKeyV1162) && masterGoldenCourseV1162!=null && !masterGoldenCourseV1162.isRecycled())return masterGoldenCourseV1162;
            if(masterGoldenCourseV1162!=null && !masterGoldenCourseV1162.isRecycled())try{masterGoldenCourseV1162.recycle();}catch(Exception ignored){}
            masterGoldenCourseV1162=null;masterGoldenCropV1162=null;masterGoldenKeyV1162=key;
            android.graphics.Bitmap raw=masterCourseBitmapV1161();if(raw==null)return null;
            int w=raw.getWidth(),h=raw.getHeight(),n=w*h;if(n<=0)return null;
            int[] px=new int[n];raw.getPixels(px,0,w,0,0,w,h);
            byte[] seen=new byte[n];int[] q=new int[n];int head=0,tail=0;
            for(int x=0;x<w;x++){
                int a=x,b=(h-1)*w+x;
                if(seen[a]==0&&goldenNeutralV1162(px[a])){seen[a]=1;q[tail++]=a;}
                if(seen[b]==0&&goldenNeutralV1162(px[b])){seen[b]=1;q[tail++]=b;}
            }
            for(int y=0;y<h;y++){
                int a=y*w,b=y*w+w-1;
                if(seen[a]==0&&goldenNeutralV1162(px[a])){seen[a]=1;q[tail++]=a;}
                if(seen[b]==0&&goldenNeutralV1162(px[b])){seen[b]=1;q[tail++]=b;}
            }
            while(head<tail){
                int i=q[head++],x=i%w,y=i/w,nb;
                if(x>0){nb=i-1;if(seen[nb]==0&&goldenNeutralV1162(px[nb])){seen[nb]=1;q[tail++]=nb;}}
                if(x+1<w){nb=i+1;if(seen[nb]==0&&goldenNeutralV1162(px[nb])){seen[nb]=1;q[tail++]=nb;}}
                if(y>0){nb=i-w;if(seen[nb]==0&&goldenNeutralV1162(px[nb])){seen[nb]=1;q[tail++]=nb;}}
                if(y+1<h){nb=i+w;if(seen[nb]==0&&goldenNeutralV1162(px[nb])){seen[nb]=1;q[tail++]=nb;}}
            }
            int minX=w,minY=h,maxX=-1,maxY=-1;
            for(int i=0;i<n;i++){
                if(seen[i]!=0){px[i]=px[i]&0x00ffffff;continue;}
                if(Color.alpha(px[i])!=0){int x=i%w,y=i/w;if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y;}
            }
            masterGoldenCourseV1162=android.graphics.Bitmap.createBitmap(px,w,h,android.graphics.Bitmap.Config.ARGB_8888);
            if(maxX<minX||maxY<minY)masterGoldenCropV1162=new android.graphics.Rect(0,0,w,h);
            else{int pad=Math.max(3,Math.min(w,h)/100);masterGoldenCropV1162=new android.graphics.Rect(Math.max(0,minX-pad),Math.max(0,minY-pad),Math.min(w,maxX+pad+1),Math.min(h,maxY+pad+1));}
            return masterGoldenCourseV1162;
        }
        private void goldenTextV1162(Canvas c,String s,float x,float y,float z,int fill,Paint.Align align,boolean outline){
            p.setShader(null);p.clearShadowLayer();p.setAlpha(255);p.setTextAlign(align);p.setTextSize(z);p.setTypeface(conceptTypefaceV1130(s,true));
            if(outline){p.setStyle(Paint.Style.STROKE);p.setStrokeJoin(Paint.Join.ROUND);p.setStrokeWidth(Math.max(2.2f,z*.105f));p.setColor(Color.rgb(12,18,10));c.drawText(s,x,y,p);}
            p.setStyle(Paint.Style.FILL);p.setColor(fill);c.drawText(s,x,y,p);p.setStrokeJoin(Paint.Join.MITER);
        }
        private void goldenMetricV1162(Canvas c,int value,float cx,int col){
            if(value<0){goldenTextV1162(c,"--",cx,261,58,col,Paint.Align.CENTER,true);return;}
            String ss=String.valueOf(value);goldenTextV1162(c,ss,cx-6,261,70,col,Paint.Align.CENTER,true);
            goldenTextV1162(c,"m",cx+74,260,28,col,Paint.Align.CENTER,true);
        }
        private String goldenInitialV1162(String n,int pl){
            if(n==null)n="";String t=n.trim();
            if(t.contains("희권"))return "HK";if(t.contains("경집"))return "KJ";if(t.contains("시형"))return "SY";if(t.contains("중수"))return "JS";
            if(t.length()>=2&&t.charAt(0)<128&&t.charAt(1)<128)return t.substring(0,2).toUpperCase();
            return t.length()>0?t.substring(0,1):("P"+(pl+1));
        }
        private int goldenDeltaV1162(int pl){int d=0;for(int h0=1;h0<=18;h0++){int pa=parForHole(h0);d+=getStroke(pl,h0,pa)-pa;}return d;}
        private String goldenSignedV1162(int v){return v>0?"+"+v:String.valueOf(v);}
        private void goldenRulerV1162(Canvas c,int totalM){
            int top=Math.max(150,((Math.max(1,totalM)+49)/50)*50);float x=798,y0=655,y1=1165;
            p.setShader(null);p.clearShadowLayer();p.setAlpha(255);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);p.setColor(Color.rgb(78,72,53));c.drawLine(x,y0,x,y1,p);
            for(int v=top;v>=50;v-=50){
                float y=y1-(v/(float)top)*(y1-y0);c.drawLine(x,y,x+18,y,p);goldenTextV1162(c,v+"m",832,y+7,20,Color.rgb(42,40,31),Paint.Align.LEFT,false);
            }
            p.setStyle(Paint.Style.FILL);
            if(top>=200){
                float y=y1-(200f/top)*(y1-y0);RectF tag=new RectF(646,y-30,777,y+30);p.setColor(Color.rgb(31,92,196));c.drawRoundRect(tag,27,27,p);
                p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.WHITE);c.drawRoundRect(tag,27,27,p);p.setStyle(Paint.Style.FILL);
                goldenTextV1162(c,"200m",711,y+9,26,Color.WHITE,Paint.Align.CENTER,true);p.setColor(Color.WHITE);c.drawCircle(x,y,13,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);p.setColor(Color.rgb(39,38,27));c.drawCircle(x,y,13,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(255,140,30));c.drawCircle(x,y,7,p);
            }
        }
        private void drawGoldenMasterV1162(Canvas c){
            final float w=getWidth(),h=getHeight(),sx=w/941f,sy=h/1672f;
            android.graphics.Bitmap chrome=goldenChromeV1162();
            p.setShader(null);p.clearShadowLayer();p.setAlpha(255);p.setStyle(Paint.Style.FILL);p.setFilterBitmap(true);
            if(chrome!=null)c.drawBitmap(chrome,null,new RectF(0,0,w,h),p);else c.drawColor(Color.rgb(247,239,214));
            c.save();c.scale(sx,sy);
            int par=currentPar(),totalM=verifiedMetersV190();if(totalM<=0)totalM=(int)Math.round(currentYards()*.9144);
            int remain=masterRemainV1160(totalM);
            goldenTextV1162(c,ko[selected],96,66,38,Color.WHITE,Paint.Align.LEFT,true);
            goldenTextV1162(c,variants[selected][variant]+" · H"+hole+" · PAR "+par,96,126,29,Color.WHITE,Paint.Align.LEFT,true);
            GeoRef gc=greenCenterRef(hole),gf=getRef("gf",hole),gb=getRef("gb",hole);Distances ds=distances3(gf,gc,gb);
            int center=ds.center>=0?ds.center:totalM;goldenMetricV1162(c,ds.front,166,Color.rgb(30,145,255));goldenMetricV1162(c,center,470,Color.WHITE);goldenMetricV1162(c,ds.back,775,Color.rgb(255,80,72));
            goldenTextV1162(c,"PAR",106,553,33,Color.WHITE,Paint.Align.RIGHT,true);goldenTextV1162(c,String.valueOf(par),114,553,33,Color.rgb(255,188,36),Paint.Align.LEFT,true);goldenTextV1162(c,"H"+hole,129,635,76,Color.WHITE,Paint.Align.CENTER,true);
            float[] yy={760f,910f,1060f,1210f};int[] ac={Color.rgb(28,105,219),Color.rgb(35,139,72),Color.rgb(255,158,20),Color.rgb(136,48,205)};String[] demo={"희권","경집","시형","중수"};int[] dd={3,5,-1,8};
            for(int pl=0;pl<4;pl++){
                String nm=previewMode?demo[pl]:playerName(pl);if(nm==null||nm.trim().isEmpty())nm="P"+(pl+1);int delta=previewMode?dd[pl]:goldenDeltaV1162(pl);float cy=yy[pl];
                p.setStyle(Paint.Style.FILL);p.setColor(Color.argb(70,0,0,0));c.drawCircle(73,cy+4,31,p);p.setColor(ac[pl]);c.drawCircle(70,cy,29,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.rgb(245,250,232));c.drawCircle(70,cy,27,p);p.setStyle(Paint.Style.FILL);
                goldenTextV1162(c,goldenInitialV1162(nm,pl),70,cy+9,24,Color.WHITE,Paint.Align.CENTER,false);goldenTextV1162(c,nm,132,cy-8,nm.length()>3?25f:30f,Color.WHITE,Paint.Align.LEFT,true);int sc=delta<0?Color.rgb(40,151,255):(delta>0?Color.rgb(255,79,70):Color.WHITE);goldenTextV1162(c,goldenSignedV1162(delta),166,cy+45,42,sc,Paint.Align.CENTER,true);
            }
            goldenTextV1162(c,remain+"m",816,500,48,Color.rgb(25,25,20),Paint.Align.CENTER,false);
            android.graphics.Bitmap course=goldenCourseV1162();RectF slot=new RectF(260,365,680,1422),dst=new RectF(slot);
            if(course!=null){dst=masterFitSourceV1161(masterGoldenCropV1162,slot);Paint bp=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);c.drawBitmap(course,masterGoldenCropV1162,dst,bp);}
            courseRect.set(dst.left*sx,dst.top*sy,dst.right*sx,dst.bottom*sy);mapLaunch.set(638*sx,1261*sy,908*sx,1388*sy);
            goldenRulerV1162(c,totalM);
            if(!previewMode&&course!=null){float q=totalM<=0?0f:Math.max(0f,Math.min(1f,1f-remain/(float)totalM));float px=dst.centerX(),py=dst.bottom-q*dst.height();p.setColor(Color.argb(70,0,0,0));c.drawCircle(px+4,py+6,17,p);p.setColor(Color.WHITE);c.drawCircle(px,py,15,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.rgb(31,103,57));c.drawCircle(px,py,15,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(31,103,57));c.drawCircle(px,py,4,p);}
            if(hasTarget){float tx=targetX/sx,ty=targetY/sy;p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(5);p.setColor(Color.rgb(244,91,55));c.drawCircle(tx,ty,20,p);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(244,91,55));c.drawCircle(tx,ty,6,p);}
            c.restore();p.setAlpha(255);p.setStyle(Paint.Style.FILL);
        }
'''
s=s[:pos]+helpers+s[pos:]

generic='if(masterSourceMappedV1161()){roundMasterMappedV1160(c);return;}'
if generic not in s: raise SystemExit('V1.16.2 generic dispatch anchor missing')
s=s.replace(generic,'if(masterSourceMappedV1161()){drawGoldenMasterV1162(c);return;}',1)
s=s.replace('if(selected==4){roundMasterMappedV1160(c);return;}','if(selected==4){drawGoldenMasterV1162(c);return;}',1)

p.write_text(s)
print('V1.16.2 GOLDEN MASTER: approved Storybook chrome restored; runtime raw geometry isolated/transparently mapped; no per-hole UI regeneration')
