from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.14.9 · COURSE PIXEL' not in s:
    raise SystemExit('V1.15.0 requires V1.14.9 course pixel base')


def bounds(src,signature):
    a=src.find(signature)
    if a<0: raise SystemExit('missing method: '+signature)
    br=src.find('{',a);dep=0
    for i in range(br,len(src)):
        if src[i]=='{': dep+=1
        elif src[i]=='}':
            dep-=1
            if dep==0:return a,i+1
    raise SystemExit('unclosed method: '+signature)


def replace_method(src,signature,repl):
    a,b=bounds(src,signature);return src[:a]+repl+src[b:]

# -----------------------------------------------------------------------------
# V1.15.0 STORYBOOK RECOVERY
# 1) Remove the full-screen Pixel-Master overlay that duplicated/covered live UI.
# 2) Draw only a responsive lower chrome over the validated live hole canvas.
# 3) Rebuild score entry as relative-to-par: -1,0,1,2,3,4,5.
#    Stored score remains the actual stroke count (PAR + delta).
# 4) Use vector icons only; avoid unsupported symbol glyphs that rendered as boxes.
# -----------------------------------------------------------------------------

if 'V1.15.0 · STORYBOOK RECOVERY' not in s:
    s=s.replace('V1.14.9 · COURSE PIXEL','V1.14.9 · COURSE PIXEL / V1.15.0 · STORYBOOK RECOVERY',1)

field='        private final RectF[] scoreHoleV1139=new RectF[5];'
if field not in s: raise SystemExit('V1.15.0 score field anchor missing')
if 'scoreDeltaV1150' not in s:
    s=s.replace(field,field+'\n        private final RectF[][] scoreDeltaV1150=new RectF[4][7];',1)

# Compact 4-item nav hit zones matching the visible footer, not the old 25%-high region.
setnav=r'''        private void setPmNavV1148(float w,float h){
            float top=h*.918f,bottom=h*.992f;float left=w*.025f,right=w*.975f,seg=(right-left)/4f;
            for(int i=0;i<4;i++)pmNavV1148[i].set(left+i*seg,top,left+(i+1)*seg,bottom);
        }'''
s=replace_method(s,'        private void setPmNavV1148(float w,float h)',setnav)

# Disable the V1.14.8 full-screen yardage chrome. The validated live course renderer
# stays visible; only the clean lower storybook footer/nav is added.
yard_chrome=r'''        private void drawYardageChromeV1148(Canvas c){
            drawYardageFooterV1150(c);
        }'''
s=replace_method(s,'        private void drawYardageChromeV1148(Canvas c)',yard_chrome)

