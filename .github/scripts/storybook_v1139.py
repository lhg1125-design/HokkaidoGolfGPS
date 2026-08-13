from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.13.8 · COVER HUD' not in s:
    raise SystemExit('storybook_v1139 requires V1.13.8 cover HUD base')

def replace_method(src, signature, replacement):
    start=src.find(signature)
    if start<0: raise SystemExit('missing method: '+signature)
    brace=src.find('{',start)
    depth=0; end=-1
    for i in range(brace,len(src)):
        if src[i]=='{': depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0: end=i+1; break
    if end<0: raise SystemExit('unclosed method: '+signature)
    return src[:start]+replacement+src[end:]

field_anchor='        private final RectF[] playerTabs={new RectF(),new RectF(),new RectF(),new RectF()};'
if field_anchor not in s: raise SystemExit('storybook score field anchor missing')
s=s.replace(field_anchor,field_anchor+'\n        private final RectF[][] scoreQuickV1139=new RectF[4][6];\n        private final RectF[] scoreHoleV1139=new RectF[5];',1)
ctor='            setKeepScreenOn(true);'
if ctor not in s: raise SystemExit('storybook constructor anchor missing')
s=s.replace(ctor,ctor+'\n            for(int i=0;i<4;i++)for(int j=0;j<6;j++)scoreQuickV1139[i][j]=new RectF();\n            for(int i=0;i<5;i++)scoreHoleV1139[i]=new RectF();',1)

