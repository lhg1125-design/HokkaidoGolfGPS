from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()


def bounds(src, signature):
    start=src.find(signature)
    if start<0: raise SystemExit('missing method: '+signature)
    brace=src.find('{',start); depth=0; end=-1
    for i in range(brace,len(src)):
        if src[i]=='{': depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0: end=i+1; break
    if end<0: raise SystemExit('unclosed method: '+signature)
    return start,end


def replace_method(src, signature, replacement):
    a,b=bounds(src,signature)
    return src[:a]+replacement+src[b:]

# Separate hit targets for the large score prev/next buttons.
field='        private final RectF[] scoreHoleV1139=new RectF[5];'
if field in s and 'scoreNextV1140' not in s:
    s=s.replace(field,field+'\n        private final RectF scorePrevV1140=new RectF(),scoreNextV1140=new RectF();',1)

# ACTUAL score route used by onDraw: same approved storybook visual language.
score=r'''        private void scoreInput(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.035f;int par=currentPar();int n=previewMode?4:playerCount();if(player>=n)player=0;
            c.drawColor(Color.rgb(249,247,224));

            RectF sky=new RectF(0,0,w,h*.118f);gradient(c,sky,Color.rgb(43,167,218),Color.rgb(82,188,222),0);
            drawStoryCloudV1139(c,w*.75f,h*.037f,17);drawStoryCloudV1139(c,w*.87f,h*.064f,10);
            text(c,"‹",m,h*.071f,27,Color.WHITE,true);text(c,"스코어 입력",w/2,h*.071f,20.5f,Color.WHITE,true,Paint.Align.CENTER);
            playerNamesBtn.set(w*.755f,h*.026f,w*.965f,h*.071f);pill(c,playerNamesBtn,Color.rgb(255,247,217),"라운드 정보",Color.rgb(83,66,38),7.2f);

            int totalM=verifiedMetersV190();if(totalM<=0)totalM=(int)Math.round(currentYards()*.9144);
            RectF info=new RectF(m,h*.126f,w-m,h*.258f);softShadow(c,info,22);box(c,info,Color.rgb(255,253,232),22);
            RectF scene=new RectF(info.left+5,info.top+5,w*.665f,info.bottom-5);c.save();c.clipRect(scene);c.drawBitmap(v12Course,null,scene,p);c.restore();
            box(c,new RectF(scene.left+8,scene.top+8,scene.right-8,scene.bottom-8),Color.argb(42,255,255,255),18);
            textFit(c,ko[selected]+"  "+variants[selected][variant],scene.left+18,scene.top+27,scene.right-12,9.0f,DEEP,true);
            text(c,""+hole,scene.left+47,scene.centerY()+25,32,Color.rgb(54,66,41),true,Paint.Align.CENTER);text(c,"PAR "+par,scene.left+92,scene.centerY()+18,10,Color.rgb(53,58,43),true);
            RectF yard=new RectF(w*.675f,info.top+7,info.right-7,info.bottom-7);gradient(c,yard,Color.rgb(158,106,54),Color.rgb(94,63,33),18);drawWoodGrainV1139(c,yard);sheen(c,yard,18);
            text(c,"YARDAGE",yard.centerX(),yard.top+25,7,Color.rgb(255,239,190),true,Paint.Align.CENTER);text(c,totalM+"m",yard.centerX(),yard.centerY()+20,22,Color.WHITE,true,Paint.Align.CENTER);

            String[] demo={"나","김프로","이프로","박프로"};int[] av={Color.rgb(132,188,73),Color.rgb(72,160,204),Color.rgb(225,145,65),Color.rgb(73,151,135)};
            float top=h*.277f,bottom=h*.646f,gap=h*.009f,rowH=(bottom-top-gap*(n-1))/n;
            for(int i=0;i<4;i++)for(int j=0;j<6;j++)scoreQuickV1139[i][j].setEmpty();
            for(int pl=0;pl<n;pl++){
                float y=top+pl*(rowH+gap);RectF row=new RectF(m,y,w-m,y+rowH);softShadow(c,row,17);box(c,row,Color.rgb(255,252,231),17);
                drawPlayerAvatarV1140(c,row.left+24,row.centerY(),15,av[pl],pl);
                String nm=previewMode?demo[pl]:playerName(pl);RectF nr=new RectF(row.left+43,row.centerY()-18,row.left+103,row.centerY()+18);
                gradient(c,nr,pl==0?Color.rgb(126,180,62):Color.rgb(166,113,54),pl==0?Color.rgb(153,201,74):Color.rgb(132,86,42),12);textFit(c,nm,nr.left+5,nr.centerY()+5,nr.right-5,8.6f,Color.WHITE,true);
                int cur=getStroke(pl,hole,par);float x0=w*.305f,g=(w*.965f-x0)/6f,rr=rowH*.31f;
                for(int j=0;j<6;j++){float cx=x0+g*(j+.5f),cy=row.centerY();scoreQuickV1139[pl][j].set(cx-g*.42f,cy-rr,cx+g*.42f,cy+rr);boolean a=(j<5&&cur==j)||(j==5&&cur>4);box(c,scoreQuickV1139[pl][j],a?Color.rgb(255,210,61):Color.rgb(255,249,225),12);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(a?2.8f:1.5f);p.setColor(a?Color.rgb(188,133,25):Color.rgb(207,184,142));c.drawRoundRect(scoreQuickV1139[pl][j],12,12,p);p.setStyle(Paint.Style.FILL);text(c,j<5?(""+j):"+",cx,cy+6,12.0f,Color.rgb(74,55,34),true,Paint.Align.CENTER);}
            }

            scorePrevV1140.set(m,h*.666f,w*.285f,h*.725f);scoreNextV1140.set(w*.305f,h*.666f,w*.965f,h*.725f);
            box(c,scorePrevV1140,Color.rgb(255,248,220),22);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.6f);p.setColor(Color.rgb(201,177,130));c.drawRoundRect(scorePrevV1140,22,22,p);p.setStyle(Paint.Style.FILL);text(c,"‹ 이전 홀",scorePrevV1140.centerX(),scorePrevV1140.centerY()+5,9.2f,Color.rgb(93,72,42),true,Paint.Align.CENTER);
            gradient(c,scoreNextV1140,Color.rgb(42,133,194),Color.rgb(67,163,214),24);sheen(c,scoreNextV1140,24);text(c,"OK  다음 홀  ›",scoreNextV1140.centerX(),scoreNextV1140.centerY()+7,15.0f,Color.WHITE,true,Paint.Align.CENTER);

            RectF ribbon=new RectF(m,h*.747f,w-m,h*.814f);box(c,ribbon,Color.rgb(209,232,149),22);
            for(int k=0;k<5;k++){int hh=Math.max(1,Math.min(18,hole+k-2));float seg=ribbon.width()/5f,l=ribbon.left+k*seg;scoreHoleV1139[k].set(l+3,ribbon.top+4,l+seg-3,ribbon.bottom-4);boolean a=hh==hole;box(c,scoreHoleV1139[k],a?Color.rgb(255,207,63):Color.argb(0,255,255,255),14);text(c,""+hh,scoreHoleV1139[k].centerX(),ribbon.top+28,a?13:11,a?Color.rgb(75,56,31):DEEP,true,Paint.Align.CENTER);text(c,"PAR"+parForHole(hh),scoreHoleV1139[k].centerX(),ribbon.bottom-9,5.8f,Color.rgb(72,89,49),true,Paint.Align.CENTER);}
            drawStorybookBottomNavV1140(c);
        }'''
