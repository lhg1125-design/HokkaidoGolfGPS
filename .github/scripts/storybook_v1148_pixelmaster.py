from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random

ROOT=Path('app/src/main/res/drawable-nodpi')
ROOT.mkdir(parents=True,exist_ok=True)
W,H=768,1600

# -----------------------------------------------------------------------------
# V1.14.8 PIXEL MASTER ASSETS
# Fixed visual chrome is rasterized ONCE at build time and used as Texture/Sprite.
# Runtime Canvas only overlays dynamic data (names/scores/hole/par/yardage/GPS).
# -----------------------------------------------------------------------------

def font(sz):
    for fp in ['/tmp/Jua-Regular.ttf','app/src/main/res/font/jua_regular.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        if Path(fp).exists():
            try:return ImageFont.truetype(fp,sz)
            except:pass
    return ImageFont.load_default()

F={k:font(v) for k,v in {'xs':18,'sm':22,'md':28,'lg':36,'xl':46,'xxl':62}.items()}
INK=(72,53,33,255); CREAM=(255,250,230,255); PAPER=(251,248,226,255)
GREEN=(19,101,64,255); GREEN2=(38,126,78,255); DEEP=(9,78,50,255)
BLUE=(44,151,207,255); BLUE2=(81,183,224,255); ORANGE=(231,121,28,255)
YELLOW=(255,207,58,255); WOOD=(139,89,42,255); WOOD2=(103,62,29,255)
BORDER=(201,169,116,255)


def shadow_round(base,box,radius,fill,blur=11,offset=(0,7),shadow=(85,60,35,72),outline=None,ow=2):
    x0,y0,x1,y1=map(int,box)
    sh=Image.new('RGBA',base.size,(0,0,0,0)); d=ImageDraw.Draw(sh)
    ox,oy=offset; d.rounded_rectangle((x0+ox,y0+oy,x1+ox,y1+oy),radius=radius,fill=shadow)
    sh=sh.filter(ImageFilter.GaussianBlur(blur)); base.alpha_composite(sh)
    d=ImageDraw.Draw(base); d.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=ow if outline else 1)
    # top sheen for 3D depth
    sheen=(255,255,255,48)
    d.rounded_rectangle((x0+3,y0+3,x1-3,y0+(y1-y0)*.43),radius=max(5,radius-3),fill=sheen)


def center_text(d,xy,text,ft,fill,stroke=0,sc=(255,255,255,0)):
    d.text(xy,text,font=ft,fill=fill,anchor='mm',stroke_width=stroke,stroke_fill=sc)


def wood_panel(base,box,r=22):
    shadow_round(base,box,r,WOOD,blur=10,offset=(0,6),shadow=(50,31,18,90),outline=(86,50,25,255),ow=3)
    d=ImageDraw.Draw(base,'RGBA'); x0,y0,x1,y1=box
    for i in range(5):
        yy=y0+18+i*(y1-y0-30)/5
        d.line((x0+15,yy,x1-15,yy+random.Random(i+31).randint(-3,3)),fill=(235,184,112,30),width=2)
    for x in [x0+(x1-x0)*.32,x0+(x1-x0)*.66]: d.line((x,y0+8,x,y1-8),fill=(67,41,24,85),width=2)


def cloud(d,x,y,s):
    c=(255,255,245,220)
    for dx,dy,rr in [(-.5,0,.42),(0,-.18,.55),(.5,.02,.40)]:
        d.ellipse((x+(dx-rr)*s,y+(dy-rr)*s,x+(dx+rr)*s,y+(dy+rr)*s),fill=c)