home=r'''        private void home(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.050f;c.drawColor(Color.rgb(252,249,226));
            RectF hero=new RectF(0,0,w,h*.255f);c.save();c.clipRect(hero);c.drawBitmap(v12Home,null,new RectF(0,0,w,h),p);c.restore();p.setColor(Color.argb(34,30,88,45));c.drawRect(0,hero.bottom-4,w,hero.bottom+5,p);
            RectF titleBoard=new RectF(m,h*.035f,w-m,h*.122f);gradient(c,titleBoard,Color.rgb(76,126,67),Color.rgb(36,101,61),26);sheen(c,titleBoard,26);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3.2f);p.setColor(Color.argb(170,26,74,43));c.drawRoundRect(titleBoard,26,26,p);p.setStyle(Paint.Style.FILL);
            text(c,"HOKKAIDO GOLF GPS",titleBoard.centerX(),h*.078f,19.0f,Color.WHITE,true,Paint.Align.CENTER);text(c,"GPS · 코스맵 · 스코어",titleBoard.centerX(),h*.104f,8.2f,Color.rgb(235,248,224),true,Paint.Align.CENTER);
            mascot(c,w*.86f,h*.205f,24,true);speech(c,w*.49f,h*.178f,"오늘도 즐겁게!",DEEP);text(c,"오늘 어디서 칠까요?",m,h*.286f,17.2f,DEEP,true);text(c,"실제 홀 데이터는 그대로 · 그림체만 더 부드럽게",m,h*.312f,7.6f,Color.rgb(101,112,82),true);
            float top=h*.329f,ch=h*.057f,gap=h*.008f;int[] dots={Color.rgb(96,181,91),Color.rgb(170,106,198),Color.rgb(67,158,104),CORAL,SKY};String[] region={"JP 01","JP 02","JP 03","KR TEST","KR OFFICIAL"};
            for(int i=0;i<5;i++){float y=top+i*(ch+gap);cards[i].set(m,y,w-m,y+ch);drawWoodCardV1130(c,cards[i],selected==i,dots[i]);p.setColor(dots[i]);c.drawCircle(cards[i].left+23,cards[i].centerY(),8.5f,p);text(c,region[i],cards[i].left+40,y+ch*.28f,6.2f,Color.rgb(120,76,37),true);textFit(c,ko[i],cards[i].left+40,y+ch*.62f,cards[i].right-w*.24f,13.4f,Color.rgb(61,45,29),true);String vv=variants[i][0]+((i==0||i==1||i==4)?(" / "+variants[i][1]):"");textFit(c,vv,cards[i].left+40,y+ch*.82f,cards[i].right-12,6.2f,Color.rgb(105,79,51),true);if(location!=null){int dm=(int)Math.round(distanceToCourse(location,i));String ds=dm<10000?dm+"m":"약 "+Math.round(dm/1000f)+"km";pill(c,new RectF(cards[i].right-100,y+9,cards[i].right-10,y+33),Color.argb(230,255,248,218),ds,selected==i?DEEP:Color.rgb(118,100,75),5.9f);}}
            float vy=h*.665f;text(c,"코스 선택",m,vy-8,8.0f,DEEP,true);varA.set(m,vy,w*.485f,vy+h*.040f);varB.set(w*.515f,vy,w-m,vy+h*.040f);
            if(selected>=0){goldButton(c,varA,variant==0?DEEP:Color.rgb(251,239,204),variants[selected][0],variant==0?Color.WHITE:Color.rgb(76,54,33),13.0f);goldButton(c,varB,variant==1?DEEP:Color.rgb(251,239,204),variants[selected][1],variant==1?Color.WHITE:Color.rgb(76,54,33),13.0f);}else{goldButton(c,varA,Color.rgb(242,236,214),"A COURSE",Color.GRAY,11.5f);goldButton(c,varB,Color.rgb(242,236,214),"B COURSE",Color.GRAY,11.5f);}
            start.set(m,h*.727f,w-m,h*.795f);gradient(c,start,selected>=0?Color.rgb(238,133,38):Color.rgb(205,202,185),selected>=0?Color.rgb(255,181,65):Color.rgb(188,185,170),30);sheen(c,start,30);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3f);p.setColor(selected>=0?Color.rgb(160,85,24):Color.rgb(158,155,144));c.drawRoundRect(start,30,30,p);p.setStyle(Paint.Style.FILL);goldText(c,selected>=0?"라운드 시작  >":"골프장을 먼저 선택",start.centerX(),start.centerY(),18.0f,selected>=0?Color.WHITE:Color.DKGRAY);
            RectF leaf=new RectF(m,h*.818f,w-m,h*.866f);box(c,leaf,Color.rgb(235,245,209),22);drawStoryLeafV1139(c,leaf.left+20,leaf.centerY(),8);text(c,"오프라인 코스 · GPS 실시간 · 4인 스코어",leaf.left+38,leaf.centerY()+4,7.7f,DEEP,true);text(c,"24~26 AUG · HOKKAIDO TRIP",w/2,h*.908f,8.8f,DEEP,true,Paint.Align.CENTER);text(c,"동화처럼 보기 쉽고, 현장에서는 한 손으로 빠르게",w/2,h*.938f,7.1f,Color.rgb(100,111,80),true,Paint.Align.CENTER);
        }'''
s=replace_method(s,'        private void home(Canvas c)',home)