s=replace_method(s,'        private void scoreInput(Canvas c)',score)

# Preview/SIM only: show sensible storybook sample ranges; real field GPS remains untouched.
metric=r'''        private void metric(Canvas c,String lab,String val,float x,float y){
            if(previewMode){if(lab.equals("FRONT"))val="148m";else if(lab.equals("CENTER"))val="155m";else if(lab.equals("BACK"))val="163m";}
            float lz=coverHudV1138()?11.2f:10.6f;text(c,lab,x,y,lz,Color.rgb(255,244,210),true,Paint.Align.CENTER);int vc=Color.WHITE;if(lab.equals("FRONT"))vc=Color.rgb(62,177,232);else if(lab.equals("BACK"))vc=Color.rgb(255,126,92);float z=(lab.equals("HOLE")||val.startsWith("H"))?(coverHudV1138()?26.5f:24.5f):(coverHudV1138()?24.2f:23.2f);text(c,val,x,y+getHeight()*(coverHudV1138()? .041f:.039f),z,vc,true,Paint.Align.CENTER);
        }'''
s=replace_method(s,'        private void metric(Canvas c,String lab,String val,float x,float y)',metric)

# Large score prev/next touch enhancement is optional. Quick-score and hole-ribbon touch are already preserved.
needle='            if(screen==2){int pa=currentPar();for(int pl=0;pl<4;pl)'
if needle in s:
    repl='            if(screen==2){if(scorePrevV1140.contains(x,y)){if(hole>1){holeDirection=-1;hole--;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;saveState();}invalidate();return true;}if(scoreNextV1140.contains(x,y)){if(hole<18){holeDirection=1;hole++;lastHoleChange=SystemClock.uptimeMillis();hasTarget=false;saveState();}invalidate();return true;}int pa=currentPar();for(int pl=0;pl<4;pl)'
    s=s.replace(needle,repl,1)
    print('V1.14.0 large score prev/next touch linked')