def tree_sprite(size=86,seed=0):
    rnd=random.Random(seed); im=Image.new('RGBA',(size,size+30),(0,0,0,0));d=ImageDraw.Draw(im,'RGBA')
    cx=size//2; d.rounded_rectangle((cx-6,size*.58,cx+6,size+22),radius=5,fill=(100,67,38,255))
    cols=[(31,117,57,255),(51,145,67,255),(84,166,72,255),(115,184,78,255)]
    for i in range(8):
        rr=rnd.randint(size//6,size//4); x=cx+rnd.randint(-size//4,size//4); y=rnd.randint(size//5,size//2)
        d.ellipse((x-rr+4,y-rr+8,x+rr+4,y+rr+8),fill=(25,74,38,65))
        d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=cols[rnd.randrange(len(cols))])
        d.ellipse((x-rr*.45,y-rr*.65,x+rr*.15,y-rr*.05),fill=(190,225,117,80))
    return im

TREE=[tree_sprite(92,i) for i in range(5)]

# ---------------- SCORE PIXEL MASTER ----------------
score=Image.new('RGBA',(W,H),PAPER); d=ImageDraw.Draw(score,'RGBA')
# header sky gradient
for y in range(0,188):
    t=y/188; col=(int(39+(82-39)*t),int(166+(196-166)*t),int(218+(228-218)*t),255); d.line((0,y,W,y),fill=col)
cloud(d,610,60,28);cloud(d,680,105,18)
center_text(d,(W/2,92),'스코어 입력',F['xl'],(255,255,255,255),2,(36,104,130,110));d.text((26,76),'‹',font(58),fill=(255,255,255,255),anchor='lm')
shadow_round(score,(604,44,744,106),30,(255,247,214,255),blur=10,offset=(0,4),shadow=(53,77,53,55),outline=(232,215,169,255),ow=2)
center_text(d,(674,75),'라운드 정보',F['sm'],INK)
# course info card
shadow_round(score,(24,202,744,330),28,(255,253,234,255),blur=12,offset=(0,7),shadow=(80,68,43,58))
# illustrated left panorama
pan=(32,210,522,322); x0,y0,x1,y1=pan
for y in range(y0,y1):
    t=(y-y0)/(y1-y0);d.line((x0,y,x1,y),fill=(int(161-55*t),int(225-35*t),int(235-60*t),255))
# distant hills
hill=[(x0,y1-35),(x0+95,y0+62),(x0+170,y1-48),(x0+250,y0+55),(x0+330,y1-52),(x1,y0+70),(x1,y1)]
d.polygon(hill,fill=(95,163,95,255))
# fairway ribbon
fair=[(x0+190,y1),(x0+215,y0+55),(x0+290,y0+35),(x0+330,y0+58),(x0+310,y1)]
d.polygon(fair,fill=(154,209,80,255))
d.ellipse((x0+90,y0+72,x0+138,y0+94),fill=(249,224,153,255));d.ellipse((x0+350,y0+68,x0+420,y0+100),fill=(67,166,213,255))
for i in range(7):
    ts=TREE[i%len(TREE)].resize((54,70)); score.alpha_composite(ts,(x0+10+i*68,y0+48+(i%2)*14))
# wood yardage card
wood_panel(score,(536,210,736,322),22);center_text(d,(636,236),'YARDAGE (CENTER)',F['xs'],(255,239,190,255))
# player rows + fixed 3D number buttons
row_top=354; row_h=126; gap=12
for r in range(4):
    y=row_top+r*(row_h+gap)
    shadow_round(score,(22,y,746,y+row_h),20,(255,252,234,255),blur=10,offset=(0,6),shadow=(79,63,37,38))
    # avatar circle + name pill
    avcols=[(143,193,72,255),(76,167,210,255),(229,145,65,255),(71,153,137,255)]
    d.ellipse((38,y+31,82,y+75),fill=avcols[r],outline=(83,77,44,255),width=2);d.ellipse((50,y+43,58,y+51),fill=(60,55,40,255));d.ellipse((64,y+43,72,y+51),fill=(60,55,40,255));d.arc((51,y+46,70,y+65),0,180,fill=(60,55,40,255),width=2)
    tag=(78,y+35,196,y+79); tagfill=(128,186,69,255) if r==0 else (164,108,49,255);shadow_round(score,tag,13,tagfill,blur=4,offset=(0,3),shadow=(62,48,28,45),outline=(104,79,38,255),ow=2)
    # 0..4,+ buttons
    x0=210; bw=77; bh=76; bgap=8
    for j,lab in enumerate(['0','1','2','3','4','+']):
        bx=x0+j*(bw+bgap);by=y+25
        shadow_round(score,(bx,by,bx+bw,by+bh),15,(255,249,226,255),blur=5,offset=(0,4),shadow=(86,62,37,42),outline=BORDER,ow=2)
        center_text(d,(bx+bw/2,by+bh/2+2),lab,F['lg'],INK)