score=r'''        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;c.drawColor(Color.rgb(252,249,226));int par=currentPar();int totalM=verifiedMetersV190();if(totalM<=0)totalM=(int)Math.round(currentYards()*.9144);
            RectF sky=new RectF(0,0,w,h*.168f);gradient(c,sky,Color.rgb(68,181,231),Color.rgb(121,205,230),0);drawStoryCloudV1139(c,w*.72f,h*.045f,18);drawStoryCloudV1139(c,w*.84f,h*.078f,11);text(c,"스코어 입력",m,h*.052f,20.5f,Color.WHITE,true);textFit(c,ko[selected]+" · "+variants[selected][variant],m,h*.083f,w*.68f,9.2f,Color.rgb(239,251,239),true);pill(c,new RectF(w*.72f,h*.026f,w*.95f,h*.062f),Color.rgb(255,246,215),"한 번 탭 입력",Color.rgb(117,78,34),7.1f);
            RectF info=new RectF(m,h*.107f,w-m,h*.207f);softShadow(c,info,22);box(c,info,Color.rgb(255,253,235),22);RectF scene=new RectF(info.left+8,info.top+7,w*.61f,info.bottom-7);c.save();c.clipRect(scene);c.drawBitmap(v12Course,null,scene,p);c.restore();text(c,"H"+hole,scene.left+15,scene.top+31,27,Color.WHITE,true);text(c,"PAR "+par,scene.left+17,scene.top+53,8.2f,Color.WHITE,true);RectF yard=new RectF(w*.63f,info.top+9,info.right-8,info.bottom-9);gradient(c,yard,Color.rgb(156,105,53),Color.rgb(99,67,35),18);drawWoodGrainV1139(c,yard);text(c,"YARDAGE",yard.centerX(),yard.top+20,7.0f,Color.rgb(255,239,195),true,Paint.Align.CENTER);text(c,totalM+"m",yard.centerX(),yard.centerY()+15,24.5f,Color.WHITE,true,Paint.Align.CENTER);
            text(c,"타수를 바로 선택하세요",m,h*.239f,10.0f,DEEP,true);text(c,"현재 PAR 기준 ±2를 한 화면에 표시",w-m,h*.239f,6.6f,Color.rgb(113,114,91),true,Paint.Align.RIGHT);
            float rowTop=h*.264f,rowH=h*.092f,rowGap=h*.010f;int[] avatar={Color.rgb(119,187,91),Color.rgb(80,174,211),Color.rgb(239,147,80),Color.rgb(230,193,70)};
            for(int pl=0;pl<4;pl++){float y=rowTop+pl*(rowH+rowGap);RectF row=new RectF(m,y,w-m,y+rowH);softShadow(c,row,22);box(c,row,Color.rgb(255,253,239),22);p.setColor(avatar[pl]);c.drawCircle(row.left+24,row.centerY(),17,p);p.setColor(Color.rgb(255,244,214));c.drawCircle(row.left+24,row.centerY()-2,11,p);text(c,"P"+(pl+1),row.left+24,row.centerY()+4,8.2f,Color.rgb(73,57,40),true,Paint.Align.CENTER);if(player==pl)pill(c,new RectF(row.left+45,row.top+10,row.left+88,row.top+34),Color.rgb(224,241,189),"나",DEEP,7.0f);else text(c,"PLAYER "+(pl+1),row.left+46,row.top+27,7.2f,Color.rgb(103,78,49),true);int cur=getStroke(pl,hole,par);float x0=w*.32f,rr=rowH*.28f,g=(w*.95f-x0)/6f;for(int j=0;j<6;j++){float cx=x0+g*(j+.5f),cy=row.centerY();scoreQuickV1139[pl][j].set(cx-g*.42f,cy-rr,cx+g*.42f,cy+rr);int val=j<5?Math.max(1,par-2+j):cur+1;boolean active=j<5&&cur==val;int bg=active?Color.rgb(255,208,64):Color.rgb(255,249,227);int fg=active?Color.rgb(83,60,29):Color.rgb(78,64,47);box(c,scoreQuickV1139[pl][j],bg,12);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(active?2.8f:1.4f);p.setColor(active?Color.rgb(191,137,28):Color.rgb(211,191,153));c.drawRoundRect(scoreQuickV1139[pl][j],12,12,p);p.setStyle(Paint.Style.FILL);text(c,j<5?(""+val):"+",cx,cy+5,active?12.2f:11.1f,fg,true,Paint.Align.CENTER);}String rel=scoreRelationV1139(cur,par);text(c,"현재 "+cur+" · "+rel,row.left+46,row.bottom-10,6.6f,cur<par?DEEP:(cur>par?CORAL:Color.rgb(94,89,70)),true);}
            float hy=h*.697f;RectF ribbon=new RectF(m,hy,w-m,hy+h*.060f);box(c,ribbon,Color.rgb(223,239,178),22);for(int k=0;k<5;k++){int hh=Math.max(1,Math.min(18,hole+k-2));float seg=ribbon.width()/5f,l=ribbon.left+k*seg;scoreHoleV1139[k].set(l+3,ribbon.top+4,l+seg-3,ribbon.bottom-4);boolean a=hh==hole;box(c,scoreHoleV1139[k],a?Color.rgb(255,207,65):Color.argb(0,255,255,255),14);text(c,""+hh,scoreHoleV1139[k].centerX(),ribbon.top+25,a?12.2f:10.6f,a?Color.rgb(79,60,30):DEEP,true,Paint.Align.CENTER);text(c,"PAR"+parForHole(hh),scoreHoleV1139[k].centerX(),ribbon.bottom-8,5.8f,Color.rgb(80,93,57),true,Paint.Align.CENTER);}mascot(c,w*.12f,h*.805f,20,true);speech(c,w*.19f,h*.777f,"한눈에 보고, 한 번에 입력!",DEEP);nav(c);
        }'''
