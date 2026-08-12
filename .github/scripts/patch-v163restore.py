from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

marker='        static final class Hazard{'
idx=s.find(marker)
if idx<0:
    marker='        static final class GeoRef{'
    idx=s.find(marker)
if idx<0:
    raise SystemExit('v1.6.3 helper restore insertion marker missing')

parts=[]
if 'private int currentPar(){' not in s:
    parts.append(r'''        private int currentPar(){return parForHole(hole);}
        private int parForHole(int h){return pars[selected][variant][h-1];}
        private int currentYards(){return yards[selected][variant][hole-1];}
        private int getStroke(int pl,int h,int par){return scorePrefs.getInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,par);}
        private int getPutt(int pl,int h){return scorePrefs.getInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,0);}
        private void setStroke(int pl,int h,int v){scorePrefs.edit().putInt("s_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply();}
        private void setPutt(int pl,int h,int v){scorePrefs.edit().putInt("p_"+selected+"_"+variant+"_"+pl+"_"+h,v).apply();}
        private int nearestCourse(Location l){int best=-1;float bd=Float.MAX_VALUE;for(int i=0;i<3;i++){float d=(float)distanceToCourse(l,i);if(d<bd){bd=d;best=i;}}return best;}
        private double distanceToCourse(Location l,int i){if(l==null)return -1;float[] o=new float[1];Location.distanceBetween(l.getLatitude(),l.getLongitude(),courseLat[i],courseLon[i],o);return o[0];}
        private int clamp(int v,int a,int b){return Math.max(a,Math.min(b,v));}

''')

if 'private void showToast(String s)' not in s:
    parts.append(r'''        private void showToast(String s){toastText=s;toastAt=SystemClock.uptimeMillis();}
        private void drawToast(Canvas c){
            if(toastAt==0)return;long age=SystemClock.uptimeMillis()-toastAt;if(age>1800)return;float w=getWidth(),h=getHeight();int a=age<1400?245:(int)(245*(1-(age-1400)/400f));
            RectF r=new RectF(w*.18f,h*.49f,w*.82f,h*.545f);box(c,r,Color.argb(Math.max(0,a),20,70,45),24);text(c,toastText,w/2,r.centerY()+5,9.5f,Color.WHITE,true,Paint.Align.CENTER);
        }
        private void drawTapBurst(Canvas c,float h){
            long age=SystemClock.uptimeMillis()-lastTap;if(age>600||lastDelta==0)return;float t=age/600f;float x=lastDelta>0?getWidth()*.43f:getWidth()*.12f,y=h*.82f-t*45;int a=(int)(255*(1-t));
            p.setColor(Color.argb(Math.min(220,a),255,255,255));c.drawCircle(x,y,18,p);text(c,lastDelta>0?"+1":"−1",x,y+5,10,Color.argb(a,24,111,68),true,Paint.Align.CENTER);
        }
        private float holeSlideOffset(long now){if(lastHoleChange==0)return 0;float t=(now-lastHoleChange)/320f;if(t>=1)return 0;float e=1-(1-t)*(1-t)*(1-t);return holeDirection*getWidth()*(1-e)*.34f;}

''')

if 'private void drawMountains(Canvas c,RectF r)' not in s:
    parts.append(r'''        private void drawMountains(Canvas c,RectF r){Path a=new Path();a.moveTo(r.left,r.top+84);a.lineTo(r.left+72,r.top+28);a.lineTo(r.left+138,r.top+84);a.close();p.setColor(Color.argb(70,100,150,112));c.drawPath(a,p);Path b=new Path();b.moveTo(r.left+88,r.top+84);b.lineTo(r.left+168,r.top+17);b.lineTo(r.left+246,r.top+84);b.close();p.setColor(Color.argb(58,70,130,95));c.drawPath(b,p);}
        private void drawCloud(Canvas c,float x,float y,float z){p.setColor(Color.argb(210,255,255,255));c.drawCircle(x,y,z*.45f,p);c.drawCircle(x+z*.4f,y-z*.1f,z*.58f,p);c.drawCircle(x+z*.86f,y,z*.42f,p);c.drawRoundRect(new RectF(x-z*.1f,y,x+z*1.15f,y+z*.38f),z*.18f,z*.18f,p);}
        private void stripes(Canvas c,Path f,RectF r,float phase){c.save();c.clipPath(f);p.setStrokeWidth(22);for(int i=-8;i<20;i++){float x=r.left+i*44+phase*44;p.setColor(i%2==0?Color.argb(18,255,255,255):Color.argb(11,20,90,40));c.drawLine(x,r.bottom,x+r.height()*.55f,r.top,p);}c.restore();}
        private void ripples(Canvas c,RectF water,float phase){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);p.setColor(Color.argb(100,255,255,255));for(int i=0;i<3;i++){float g=(phase+i*.28f)%1f,rw=water.width()*(.12f+.28f*g),rh=water.height()*(.04f+.07f*g),cy=water.centerY()+i*15;c.drawOval(new RectF(water.centerX()-rw,cy-rh,water.centerX()+rw,cy+rh),p);}p.setStyle(Paint.Style.FILL);}
        private void dashRoute(Canvas c,float x1,float y1,float x2,float y2,float phase){float dx=x2-x1,dy=y2-y1,len=(float)Math.sqrt(dx*dx+dy*dy);if(len<1)return;float ux=dx/len,uy=dy/len,start=(phase*24)%24;p.setStrokeWidth(2);p.setColor(Color.argb(170,255,255,255));for(float d=start;d<len;d+=24){float e=Math.min(d+11,len);c.drawLine(x1+ux*d,y1+uy*d,x1+ux*e,y1+uy*e,p);}}
        private void mascot(Canvas c,float x,float y,float r,boolean wave){float bob=(float)Math.sin(SystemClock.uptimeMillis()/300.0)*2;y+=bob;p.setColor(Color.argb(24,20,60,30));c.drawOval(new RectF(x-r*.8f,y+r*.78f,x+r*.8f,y+r),p);p.setColor(Color.WHITE);c.drawCircle(x,y,r,p);p.setColor(INK);c.drawCircle(x-r*.25f,y-r*.05f,r*.075f,p);c.drawCircle(x+r*.25f,y-r*.05f,r*.075f,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);c.drawArc(new RectF(x-r*.3f,y-r*.02f,x+r*.3f,y+r*.45f),15,150,false,p);p.setStyle(Paint.Style.FILL);p.setColor(GREEN);c.drawRoundRect(new RectF(x-r*.65f,y-r*.82f,x+r*.58f,y-r*.48f),r*.16f,r*.16f,p);if(wave){p.setStrokeWidth(Math.max(3,r*.12f));p.setColor(INK);c.drawLine(x+r*.68f,y,x+r*1.15f,y-r*.42f+(float)Math.sin(SystemClock.uptimeMillis()/160.0)*r*.18f,p);}}
        private void speech(Canvas c,float x,float y,String v,int col){RectF b=new RectF(x,y,x+145,y+36);softShadow(c,b,18);box(c,b,Color.argb(242,255,255,255),18);text(c,v,b.centerX(),b.centerY()+4,8.4f,col,true,Paint.Align.CENTER);}

''')

if parts:
    s=s[:idx]+''.join(parts)+s[idx:]
    p.write_text(s)
    print('restored v1.6.3 shared golf/drawing helpers')
else:
    print('v1.6.3 shared helpers already present')