# action row
ay=926
shadow_round(score,(24,ay,184,ay+100),24,(255,249,224,255),blur=9,offset=(0,5),shadow=(82,62,36,48),outline=BORDER,ow=2);center_text(d,(104,ay+50),'‹ 이전 홀',F['md'],INK)
shadow_round(score,(198,ay,546,ay+100),26,BLUE,blur=11,offset=(0,7),shadow=(30,79,110,78),outline=(36,115,166,255),ow=2);center_text(d,(372,ay+50),'OK  다음 홀  ›',F['lg'],(255,255,255,255),1,(30,95,130,120))
shadow_round(score,(558,ay,744,ay+100),26,ORANGE,blur=11,offset=(0,7),shadow=(119,65,25,75),outline=(186,91,24,255),ow=2);center_text(d,(651,ay+50),'홀 건너뛰기 ›',F['sm'],(255,255,255,255))
# hole ribbon blank cells
ry=1045;shadow_round(score,(22,ry,746,ry+112),24,(210,232,146,255),blur=8,offset=(0,5),shadow=(70,83,38,40))
for i in range(5):
    x=24+i*(720/5);d.rounded_rectangle((x+4,ry+5,x+140,ry+107),radius=18,fill=(255,255,255,12))
# center selected fixed 3D yellow plate
shadow_round(score,(22+2*(720/5)+5,ry+5,22+3*(720/5)-5,ry+107),18,YELLOW,blur=7,offset=(0,4),shadow=(128,92,21,70),outline=(212,155,23,255),ow=2)
# bottom nav fixed 4 items, as approved concept
ny0=1192;shadow_round(score,(16,ny0,752,1572),40,DEEP,blur=14,offset=(0,8),shadow=(23,48,32,70))
d.rounded_rectangle((20,ny0+4,748,ny0+125),radius=36,fill=(55,128,95,220))
nav=[('스코어','✎'),('코스','♟'),('타겟','⌖'),('메뉴','☷')]
for i,(lab,ico) in enumerate(nav):
    cx=16+(i+.5)*(736/4);center_text(d,(cx,ny0+72),ico,font(42),(255,255,255,255));center_text(d,(cx,ny0+298),lab,font(48),(255,255,255,255),1,(8,64,42,150))
score.save(ROOT/'score_pixel_master_v1148.webp','WEBP',lossless=True,method=6)
# selected score button sprite
sel=Image.new('RGBA',(92,92),(0,0,0,0));shadow_round(sel,(6,4,86,84),16,YELLOW,blur=6,offset=(0,5),shadow=(120,83,18,90),outline=(201,143,14,255),ow=3);sel.save(ROOT/'score_selected_v1148.webp','WEBP',lossless=True,method=6)

# ---------------- YARDAGE CHROME PIXEL MASTER ----------------
yard=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(yard,'RGBA')
# top sky/header opaque
for y in range(0,186):
    t=y/186;d.line((0,y,W,y),fill=(int(41+37*t),int(170+28*t),int(220+12*t),255))
cloud(d,610,60,27);cloud(d,680,106,16)
# wood metric board fixed chrome; dynamic numbers are runtime overlay
wood_panel(yard,(28,166,740,304),24)
for x in [266,503]:d.line((x,177,x,294),fill=(63,39,22,95),width=3)
for x,lab in [(147,'FRONT'),(384,'CENTER'),(621,'BACK')]:center_text(d,(x,276),lab,F['sm'],(255,246,213,255),1,(58,38,24,120))
# side foliage and water/sand overlays in transparent course window
for i in range(13):
    y=310+i*78;ts=TREE[i%len(TREE)].resize((84,105));yard.alpha_composite(ts,(-20,y));yard.alpha_composite(TREE[(i+2)%len(TREE)].resize((84,105)),(704,y+18))
