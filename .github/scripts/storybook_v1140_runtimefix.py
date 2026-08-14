from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()


def bounds(src, signature):
    start=src.find(signature)
    if start<0: raise SystemExit('missing method: '+signature)
    brace=src.find('{',start);depth=0;end=-1
    for i in range(brace,len(src)):
        if src[i]=='{':depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0:end=i+1;break
    if end<0:raise SystemExit('unclosed method: '+signature)
    return start,end


def replace_method(src,signature,replacement):
    a,b=bounds(src,signature);return src[:a]+replacement+src[b:]

# ------------------------------------------------------------------
# V1.14.1 APPROVED STORYBOOK TUNE
# - Taller sky header and larger title/course typography.
# - Wider illustrated yardage art is supplied by stylize-yardage-v1130.py.
# - Remove engineering-looking labels from the live screen.
# - Score input is rebuilt around large one-tap controls and readable footer.
# ------------------------------------------------------------------

# Give tall phones the same breathing room as the approved mockup.
s=s.replace('h*(coverHudV1138()? .105f:.070f)','h*(coverHudV1138()? .105f:.095f)')
s=s.replace('h*(coverHudV1138()? .108f:.073f)','h*(coverHudV1138()? .112f:.100f)')
s=s.replace('h*(coverHudV1138()? .185f:.126f)','h*(coverHudV1138()? .190f:.153f)')
s=s.replace('h*(coverHudV1138()? .191f:.132f)','h*(coverHudV1138()? .196f:.158f)')

metric_y=r'''        private float metricYV1138(float h){return h*(coverHudV1138()? .133f:.111f);}'''
s=replace_method(s,'        private float metricYV1138(float h)',metric_y)

title=r'''        private void drawPlayTitleV1137(Canvas c,float m,float w,float h){
            String title=ko[selected],course=variants[selected][variant];float ty=h*(coverHudV1138()? .066f:.052f);
            textFit(c,title,m,ty,w*.67f,coverHudV1138()?19.0f:18.2f,Color.WHITE,true);
            textFit(c,course,m,ty+h*(coverHudV1138()? .032f:.027f),w*.67f,10.0f,Color.rgb(239,252,239),true);
        }'''
s=replace_method(s,'        private void drawPlayTitleV1137(Canvas c,float m,float w,float h)',title)

metric=r'''        private void metric(Canvas c,String lab,String val,float x,float y){
            if(previewMode){if(lab.equals("FRONT"))val="148m";else if(lab.equals("CENTER"))val="155m";else if(lab.equals("BACK"))val="163m";}
            float lz=coverHudV1138()?11.5f:11.2f;text(c,lab,x,y,lz,Color.rgb(255,242,198),true,Paint.Align.CENTER);
            int vc=Color.WHITE;if(lab.equals("FRONT"))vc=Color.rgb(58,181,237);else if(lab.equals("BACK"))vc=Color.rgb(255,124,91);
            float z=(lab.equals("HOLE")||val.startsWith("H"))?(coverHudV1138()?27.0f:26.0f):(coverHudV1138()?25.0f:24.2f);
            text(c,val,x,y+getHeight()*(coverHudV1138()? .041f:.038f),z,vc,true,Paint.Align.CENTER);
        }'''
s=replace_method(s,'        private void metric(Canvas c,String lab,String val,float x,float y)',metric)

# Friendlier live status: keep calibration truth, remove engineering jargon.
try:
    live_chip=r'''        private String liveGeoChipV1135(){
            GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t==null)return "TEE 위치 저장";if(g==null)return "GREEN 위치 저장";return "LIVE GPS";
        }'''
    s=replace_method(s,'        private String liveGeoChipV1135()',live_chip)
except SystemExit:
    pass

s=s.replace('textFit(c,srcLabel+" · TEE → GREEN",src.left+8,src.centerY()+3,src.right-8,6.8f,GREEN,true);','textFit(c,"홀 전체 보기 · TEE → GREEN",src.left+8,src.centerY()+4,src.right-8,8.2f,GREEN,true);')
s=s.replace('text(c,"공략",strategy.left+10,h*.870f,7.0f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+48,h*.870f,strategy.right-8,6.7f,INK,true);','text(c,"공략",strategy.left+10,h*.870f,8.6f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+52,h*.870f,strategy.right-8,8.0f,INK,true);')

# Score hit targets.
field='        private final RectF[] scoreHoleV1139=new RectF[5];'
if field in s and 'scoreNextV1140' not in s:
    s=s.replace(field,field+'\n        private final RectF scorePrevV1140=new RectF(),scoreNextV1140=new RectF();',1)