s=replace_method(s,'        private void score(Canvas c)',score)

needle='gradient(c,range,Color.rgb(34,126,72),Color.rgb(87,159,98),18);sheen(c,range,18);'
if needle not in s: raise SystemExit('storybook live metric board anchor missing')
s=s.replace(needle,'gradient(c,range,Color.rgb(151,103,53),Color.rgb(93,64,35),18);drawWoodGrainV1139(c,range);sheen(c,range,18);',1)

touch='            if(screen==4 && roundLogShareBtnV1136.contains(x,y)){shareRoundLogV1136();return true;}'
if touch not in s: raise SystemExit('storybook touch anchor missing')
s=s.replace(touch,touch+'\n            if(screen==2){int pa=currentPar();for(int pl=0;pl<4;pl++)for(int j=0;j<6;j++){if(scoreQuickV1139[pl][j].contains(x,y)){int nv=j<5?Math.max(1,pa-2+j):getStroke(pl,hole,pa)+1;setStroke(pl,hole,nv);player=pl;lastTap=SystemClock.uptimeMillis();lastDelta=1;saveState();showToast("P"+(pl+1)+" · H"+hole+" · "+nv+"타 ("+scoreRelationV1139(nv,pa)+")");invalidate();return true;}}for(int k=0;k<5;k++)if(scoreHoleV1139[k].contains(x,y)){int nh=Math.max(1,Math.min(18,hole+k-2));if(nh!=hole){holeDirection=nh>hole?1:-1;hole=nh;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;saveState();}invalidate();return true;}}',1)

anchor='        private boolean coverHudV1138(){'
idx=s.find(anchor)
if idx<0: raise SystemExit('storybook helper anchor missing')
helpers=r'''        private void drawWoodGrainV1139(Canvas c,RectF r){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.3f);p.setColor(Color.argb(42,255,228,171));for(int i=1;i<=4;i++){float yy=r.top+r.height()*i/5f;c.drawLine(r.left+10,yy,r.right-10,yy,p);}p.setStrokeWidth(2.2f);p.setColor(Color.argb(90,76,48,25));c.drawRoundRect(new RectF(r.left+2,r.top+2,r.right-2,r.bottom-2),Math.min(18,r.height()/3),Math.min(18,r.height()/3),p);p.setStyle(Paint.Style.FILL);}
        private void drawStoryLeafV1139(Canvas c,float x,float y,float r){p.setColor(Color.rgb(92,171,70));c.save();c.rotate(-28,x,y);c.drawOval(new RectF(x-r,y-r*.55f,x+r,y+r*.55f),p);c.restore();p.setStrokeWidth(1.8f);p.setColor(Color.rgb(53,126,57));c.drawLine(x-r*.65f,y+r*.42f,x+r*.7f,y-r*.45f,p);}
        private void drawStoryCloudV1139(Canvas c,float x,float y,float r){p.setColor(Color.argb(218,255,255,250));c.drawCircle(x-r*.5f,y,r*.48f,p);c.drawCircle(x,y-r*.17f,r*.62f,p);c.drawCircle(x+r*.58f,y,r*.43f,p);c.drawRoundRect(new RectF(x-r*.92f,y,x+r*.98f,y+r*.42f),r*.24f,r*.24f,p);}
        private String scoreRelationV1139(int stroke,int par){int d=stroke-par;if(d==0)return "EVEN";if(d==-1)return "BIRDIE";if(d==-2)return "EAGLE";if(d==1)return "+1";if(d==2)return "+2";return d>0?("+"+d):(""+d);}
'''
s=s[:idx]+helpers+s[idx:]
p.write_text(s)
print('storybook_v1139 applied')