# water left
water=Image.new('RGBA',(150,610),(0,0,0,0));wd=ImageDraw.Draw(water,'RGBA');wd.rounded_rectangle((0,15,145,590),radius=65,fill=(58,164,215,245),outline=(31,120,177,255),width=5)
for yy in range(45,565,45):wd.arc((18,yy,128,yy+30),15,165,fill=(206,241,246,115),width=4)
yard.alpha_composite(water,(-55,500))
# organic sand patches
for box in [(28,470,115,555),(660,575,755,650),(32,930,120,1018)]:d.ellipse(box,fill=(250,226,158,248),outline=(211,176,105,255),width=4)
# flowers
for i in range(22):
    rnd=random.Random(700+i);x=rnd.choice([rnd.randint(30,112),rnd.randint(656,738)]);y=rnd.randint(360,1250);col=rnd.choice([(247,188,61,255),(240,113,113,255),(125,188,231,255)]);d.ellipse((x-5,y-5,x+5,y+5),fill=col)
# lower center yardage badge and target button chrome
shadow_round(yard,(28,1282,252,1406),28,(111,174,61,255),blur=10,offset=(0,7),shadow=(37,74,35,70),outline=(71,128,44,255),ow=3);center_text(d,(140,1381),'CENTER',F['sm'],(255,255,243,255))
shadow_round(yard,(538,1314,738,1396),30,(255,249,222,255),blur=9,offset=(0,5),shadow=(75,61,36,55),outline=(216,190,143,255),ow=2);center_text(d,(638,1355),'⌖  타겟',F['md'],INK)
# bottom nav 4 items opaque
ny=1412;shadow_round(yard,(14,ny,754,1590),38,DEEP,blur=14,offset=(0,7),shadow=(23,48,32,70));d.rounded_rectangle((18,ny+4,750,ny+70),radius=34,fill=(53,126,93,225))
for i,(lab,ico) in enumerate(nav):
    cx=14+(i+.5)*(740/4);center_text(d,(cx,ny+50),ico,font(36),(255,255,255,255));center_text(d,(cx,ny+135),lab,font(40),(255,255,255,255),1,(8,64,42,150))
yard.save(ROOT/'yardage_chrome_v1148.webp','WEBP',lossless=True,method=6)

# -----------------------------------------------------------------------------
# Runtime patch
# -----------------------------------------------------------------------------
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

def bounds(src,signature):
    a=src.find(signature)
    if a<0:raise SystemExit('missing method: '+signature)
    brace=src.find('{',a);depth=0
    for i in range(brace,len(src)):
        if src[i]=='{':depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0:return a,i+1
    raise SystemExit('unclosed method '+signature)

def replace_method(src,signature,replacement):
    a,b=bounds(src,signature);return src[:a]+replacement+src[b:]

# marker
if 'V1.14.8 · PIXEL MASTER' not in s:
    s=s.replace('V1.14.6 · ILLUSTRATED MASTER','V1.14.6 · ILLUSTRATED MASTER / V1.14.8 · PIXEL MASTER',1)

# fields + helpers near existing score hit arrays
anchor='        private final RectF[] scoreHoleV1139=new RectF[5];'
if anchor in s and 'pmNavV1148' not in s:
    s=s.replace(anchor,anchor+'\n        private final RectF[] pmNavV1148={new RectF(),new RectF(),new RectF(),new RectF()};\n        private final RectF scoreSkipV1148=new RectF();\n        private final java.util.HashMap<String,android.graphics.Bitmap> pmCacheV1148=new java.util.HashMap<>();',1)