helper_anchor='        private boolean coverHudV1138(){'
pos=s.find(helper_anchor)
if pos<0: raise SystemExit('V1.15.0 helper anchor missing')
helpers=r'''        private String scoreDeltaLabelV1150(int d){
            if(d==-1)return "버디";if(d==0)return "파";if(d==1)return "보기";if(d==2)return "더블";if(d==3)return "트리플";return d+"오버";
        }
        private int scoreDeltaColorV1150(int d){
            if(d<0)return Color.rgb(43,133,92);if(d==0)return Color.rgb(54,112,63);if(d<=2)return Color.rgb(187,126,36);return Color.rgb(188,87,53);
        }
        private void drawBackArrowV1150(Canvas c,float x,float y,float s,int col){
            p.setStyle(Paint.Style.STROKE);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeWidth(Math.max(3f,s*.18f));p.setColor(col);c.drawLine(x+s*.38f,y-s*.55f,x-s*.20f,y,p);c.drawLine(x-s*.20f,y,x+s*.38f,y+s*.55f,p);p.setStrokeCap(Paint.Cap.BUTT);p.setStyle(Paint.Style.FILL);
        }
        private void drawTargetIconV1150(Canvas c,float x,float y,float s,int col){
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(Math.max(2.5f,s*.12f));p.setColor(col);c.drawCircle(x,y,s*.43f,p);c.drawCircle(x,y,s*.15f,p);c.drawLine(x-s*.62f,y,x-s*.34f,y,p);c.drawLine(x+s*.34f,y,x+s*.62f,y,p);c.drawLine(x,y-s*.62f,x,y-s*.34f,p);c.drawLine(x,y+s*.34f,x,y+s*.62f,p);p.setStyle(Paint.Style.FILL);
        }
        private void drawNavIconV1150(Canvas c,int idx,float x,float y,float s,int col){
            p.setColor(col);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(Math.max(2.5f,s*.11f));p.setStrokeCap(Paint.Cap.ROUND);
            if(idx==0){c.drawRoundRect(new RectF(x-s*.42f,y-s*.48f,x+s*.42f,y+s*.40f),s*.10f,s*.10f,p);for(int k=-1;k<=1;k++)c.drawLine(x-s*.22f,y+k*s*.20f,x+s*.23f,y+k*s*.20f,p);}
            else if(idx==1){c.drawCircle(x-s*.20f,y-s*.18f,s*.19f,p);c.drawCircle(x+s*.24f,y-s*.18f,s*.19f,p);c.drawArc(new RectF(x-s*.55f,y-s*.05f,x+s*.08f,y+s*.55f),200,140,false,p);c.drawArc(new RectF(x-s*.05f,y-s*.05f,x+s*.58f,y+s*.55f),200,140,false,p);}
            else if(idx==2){drawTargetIconV1150(c,x,y,s,col);}
            else{for(int k=-1;k<=1;k++)c.drawLine(x-s*.45f,y+k*s*.25f,x+s*.45f,y+k*s*.25f,p);}
            p.setStrokeCap(Paint.Cap.BUTT);p.setStyle(Paint.Style.FILL);
        }
        private void drawCleanNavV1150(Canvas c){
            float w=getWidth(),h=getHeight();setPmNavV1148(w,h);RectF bar=new RectF(w*.020f,h*.914f,w*.980f,h*.992f);softShadow(c,bar,bar.height()*.28f);gradient(c,bar,Color.rgb(27,119,77),Color.rgb(9,78,52),bar.height()*.30f);sheen(c,bar,bar.height()*.30f);
            String[] labs={"스코어","코스","타겟","메뉴"};for(int i=0;i<4;i++){RectF r=pmNavV1148[i];float cx=r.centerX(),iy=bar.top+bar.height()*.32f;drawNavIconV1150(c,i,cx,iy,bar.height()*.24f,Color.rgb(255,252,230));text(c,labs[i],cx,bar.bottom-bar.height()*.13f,9.4f,Color.rgb(255,252,230),true,Paint.Align.CENTER);}
        }
        private void drawYardageFooterV1150(Canvas c){
            float w=getWidth(),h=getHeight();
            // Cover legacy calibration furniture that used to collide with the nav.
            p.setColor(Color.rgb(252,249,226));c.drawRect(0,h*.842f,w,h,p);
            greenSave.set(-1,-1,-1,-1);teeSave.set(-1,-1,-1,-1);
            GeoRef g=greenCenterRef(hole);int center=-1;if(previewMode)center=155;else if(g!=null&&gpsUsable())center=Math.round(distance(location,g.lat,g.lon));if(center<0){int v=verifiedMetersV190();center=v>0?v:(int)Math.round(currentYards()*.9144);}
            RectF badge=new RectF(w*.035f,h*.852f,w*.335f,h*.907f);softShadow(c,badge,18);gradient(c,badge,Color.rgb(112,177,65),Color.rgb(76,145,51),18);sheen(c,badge,18);text(c,center+"m",badge.centerX(),badge.top+badge.height()*.48f,24.0f,Color.WHITE,true,Paint.Align.CENTER);text(c,"CENTER",badge.centerX(),badge.bottom-8,8.2f,Color.WHITE,true,Paint.Align.CENTER);
            mapLaunch.set(w*.705f,h*.857f,w*.965f,h*.907f);softShadow(c,mapLaunch,18);box(c,mapLaunch,Color.rgb(255,248,221),18);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.5f);p.setColor(Color.rgb(208,177,124));c.drawRoundRect(mapLaunch,18,18,p);p.setStyle(Paint.Style.FILL);drawTargetIconV1150(c,mapLaunch.left+27,mapLaunch.centerY(),13,Color.rgb(75,61,38));text(c,"타겟",mapLaunch.left+50,mapLaunch.centerY()+5,11.0f,Color.rgb(75,61,38),true);
            drawCleanNavV1150(c);
        }

'''
s=s[:pos]+helpers+s[pos:]

# The common storybook footer now draws only the responsive lower UI.
nav=r'''        private void drawStorybookBottomNavV1140(Canvas c){
            if(screen==1)drawYardageFooterV1150(c);else drawCleanNavV1150(c);
        }'''
s=replace_method(s,'        private void drawStorybookBottomNavV1140(Canvas c)',nav)

