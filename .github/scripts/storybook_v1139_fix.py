from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

# V1.14.0 approved visual master.
# Keep all geo/course/GPS logic intact; replace only the approved Yardage/Score presentation layer.

def replace_method(src, signature, replacement):
    start=src.find(signature)
    if start < 0:
        raise SystemExit('missing method: '+signature)
    brace=src.find('{',start)
    depth=0
    end=-1
    for i in range(brace,len(src)):
        if src[i]=='{': depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0:
                end=i+1
                break
    if end < 0:
        raise SystemExit('unclosed method: '+signature)
    return src[:start]+replacement+src[end:]

# -------- SCORE: approved 0/1/2/3/4/+ one-tap storybook layout --------
score=r'''        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.035f;
            c.drawColor(Color.rgb(249,247,224));
            int par=currentPar();
            int totalM=verifiedMetersV190();
            if(totalM<=0) totalM=(int)Math.round(currentYards()*.9144);

            // Bright illustrated sky header.
            RectF sky=new RectF(0,0,w,h*.118f);
            gradient(c,sky,Color.rgb(43,167,218),Color.rgb(81,187,220),0);
            drawStoryCloudV1139(c,w*.76f,h*.037f,17);
            drawStoryCloudV1139(c,w*.88f,h*.066f,10);
            text(c,"‹",m,h*.071f,27,Color.WHITE,true);
            text(c,"스코어 입력",w/2,h*.071f,20.5f,Color.WHITE,true,Paint.Align.CENTER);
            pill(c,new RectF(w*.745f,h*.026f,w*.965f,h*.070f),Color.rgb(255,246,215),"라운드 정보",Color.rgb(86,69,38),7.4f);

            // Hole summary: illustrated course card + wood yardage board.
            RectF info=new RectF(m,h*.125f,w-m,h*.258f);
            softShadow(c,info,22); box(c,info,Color.rgb(255,253,232),22);
            RectF scene=new RectF(info.left+5,info.top+5,w*.665f,info.bottom-5);
            c.save(); c.clipRect(scene); c.drawBitmap(v12Course,null,scene,p); c.restore();
            box(c,new RectF(scene.left+8,scene.top+8,scene.right-8,scene.bottom-8),Color.argb(42,255,255,255),18);
            textFit(c,ko[selected]+"  "+variants[selected][variant],scene.left+18,scene.top+27,scene.right-14,9.0f,DEEP,true);
            text(c,""+hole,scene.left+46,scene.centerY()+25,32.0f,Color.rgb(55,67,42),true,Paint.Align.CENTER);
            text(c,"PAR "+par,scene.left+91,scene.centerY()+18,10.0f,Color.rgb(53,58,43),true);
            RectF yard=new RectF(w*.675f,info.top+7,info.right-7,info.bottom-7);
            gradient(c,yard,Color.rgb(157,105,53),Color.rgb(96,64,34),18); drawWoodGrainV1139(c,yard); sheen(c,yard,18);
            text(c,"YARDAGE",yard.centerX(),yard.top+26,7.0f,Color.rgb(255,239,190),true,Paint.Align.CENTER);
            text(c,totalM+"m",yard.centerX(),yard.centerY()+20,22.5f,Color.WHITE,true,Paint.Align.CENTER);

            // Four-player one-tap grid, matching the approved reference.
            String[] names={"나","김프로","이프로","박프로"};
            int[] avatar={Color.rgb(132,188,73),Color.rgb(72,160,204),Color.rgb(225,145,65),Color.rgb(73,151,135)};
            float panelTop=h*.272f,rowH=h*.078f,rowGap=h*.010f;
            for(int pl=0;pl<4;pl++){
                float y=panelTop+pl*(rowH+rowGap);
                RectF row=new RectF(m,y,w-m,y+rowH);
                softShadow(c,row,17); box(c,row,Color.rgb(255,252,231),17);
                drawPlayerAvatarV1140(c,row.left+25,row.centerY(),15,avatar[pl],pl);
                RectF nameR=new RectF(row.left+43,row.centerY()-18,row.left+102,row.centerY()+18);
                gradient(c,nameR,pl==0?Color.rgb(126,180,62):Color.rgb(166,113,54),pl==0?Color.rgb(153,201,74):Color.rgb(132,86,42),12);
                text(c,names[pl],nameR.centerX(),nameR.centerY()+5,8.7f,Color.WHITE,true,Paint.Align.CENTER);
                int cur=getStroke(pl,hole,par);
                float x0=w*.305f,g=(w*.965f-x0)/6f,rr=rowH*.31f;
                for(int j=0;j<6;j++){
                    float cx=x0+g*(j+.5f),cy=row.centerY();
                    scoreQuickV1139[pl][j].set(cx-g*.42f,cy-rr,cx+g*.42f,cy+rr);
                    boolean active=(j<5&&cur==j)||(j==5&&cur>4);
                    int bg=active?Color.rgb(255,210,61):Color.rgb(255,249,225);
                    box(c,scoreQuickV1139[pl][j],bg,12);
                    p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(active?2.8f:1.5f);
                    p.setColor(active?Color.rgb(188,133,25):Color.rgb(207,184,142));
                    c.drawRoundRect(scoreQuickV1139[pl][j],12,12,p); p.setStyle(Paint.Style.FILL);
                    text(c,j<5?(""+j):"+",cx,cy+6,12.1f,Color.rgb(74,55,34),true,Paint.Align.CENTER);
                }
            }

            // Large one-hand hole controls.
            prev.set(m,h*.644f,w*.29f,h*.704f);
            next.set(w*.305f,h*.644f,w*.965f,h*.704f);
            box(c,prev,Color.rgb(255,248,220),22);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.6f);p.setColor(Color.rgb(201,177,130));c.drawRoundRect(prev,22,22,p);p.setStyle(Paint.Style.FILL);
            text(c,"‹ 이전 홀",prev.centerX(),prev.centerY()+5,9.2f,Color.rgb(93,72,42),true,Paint.Align.CENTER);
            gradient(c,next,Color.rgb(42,133,194),Color.rgb(67,163,214),24);sheen(c,next,24);
            text(c,"OK  다음 홀  ›",next.centerX(),next.centerY()+7,15.2f,Color.WHITE,true,Paint.Align.CENTER);

            // Hole ribbon.
            RectF ribbon=new RectF(m,h*.723f,w-m,h*.790f); box(c,ribbon,Color.rgb(209,232,149),22);
            for(int k=0;k<5;k++){
                int hh=Math.max(1,Math.min(18,hole+k-2));float seg=ribbon.width()/5f,l=ribbon.left+k*seg;
                scoreHoleV1139[k].set(l+3,ribbon.top+4,l+seg-3,ribbon.bottom-4);
                boolean a=hh==hole; box(c,scoreHoleV1139[k],a?Color.rgb(255,207,63):Color.argb(0,255,255,255),14);
                text(c,""+hh,scoreHoleV1139[k].centerX(),ribbon.top+28,a?13.0f:11.0f,a?Color.rgb(75,56,31):DEEP,true,Paint.Align.CENTER);
                text(c,"PAR"+parForHole(hh),scoreHoleV1139[k].centerX(),ribbon.bottom-9,5.8f,Color.rgb(72,89,49),true,Paint.Align.CENTER);
            }

            setFourNav(w,h); drawGoldenNav(c);
        }'''