else:
    print('V1.14.0 optional large-button touch anchor not found; quick-score and hole-ribbon touch preserved')

# Insert the dark-green storybook nav helper. Only play/score screens call it.
anchor='        private boolean coverHudV1138(){'
pos=s.find(anchor)
if pos<0: raise SystemExit('V1.14.0 nav helper anchor missing')
nav=r'''        private void drawStorybookBottomNavV1140(Canvas c){
            float w=getWidth(),h=getHeight();setFourNav(w,h);RectF bar=new RectF(w*.035f,h*.918f,w*.965f,h*.985f);softShadow(c,bar,bar.height()*.34f);gradient(c,bar,Color.rgb(24,112,70),Color.rgb(12,83,57),bar.height()*.34f);sheen(c,bar,bar.height()*.34f);
            RectF[] rr={homeBtn,mapTab,prev,scoreTab,next};String[] tx={"홈","코스","입력","카드","요약"};for(int i=0;i<5;i++){float cx=rr[i].centerX(),cy=bar.centerY();p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.2f);p.setColor(Color.rgb(247,246,221));if(i==0){Path q=new Path();q.moveTo(cx-7,cy-5);q.lineTo(cx,cy-12);q.lineTo(cx+7,cy-5);q.lineTo(cx+7,cy+3);q.lineTo(cx-7,cy+3);q.close();c.drawPath(q,p);}else if(i==1){c.drawCircle(cx,cy-5,7,p);c.drawLine(cx-6,cy+4,cx+6,cy+4,p);}else if(i==2){c.drawCircle(cx,cy-5,7,p);c.drawLine(cx-10,cy-5,cx+10,cy-5,p);c.drawLine(cx,cy-15,cx,cy+5,p);}else if(i==3){c.drawRect(cx-7,cy-12,cx+7,cy+2,p);c.drawLine(cx-4,cy-7,cx+4,cy-7,p);c.drawLine(cx-4,cy-3,cx+4,cy-3,p);}else{for(int k=-1;k<=1;k++)c.drawLine(cx-7,cy-7+k*5,cx+7,cy-7+k*5,p);}p.setStyle(Paint.Style.FILL);text(c,tx[i],cx,cy+18,6.9f,Color.rgb(250,248,224),true,Paint.Align.CENTER);}
        }

'''
s=s[:pos]+nav+s[pos:]

# Use the dark storybook nav only in the two play renderers, preserving other screens.
for sig in ['        private void roundJapanPremium(Canvas c)','        private void roundKorea(Canvas c)']:
    try:
        a,b=bounds(s,sig);chunk=s[a:b]
    except SystemExit:
        continue
    if 'setFourNav(w,h);drawGoldenNav(c);' in chunk:
        chunk=chunk.replace('setFourNav(w,h);drawGoldenNav(c);','drawStorybookBottomNavV1140(c);')
        s=s[:a]+chunk+s[b:]

p.write_text(s)
print('V1.14.0 runtime fix: live scoreInput + preview distances + storybook play nav')