score=r'''        private void scoreInput(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.030f;int par=currentPar();int n=previewMode?4:playerCount();if(player>=n)player=0;c.drawColor(Color.rgb(250,248,227));

            RectF sky=new RectF(0,0,w,h*.135f);gradient(c,sky,Color.rgb(42,166,220),Color.rgb(92,197,224),0);drawStoryCloudV1139(c,w*.76f,h*.040f,20);drawStoryCloudV1139(c,w*.88f,h*.075f,12);
            text(c,"‹",m,h*.082f,30,Color.WHITE,true);text(c,"스코어 입력",w/2,h*.082f,23.0f,Color.WHITE,true,Paint.Align.CENTER);
            playerNamesBtn.set(w*.755f,h*.031f,w*.970f,h*.080f);pill(c,playerNamesBtn,Color.rgb(255,247,215),"라운드 정보",Color.rgb(86,65,36),8.8f);

            int totalM=verifiedMetersV190();if(totalM<=0)totalM=(int)Math.round(currentYards()*.9144);
            RectF info=new RectF(m,h*.145f,w-m,h*.270f);softShadow(c,info,22);box(c,info,Color.rgb(255,253,234),22);
            RectF scene=new RectF(info.left+6,info.top+6,w*.680f,info.bottom-6);c.save();c.clipRect(scene);c.drawBitmap(v12Course,null,scene,p);c.restore();
            box(c,new RectF(scene.left+7,scene.top+7,scene.right-7,scene.bottom-7),Color.argb(32,255,255,255),18);
            textFit(c,ko[selected]+"  "+variants[selected][variant],scene.left+18,scene.top+27,scene.right-10,10.5f,DEEP,true);
            text(c,""+hole,scene.left+48,scene.centerY()+28,35,Color.rgb(52,65,40),true,Paint.Align.CENTER);text(c,"PAR "+par,scene.left+100,scene.centerY()+20,11.5f,Color.rgb(50,58,41),true);
            RectF yard=new RectF(w*.692f,info.top+8,info.right-8,info.bottom-8);gradient(c,yard,Color.rgb(163,109,55),Color.rgb(94,62,32),18);drawWoodGrainV1139(c,yard);sheen(c,yard,18);
            text(c,"YARDAGE",yard.centerX(),yard.top+25,9.0f,Color.rgb(255,239,190),true,Paint.Align.CENTER);text(c,totalM+"m",yard.centerX(),yard.centerY()+22,27.0f,Color.WHITE,true,Paint.Align.CENTER);

            String[] demo={"나","김프로","이프로","박프로"};int[] av={Color.rgb(132,188,73),Color.rgb(72,160,204),Color.rgb(225,145,65),Color.rgb(73,151,135)};
            float top=h*.288f,bottom=h*.655f,gap=h*.008f,rowH=(bottom-top-gap*(n-1))/n;for(int i=0;i<4;i++)for(int j=0;j<6;j++)scoreQuickV1139[i][j].setEmpty();
            for(int pl=0;pl<n;pl++){
                float y=top+pl*(rowH+gap);RectF row=new RectF(m,y,w-m,y+rowH);softShadow(c,row,17);box(c,row,Color.rgb(255,252,232),17);drawPlayerAvatarV1140(c,row.left+26,row.centerY(),17,av[pl],pl);
                String nm=previewMode?demo[pl]:playerName(pl);RectF nr=new RectF(row.left+47,row.centerY()-20,row.left+116,row.centerY()+20);gradient(c,nr,pl==0?Color.rgb(126,180,62):Color.rgb(166,113,54),pl==0?Color.rgb(153,201,74):Color.rgb(132,86,42),12);textFit(c,nm,nr.left+6,nr.centerY()+6,nr.right-6,10.5f,Color.WHITE,true);
                int cur=getStroke(pl,hole,par);float x0=w*.325f,g=(w*.970f-x0)/6f,rr=rowH*.33f;
                for(int j=0;j<6;j++){float cx=x0+g*(j+.5f),cy=row.centerY();scoreQuickV1139[pl][j].set(cx-g*.43f,cy-rr,cx+g*.43f,cy+rr);boolean a=(j<5&&cur==j)||(j==5&&cur>4);box(c,scoreQuickV1139[pl][j],a?Color.rgb(255,211,57):Color.rgb(255,249,225),13);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(a?3.0f:1.7f);p.setColor(a?Color.rgb(187,132,24):Color.rgb(205,180,136));c.drawRoundRect(scoreQuickV1139[pl][j],13,13,p);p.setStyle(Paint.Style.FILL);text(c,j<5?(""+j):"+",cx,cy+7,15.0f,Color.rgb(73,54,33),true,Paint.Align.CENTER);}
            }

            scorePrevV1140.set(m,h*.672f,w*.285f,h*.742f);scoreNextV1140.set(w*.305f,h*.672f,w*.970f,h*.742f);box(c,scorePrevV1140,Color.rgb(255,248,218),22);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.8f);p.setColor(Color.rgb(199,174,126));c.drawRoundRect(scorePrevV1140,22,22,p);p.setStyle(Paint.Style.FILL);text(c,"‹ 이전 홀",scorePrevV1140.centerX(),scorePrevV1140.centerY()+6,11.0f,Color.rgb(92,70,41),true,Paint.Align.CENTER);
            gradient(c,scoreNextV1140,Color.rgb(40,132,195),Color.rgb(70,166,216),24);sheen(c,scoreNextV1140,24);text(c,"OK  다음 홀  ›",scoreNextV1140.centerX(),scoreNextV1140.centerY()+7,17.0f,Color.WHITE,true,Paint.Align.CENTER);

            RectF ribbon=new RectF(m,h*.758f,w-m,h*.844f);box(c,ribbon,Color.rgb(207,232,145),22);for(int k=0;k<5;k++){int hh=Math.max(1,Math.min(18,hole+k-2));float seg=ribbon.width()/5f,l=ribbon.left+k*seg;scoreHoleV1139[k].set(l+3,ribbon.top+4,l+seg-3,ribbon.bottom-4);boolean a=hh==hole;box(c,scoreHoleV1139[k],a?Color.rgb(255,207,62):Color.argb(0,255,255,255),14);text(c,""+hh,scoreHoleV1139[k].centerX(),ribbon.top+34,a?16.0f:14.0f,a?Color.rgb(74,55,31):DEEP,true,Paint.Align.CENTER);text(c,"PAR"+parForHole(hh),scoreHoleV1139[k].centerX(),ribbon.bottom-11,8.4f,Color.rgb(72,88,48),true,Paint.Align.CENTER);}
            drawStorybookBottomNavV1140(c);
        }'''
