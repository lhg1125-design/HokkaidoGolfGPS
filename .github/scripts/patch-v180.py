from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.7.0 · KOREA FIELD TEST' not in s:
    raise SystemExit('v1.8.0 base version not found')
s=s.replace('V1.7.0 · KOREA FIELD TEST','V1.8.0 · PREMIUM COURSE ART',1)

# Premium art cache is decoded only when the selected course changes.
anchor='private final Bitmap v12Home,v12Course,v12Score;'
if anchor not in s:
    raise SystemExit('v1.8 bitmap field anchor missing')
s=s.replace(anchor,anchor+'\n        private Bitmap v18CourseArt;\n        private int v18CourseArtIndex=-99;',1)

# Add premium image helpers before Korea renderer. Artwork is visual; factual
# yardage/PAR/GPS data stays in the structured model and overlays.
marker='        private void roundKorea(Canvas c){'
idx=s.find(marker)
if idx<0: raise SystemExit('v1.8 Korea round marker missing')
helpers=r'''        private Bitmap premiumCourseArt(){
            if(v18CourseArt!=null && v18CourseArtIndex==selected)return v18CourseArt;
            String[] n={"kami","furano","sahoro","naepo","royal"};
            if(selected<0||selected>=n.length)return null;
            int id=getResources().getIdentifier("v18_course_"+n[selected],"drawable",ctx.getPackageName());
            v18CourseArt=id==0?null:BitmapFactory.decodeResource(getResources(),id);
            v18CourseArtIndex=selected;
            return v18CourseArt;
        }
        private String premiumArtLabel(){
            if(selected==0)return "HOKKAIDO · TOKACHI SCENE";
            if(selected==1)return "FURANO · RESORT COURSE";
            if(selected==2)return "SAHORO · HIGHLAND COURSE";
            if(selected==3)return "AERIAL REF · FIELD GPS CAL";
            if(selected==4)return "ROYAL LINKS · COURSE ART";
            return "PREMIUM COURSE ART";
        }
        private void drawPremiumCourseArt(Canvas c,RectF r){
            Bitmap b=premiumCourseArt();
            if(b==null)return;
            float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/420.0));
            c.save();Path cp=new Path();cp.addRoundRect(r,34,34,Path.Direction.CW);c.clipPath(cp);
            // very small parallax drift keeps the approved artwork feeling alive without
            // pretending that the image itself is a georeferenced position map.
            float dx=(float)Math.sin(SystemClock.uptimeMillis()/2200.0)*5f;
            RectF dst=new RectF(r.left-7+dx,r.top-7,r.right+7+dx,r.bottom+7);
            c.drawBitmap(b,null,dst,p);
            p.setColor(Color.argb(38,5,45,27));c.drawRect(r,p);
            float sweep=(SystemClock.uptimeMillis()%3600L)/3600f;
            float sx=r.left-r.width()*.25f+sweep*r.width()*1.5f;
            LinearGradient lg=new LinearGradient(sx-85,r.top,sx+85,r.bottom,
                    new int[]{Color.argb(0,255,255,255),Color.argb(42,255,255,255),Color.argb(0,255,255,255)},
                    new float[]{0f,.5f,1f},Shader.TileMode.CLAMP);
            p.setShader(lg);c.drawRect(r,p);p.setShader(null);c.restore();
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.argb(155,255,255,255));c.drawRoundRect(r,34,34,p);p.setStyle(Paint.Style.FILL);
            RectF chip=new RectF(r.left+15,r.top+15,Math.min(r.right-15,r.left+r.width()*.56f),r.top+53);
            pill(c,chip,Color.argb(226,255,255,255),premiumArtLabel(),DEEP,6.6f);
            // animated live-dot only means the screen is live, not a map coordinate.
            float lx=r.right-31,ly=r.top+34;p.setColor(Color.argb(85+(int)(100*pulse),255,255,255));c.drawCircle(lx,ly,15+6*pulse,p);p.setColor(GREEN);c.drawCircle(lx,ly,7,p);
        }
        private void drawKoreaArtOverlay(Canvas c,RectF r,int par,int officialM){
            RectF stat=new RectF(r.left+18,r.bottom-70,r.right-18,r.bottom-20);box(c,stat,Color.argb(226,255,255,255),22);
            String main;
            if(selected==4)main="H"+hole+" · PAR "+par+" · WHITE "+officialM+"m";
            else if(officialM>0)main=koreaHoleLabel()+" · PAR "+par+" · FIELD "+officialM+"m";
            else main=koreaHoleLabel()+" · PAR "+par+" · TEE/GREEN GPS 저장";
            goldText(c,main,stat.centerX(),stat.centerY(),12.2f,DEEP);
        }

'''
s=s[:idx]+helpers+s[idx:]

# Japan: cover the old coarse 2D map core with the high-resolution premium art.
jp_anchor='            courseRect.set(w*.07f,h*.258f,w*.93f,h*.669f);'
if jp_anchor not in s:
    raise SystemExit('v1.8 Japan courseRect anchor missing')
s=s.replace(jp_anchor,jp_anchor+'\n            drawPremiumCourseArt(c,courseRect);',1)

# The old marker was a progress abstraction; rename it so it is never read as
# a precise geospatial "you are here" point on scenic artwork.
s=s.replace('text(c,"YOU",xx,yy+34,8,Color.WHITE,true,Paint.Align.CENTER);','text(c,"LIVE",xx,yy+34,8,Color.WHITE,true,Paint.Align.CENTER);',1)

# Korea: replace the rough vector sketch with the same premium art language.
kr_old='            courseRect.set(m,h*.278f,w-m,h*.600f);drawKoreaYardage(c,courseRect,par,officialM);'
kr_new='            courseRect.set(m,h*.278f,w-m,h*.600f);drawPremiumCourseArt(c,courseRect);drawKoreaArtOverlay(c,courseRect,par,officialM);'
if kr_old not in s:
    raise SystemExit('v1.8 Korea rough-map anchor missing')
s=s.replace(kr_old,kr_new,1)

# Premium view uses factual distance chips; remove the old footer phrase if the
# fallback vector renderer is ever used elsewhere.
s=s.replace('VECTOR YARDAGE · CRISP AT DEVICE RESOLUTION','PREMIUM ART · STRUCTURED YARDAGE DATA')

p.write_text(s)
print('applied v1.8.0 premium animated course-art UI')