# Rebuild score input from responsive Canvas primitives. No fixed full-screen bitmap.
score=r'''        private void scoreInput(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.030f;int par=currentPar();int n=previewMode?4:playerCount();if(n<1)n=1;if(n>4)n=4;if(player>=n)player=0;c.drawColor(Color.rgb(252,249,228));
            for(int pl=0;pl<4;pl++){for(int j=0;j<6;j++)scoreQuickV1139[pl][j].setEmpty();for(int j=0;j<7;j++){if(scoreDeltaV1150[pl][j]==null)scoreDeltaV1150[pl][j]=new RectF();scoreDeltaV1150[pl][j].setEmpty();}}

            RectF sky=new RectF(0,0,w,h*.122f);gradient(c,sky,Color.rgb(43,169,220),Color.rgb(89,195,226),0);drawStoryCloudV1139(c,w*.78f,h*.033f,18);drawStoryCloudV1139(c,w*.88f,h*.066f,11);drawBackArrowV1150(c,w*.055f,h*.061f,17,Color.WHITE);text(c,"스코어 입력",w/2,h*.073f,24.0f,Color.WHITE,true,Paint.Align.CENTER);playerNamesBtn.set(w*.775f,h*.025f,w*.965f,h*.073f);pill(c,playerNamesBtn,Color.rgb(255,247,216),"라운드 정보",Color.rgb(82,63,36),8.3f);

            int totalM=verifiedMetersV190();if(totalM<=0)totalM=(int)Math.round(currentYards()*.9144);
            RectF info=new RectF(m,h*.135f,w-m,h*.255f);softShadow(c,info,20);box(c,info,Color.rgb(255,253,236),20);
            RectF scene=new RectF(info.left+7,info.top+7,w*.690f,info.bottom-7);c.save();c.clipRect(scene);c.drawBitmap(v12Course,null,scene,p);c.restore();p.setColor(Color.argb(30,255,255,255));c.drawRoundRect(scene,16,16,p);textFit(c,ko[selected]+"  "+variants[selected][variant],scene.left+17,scene.top+24,scene.right-10,11.0f,DEEP,true);text(c,""+hole,scene.left+48,scene.centerY()+27,35.0f,Color.rgb(49,65,40),true,Paint.Align.CENTER);text(c,"PAR "+par,scene.left+96,scene.centerY()+17,13.0f,Color.rgb(49,60,40),true);
            RectF yard=new RectF(w*.704f,info.top+7,info.right-7,info.bottom-7);gradient(c,yard,Color.rgb(151,98,48),Color.rgb(91,58,31),17);drawWoodGrainV1139(c,yard);sheen(c,yard,17);text(c,"YARDAGE",yard.centerX(),yard.top+24,8.4f,Color.rgb(255,239,195),true,Paint.Align.CENTER);text(c,totalM+"m",yard.centerX(),yard.centerY()+20,27.0f,Color.WHITE,true,Paint.Align.CENTER);

            // Relative-to-par legend: exactly the seven values requested.
            float lx=w*.245f,lw=w*.720f/7f;String[] nums={"-1","0","1","2","3","4","5"};String[] rels={"버디","파","보기","더블","트리플","4오버","5오버"};text(c,"PAR 기준",m,h*.286f,9.0f,DEEP,true);
            for(int j=0;j<7;j++){float cx=lx+lw*(j+.5f);text(c,nums[j],cx,h*.280f,11.2f,Color.rgb(73,57,38),true,Paint.Align.CENTER);text(c,rels[j],cx,h*.303f,6.8f,scoreDeltaColorV1150(j-1),true,Paint.Align.CENTER);}

            String[] demo={"나","김프로","이프로","박프로"};int[] av={Color.rgb(132,188,73),Color.rgb(72,160,204),Color.rgb(225,145,65),Color.rgb(73,151,135)};
            float top=h*.317f,bottom=h*.650f,gap=h*.007f,rowH=(bottom-top-gap*(n-1))/n;
            for(int pl=0;pl<n;pl++){
                float y=top+pl*(rowH+gap);RectF row=new RectF(m,y,w-m,y+rowH);softShadow(c,row,15);box(c,row,Color.rgb(255,252,234),15);drawPlayerAvatarV1140(c,row.left+25,row.centerY(),16,av[pl],pl);
                String nm=previewMode?demo[pl]:playerName(pl);RectF nr=new RectF(row.left+45,row.top+rowH*.17f,w*.225f,row.top+rowH*.55f);gradient(c,nr,pl==0?Color.rgb(126,180,62):Color.rgb(166,113,54),pl==0?Color.rgb(153,201,74):Color.rgb(132,86,42),10);textFit(c,nm,nr.left+5,nr.centerY()+5,nr.right-5,10.2f,Color.WHITE,true);
                int cur=getStroke(pl,hole,par),cd=cur-par;String relation=scoreDeltaLabelV1150(cd);textFit(c,relation,row.left+47,row.bottom-8,w*.225f,7.1f,scoreDeltaColorV1150(cd),true);
                float x0=w*.245f,x1=w*.965f,seg=(x1-x0)/7f,cy=row.centerY()+rowH*.025f,bh=rowH*.60f;
                for(int j=0;j<7;j++){int delta=j-1;float cx=x0+seg*(j+.5f);RectF b=scoreDeltaV1150[pl][j];b.set(cx-seg*.43f,cy-bh*.50f,cx+seg*.43f,cy+bh*.50f);boolean active=cd==delta;box(c,b,active?Color.rgb(255,208,56):Color.rgb(255,249,227),11);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(active?2.8f:1.5f);p.setColor(active?Color.rgb(187,132,24):Color.rgb(205,180,136));c.drawRoundRect(b,11,11,p);p.setStyle(Paint.Style.FILL);text(c,nums[j],cx,cy+6,13.0f,Color.rgb(71,53,32),true,Paint.Align.CENTER);}
            }

            scorePrevV1140.set(m,h*.670f,w*.250f,h*.731f);scoreNextV1140.set(w*.265f,h*.670f,w*.725f,h*.731f);scoreSkipV1148.set(w*.740f,h*.670f,w*.970f,h*.731f);
            box(c,scorePrevV1140,Color.rgb(255,248,220),18);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.5f);p.setColor(Color.rgb(202,174,124));c.drawRoundRect(scorePrevV1140,18,18,p);p.setStyle(Paint.Style.FILL);text(c,"이전 홀",scorePrevV1140.centerX(),scorePrevV1140.centerY()+5,10.5f,Color.rgb(85,66,40),true,Paint.Align.CENTER);
            gradient(c,scoreNextV1140,Color.rgb(42,135,197),Color.rgb(69,165,215),20);sheen(c,scoreNextV1140,20);text(c,"다음 홀",scoreNextV1140.centerX(),scoreNextV1140.centerY()+6,15.5f,Color.WHITE,true,Paint.Align.CENTER);
            gradient(c,scoreSkipV1148,Color.rgb(229,121,30),Color.rgb(244,142,39),20);sheen(c,scoreSkipV1148,20);text(c,"건너뛰기",scoreSkipV1148.centerX(),scoreSkipV1148.centerY()+5,10.5f,Color.WHITE,true,Paint.Align.CENTER);

            RectF ribbon=new RectF(m,h*.751f,w-m,h*.837f);box(c,ribbon,Color.rgb(210,233,151),20);for(int k=0;k<5;k++){int hh=Math.max(1,Math.min(18,hole+k-2));float sg=ribbon.width()/5f,l=ribbon.left+k*sg;scoreHoleV1139[k].set(l+3,ribbon.top+4,l+sg-3,ribbon.bottom-4);boolean a=hh==hole;box(c,scoreHoleV1139[k],a?Color.rgb(255,208,57):Color.argb(0,255,255,255),13);text(c,""+hh,scoreHoleV1139[k].centerX(),ribbon.top+31,a?16.0f:14.0f,a?Color.rgb(73,55,31):DEEP,true,Paint.Align.CENTER);text(c,"PAR"+parForHole(hh),scoreHoleV1139[k].centerX(),ribbon.bottom-10,7.8f,Color.rgb(66,88,49),true,Paint.Align.CENTER);}
            drawCleanNavV1150(c);
        }'''