s=replace_method(s,'        private void scoreInput(Canvas c)',score)

# Preserve large prev/next score buttons plus existing quick-score/hole-ribbon touch.
needle='            if(screen==2){int pa=currentPar();for(int pl=0;pl<4;pl)'
if needle in s:
    repl='            if(screen==2){if(scorePrevV1140.contains(x,y)){if(hole>1){holeDirection=-1;hole--;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;saveState();}invalidate();return true;}if(scoreNextV1140.contains(x,y)){if(hole<18){holeDirection=1;hole++;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;saveState();}invalidate();return true;}int pa=currentPar();for(int pl=0;pl<4;pl)'
    s=s.replace(needle,repl,1)

# Large, readable green navigation bar like the reference.
anchor='        private boolean coverHudV1138(){';pos=s.find(anchor)
if pos<0:raise SystemExit('V1.14.1 nav helper anchor missing')
nav=r'''        private void drawStorybookBottomNavV1140(Canvas c){
            float w=getWidth(),h=getHeight();setFourNav(w,h);RectF bar=new RectF(w*.025f,h*.884f,w*.975f,h*.985f);softShadow(c,bar,bar.height()*.28f);gradient(c,bar,Color.rgb(24,114,71),Color.rgb(10,82,55),bar.height()*.30f);sheen(c,bar,bar.height()*.30f);
            RectF[] rr={homeBtn,mapTab,prev,scoreTab,next};String[] tx={"홈","코스","타겟","스코어","메뉴"};for(int i=0;i<5;i++){float cx=rr[i].centerX(),cy=bar.top+bar.height()*.39f;p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3.0f);p.setColor(Color.rgb(249,247,221));float z=10.0f;if(i==0){Path q=new Path();q.moveTo(cx-z,cy-3);q.lineTo(cx,cy-z-5);q.lineTo(cx+z,cy-3);q.lineTo(cx+z,cy+8);q.lineTo(cx-z,cy+8);q.close();c.drawPath(q,p);}else if(i==1){c.drawCircle(cx,cy-3,9,p);c.drawLine(cx-8,cy+9,cx+8,cy+9,p);}else if(i==2){c.drawCircle(cx,cy-3,9,p);c.drawCircle(cx,cy-3,3,p);c.drawLine(cx-13,cy-3,cx+13,cy-3,p);c.drawLine(cx,cy-16,cx,cy+10,p);}else if(i==3){c.drawRect(cx-9,cy-15,cx+9,cy+7,p);c.drawLine(cx-5,cy-8,cx+5,cy-8,p);c.drawLine(cx-5,cy-2,cx+5,cy-2,p);}else{for(int k=-1;k<=1;k++){c.drawCircle(cx-10,cy-7+k*7,1.4f,p);c.drawLine(cx-5,cy-7+k*7,cx+10,cy-7+k*7,p);}}p.setStyle(Paint.Style.FILL);text(c,tx[i],cx,bar.bottom-10,9.4f,Color.rgb(250,248,224),true,Paint.Align.CENTER);}
        }

'''
s=s[:pos]+nav+s[pos:]

# Use storybook nav on actual play screens.
for sig in ['        private void roundJapanPremium(Canvas c)','        private void roundKorea(Canvas c)']:
    try:a,b=bounds(s,sig);chunk=s[a:b]
    except SystemExit:continue
    if 'setFourNav(w,h);drawGoldenNav(c);' in chunk:chunk=chunk.replace('setFourNav(w,h);drawGoldenNav(c);','drawStorybookBottomNavV1140(c);')
    s=s[:a]+chunk+s[b:]

p.write_text(s)
print('V1.14.1 approved storybook tune: wider art + larger typography + readable score/nav')