helper_anchor='        private boolean coverHudV1138(){'
pos=s.find(helper_anchor)
if pos<0:raise SystemExit('pixel master helper anchor missing')
helpers=r'''        private android.graphics.Bitmap pmV1148(String n){
            android.graphics.Bitmap b=pmCacheV1148.get(n);if(b!=null)return b;int id=getResources().getIdentifier(n,"drawable",ctx.getPackageName());if(id==0)return null;b=android.graphics.BitmapFactory.decodeResource(getResources(),id);if(b!=null)pmCacheV1148.put(n,b);return b;
        }
        private void drawPmFullV1148(Canvas c,String n){android.graphics.Bitmap b=pmV1148(n);if(b!=null)c.drawBitmap(b,null,new RectF(0,0,getWidth(),getHeight()),new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG));}
        private void setPmNavV1148(float w,float h){float top=h*.8825f;for(int i=0;i<4;i++){float l=w*(.018f+i*.241f),r=w*(.018f+(i+1)*.241f);pmNavV1148[i].set(l,top,r,h*.995f);}}
        private void drawYardageChromeV1148(Canvas c){
            float w=getWidth(),h=getHeight();drawPmFullV1148(c,"yardage_chrome_v1148");setPmNavV1148(w,h);
            int par=currentPar();GeoRef g=getRef("g",hole);Distances ds=distances(g);int f=ds.front,ce=ds.center,ba=ds.back;if(previewMode){f=148;ce=155;ba=163;}
            textFit(c,ko[selected],w*.055f,h*.071f,w*.69f,22.5f,Color.WHITE,true);textFit(c,variants[selected][variant],w*.055f,h*.105f,w*.69f,12.5f,Color.rgb(242,252,240),true);
            text(c,"H"+hole+"  /  PAR "+par,w*.055f,h*.145f,14.5f,Color.WHITE,true);
            int[] vv={f,ce,ba};float[] xx={.191f,.500f,.809f};int[] cc={Color.rgb(66,184,237),Color.WHITE,Color.rgb(255,124,91)};for(int i=0;i<3;i++)text(c,vv[i]<0?"--":vv[i]+"m",w*xx[i],h*.154f,31.0f,cc[i],true,Paint.Align.CENTER);
            text(c,(ce<0?"--":ce)+"m",w*.182f,h*.847f,33.0f,Color.WHITE,true,Paint.Align.CENTER);
            mapLaunch.set(w*.700f,h*.806f,w*.965f,h*.874f);
        }

'''
s=s[:pos]+helpers+s[pos:]