s=replace_method(s,'        private void score(Canvas c)',score)

# Quick buttons are literal 0/1/2/3/4/+ as approved. 0 = clear/not-entered.
s=s.replace('int nv=j<5?Math.max(1,pa-2+j):getStroke(pl,hole,pa)+1;',
            'int nv=j<5?j:getStroke(pl,hole,pa)+1;',1)

# -------- YARDAGE: lock approved storybook palette without touching geo math --------
s=s.replace('gradient(c,head,Color.rgb(48,164,229),Color.rgb(91,190,228),0);',
            'gradient(c,head,Color.rgb(38,161,214),Color.rgb(75,187,222),0);',1)
s=s.replace('gradient(c,range,Color.rgb(151,103,53),Color.rgb(93,64,35),18);drawWoodGrainV1139(c,range);sheen(c,range,18);',
            'gradient(c,range,Color.rgb(157,105,53),Color.rgb(91,61,31),20);drawWoodGrainV1139(c,range);sheen(c,range,20);',1)

# FRONT blue / CENTER white / BACK coral like the approved artwork.
metric_sig='        private void metric(Canvas c,String lab,String val,float x,float y)'
metric=r'''        private void metric(Canvas c,String lab,String val,float x,float y){
            float lz=coverHudV1138()?11.2f:10.6f;
            text(c,lab,x,y,lz,Color.rgb(255,244,210),true,Paint.Align.CENTER);
            int vc=Color.WHITE;
            if(lab.equals("FRONT"))vc=Color.rgb(62,177,232);
            else if(lab.equals("BACK"))vc=Color.rgb(255,126,92);
            float z=(lab.equals("HOLE")||val.startsWith("H"))?(coverHudV1138()?26.5f:24.5f):(coverHudV1138()?24.2f:23.2f);
            text(c,val,x,y+getHeight()*(coverHudV1138()? .041f:.039f),z,vc,true,Paint.Align.CENTER);
        }'''
s=replace_method(s,metric_sig,metric)

# Helper for small storybook player portraits.
anchor='        private boolean coverHudV1138(){'
pos=s.find(anchor)
if pos<0: raise SystemExit('V1.14.0 helper anchor missing')
helper=r'''        private void drawPlayerAvatarV1140(Canvas c,float x,float y,float r,int cap,int idx){
            p.setColor(cap);c.drawCircle(x,y,r,p);
            p.setColor(Color.rgb(255,224,179));c.drawCircle(x,y+1,r*.68f,p);
            p.setColor(Color.rgb(67,48,35));c.drawCircle(x-r*.24f,y-r*.06f,1.4f,p);c.drawCircle(x+r*.24f,y-r*.06f,1.4f,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.3f);p.setColor(Color.rgb(118,67,43));c.drawArc(new RectF(x-r*.23f,y+r*.05f,x+r*.23f,y+r*.38f),10,160,false,p);p.setStyle(Paint.Style.FILL);
            p.setColor(cap);c.drawRect(x-r*.62f,y-r*.82f,x+r*.62f,y-r*.54f,p);
        }

'''
s=s[:pos]+helper+s[pos:]

# Visible build marker for gate/debugging.
s=s.replace('V1.13.8 · COVER HUD','V1.14.0 · STORYBOOK MASTER',1)

p.write_text(s)
print('V1.14.0 STORYBOOK MASTER applied: approved yardage palette + 0/1/2/3/4/+ score grid')