s=replace_method(s,'        private void scoreInput(Canvas c)',score)

# New relative-score touch handler runs before the old 0..4/+ handler.
a,b=bounds(s,'        @Override public boolean onTouchEvent(MotionEvent e)');chunk=s[a:b]
needle='float x=e.getX(),y=e.getY();'
if needle not in chunk: raise SystemExit('V1.15.0 touch coordinate anchor missing')
if 'scoreDeltaV1150[pl][j].contains' not in chunk:
    inject=needle+r'''if(screen==2){int pa=currentPar(),pn=previewMode?4:playerCount();for(int pl=0;pl<Math.min(4,pn);pl++)for(int j=0;j<7;j++){RectF rb=scoreDeltaV1150[pl][j];if(rb!=null&&rb.contains(x,y)){int delta=j-1,nv=Math.max(1,pa+delta);setStroke(pl,hole,nv);player=pl;lastTap=SystemClock.uptimeMillis();lastDelta=delta;saveState();showToast((previewMode?("P"+(pl+1)):playerName(pl))+" · "+scoreDeltaLabelV1150(delta)+" · "+nv+"타");invalidate();return true;}}}'''
    chunk=chunk.replace(needle,inject,1);s=s[:a]+chunk+s[b:]

p.write_text(s)
print('V1.15.0 STORYBOOK RECOVERY applied: no full-screen overlay + responsive yardage footer + relative score -1..5')