# Score screen is now a static Pixel Master texture; only dynamic fields are redrawn.
score_method=r'''        private void scoreInput(Canvas c){
            float w=getWidth(),h=getHeight();c.drawColor(Color.rgb(251,248,226));drawPmFullV1148(c,"score_pixel_master_v1148");setPmNavV1148(w,h);
            int par=currentPar(),n=previewMode?4:playerCount();if(player>=n)player=0;int totalM=verifiedMetersV190();if(totalM<=0)totalM=(int)Math.round(currentYards()*.9144);
            textFit(c,ko[selected]+"  "+variants[selected][variant],w*.052f,h*.143f,w*.665f,15.5f,Color.rgb(34,91,58),true);
            text(c,""+hole,w*.105f,h*.193f,42.0f,Color.rgb(53,66,42),true,Paint.Align.CENTER);text(c,"PAR "+par,w*.185f,h*.194f,17.0f,Color.rgb(54,58,40),true);
            text(c,totalM+"m",w*.828f,h*.188f,34.0f,Color.WHITE,true,Paint.Align.CENTER);
            String[] demo={"나","김프로","이프로","박프로"};float rowTop=h*.2213f,rowH=h*.07875f,gap=h*.0075f;float x0=w*.2734f,bw=w*.1003f,bgap=w*.0110f;
            for(int i=0;i<4;i++)for(int j=0;j<6;j++)scoreQuickV1139[i][j].setEmpty();
            for(int pl=0;pl<n;pl++){
                float y=rowTop+pl*(rowH+gap);String nm=previewMode?demo[pl]:playerName(pl);textFit(c,nm,w*.105f,y+rowH*.57f,w*.252f,16.0f,Color.WHITE,true);
                int cur=getStroke(pl,hole,par);
                for(int j=0;j<6;j++){
                    float l=x0+j*(bw+bgap),t=y+h*.0156f,r=l+bw,b=t+h*.0475f;scoreQuickV1139[pl][j].set(l,t,r,b);boolean a=(j<5&&cur==j)||(j==5&&cur>4);
                    if(a){android.graphics.Bitmap sb=pmV1148("score_selected_v1148");if(sb!=null)c.drawBitmap(sb,null,new RectF(l-3,t-3,r+3,b+5),new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG));text(c,j<5?(""+j):"+",(l+r)/2,(t+b)/2+8,23.0f,Color.rgb(72,53,31),true,Paint.Align.CENTER);}
                }
            }
            scorePrevV1140.set(w*.031f,h*.579f,w*.240f,h*.641f);scoreNextV1140.set(w*.258f,h*.579f,w*.711f,h*.641f);scoreSkipV1148.set(w*.727f,h*.579f,w*.969f,h*.641f);
            float ry=h*.654f,seg=w*.1875f;for(int k=0;k<5;k++){int hh=Math.max(1,Math.min(18,hole+k-2));float l=w*.029f+k*seg;scoreHoleV1139[k].set(l,ry,l+seg,h*.724f);boolean a=hh==hole;text(c,""+hh,l+seg/2,ry+h*.025f,a?22.0f:19.0f,a?Color.rgb(73,55,31):Color.rgb(38,92,46),true,Paint.Align.CENTER);text(c,"PAR"+parForHole(hh),l+seg/2,ry+h*.060f,11.5f,Color.rgb(64,85,46),true,Paint.Align.CENTER);}
        }'''
s=replace_method(s,'        private void scoreInput(Canvas c)',score_method)

# Replace runtime vector nav. For play screen this draws approved chrome on top of the
# existing GPS/course rendering, preserving validated marker/corridor logic underneath.
nav_method=r'''        private void drawStorybookBottomNavV1140(Canvas c){if(screen==1)drawYardageChromeV1148(c);}'''
s=replace_method(s,'        private void drawStorybookBottomNavV1140(Canvas c)',nav_method)

# Intercept only the new Pixel-Master nav/skip zones; all old GPS/score touch logic remains.
a,b=bounds(s,'        @Override public boolean onTouchEvent(MotionEvent e)');chunk=s[a:b]
needle='float x=e.getX(),y=e.getY();'
if needle in chunk and 'pmNavV1148[0].contains' not in chunk:
    inject=needle+r'''if(screen==1){if(pmNavV1148[0].contains(x,y)){screen=2;invalidate();return true;}if(pmNavV1148[1].contains(x,y)){invalidate();return true;}if(pmNavV1148[2].contains(x,y)){showToast("코스를 터치해 타겟을 지정하세요");invalidate();return true;}if(pmNavV1148[3].contains(x,y)){screen=0;saveState();invalidate();return true;}}if(screen==2){if(scoreSkipV1148.contains(x,y)){if(hole<18){holeDirection=1;hole++;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;saveState();}invalidate();return true;}if(pmNavV1148[0].contains(x,y)){invalidate();return true;}if(pmNavV1148[1].contains(x,y)){screen=1;invalidate();return true;}if(pmNavV1148[2].contains(x,y)){screen=1;showToast("코스를 터치해 타겟을 지정하세요");invalidate();return true;}if(pmNavV1148[3].contains(x,y)){screen=0;saveState();invalidate();return true;}}'''
    chunk=chunk.replace(needle,inject,1);s=s[:a]+chunk+s[b:]

p.write_text(s)
print('V1.14.8 PIXEL MASTER: fixed WebP texture/sprites for SCORE + YARDAGE chrome; dynamic values only overlay')
print('Course/GPS geometry remains under transparent yardage chrome; no corridor remap performed')
