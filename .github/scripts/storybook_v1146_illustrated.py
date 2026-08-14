from pathlib import Path

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
    raise SystemExit('unclosed method: '+signature)


def replace_method(src,signature,replacement):
    a,b=bounds(src,signature);return src[:a]+replacement+src[b:]

# V1.14.6 master marker without breaking the V1.13.8 legacy gate token.
if 'V1.14.6 · ILLUSTRATED MASTER' not in s:
    s=s.replace('V1.13.8 · COVER HUD / V1.14.0 · STORYBOOK MASTER','V1.13.8 · COVER HUD / V1.14.0 · STORYBOOK MASTER / V1.14.6 · ILLUSTRATED MASTER',1)

# Yardage art fills the card. Remove the old explanatory footer completely.
full=r'''        private void drawFullHoleYardageV1102(Canvas c,RectF r,int par,int totalM){
            Bitmap b=fullHoleBitmapV1102();if(b==null){drawActualYardageV190(c,r,par,totalM);return;}
            softShadow(c,r,30);box(c,r,Color.rgb(250,247,218),30);
            RectF stage=new RectF(r.left+7,r.top+7,r.right-7,r.bottom-7);box(c,stage,Color.rgb(29,92,51),25);
            RectF dst=fitCenterV1102(b,new RectF(stage.left+3,stage.top+3,stage.right-3,stage.bottom-3));
            Paint bp=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);c.drawBitmap(b,null,dst,bp);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3.2f);p.setColor(Color.argb(145,255,250,211));c.drawRoundRect(stage,25,25,p);p.setStyle(Paint.Style.FILL);
        }'''
s=replace_method(s,'        private void drawFullHoleYardageV1102(Canvas c,RectF r,int par,int totalM)',full)

# Bigger play HUD typography to match the approved illustrated mockup.
metric=r'''        private void metric(Canvas c,String lab,String val,float x,float y){
            if(previewMode){if(lab.equals("FRONT"))val="148m";else if(lab.equals("CENTER"))val="155m";else if(lab.equals("BACK"))val="163m";}
            text(c,lab,x,y,13.8f,Color.rgb(255,242,198),true,Paint.Align.CENTER);
            int vc=Color.WHITE;if(lab.equals("FRONT"))vc=Color.rgb(58,181,237);else if(lab.equals("BACK"))vc=Color.rgb(255,124,91);
            float z=(lab.equals("HOLE")||val.startsWith("H"))?32.5f:30.0f;
            text(c,val,x,y+getHeight()*.040f,z,vc,true,Paint.Align.CENTER);
        }'''
s=replace_method(s,'        private void metric(Canvas c,String lab,String val,float x,float y)',metric)

title=r'''        private void drawPlayTitleV1137(Canvas c,float m,float w,float h){
            String title=ko[selected],course=variants[selected][variant];float ty=h*(coverHudV1138()? .066f:.052f);
            textFit(c,title,m,ty,w*.67f,21.0f,Color.WHITE,true);
            textFit(c,course,m,ty+h*(coverHudV1138()? .034f:.030f),w*.67f,14.0f,Color.rgb(239,252,239),true);
        }'''
s=replace_method(s,'        private void drawPlayTitleV1137(Canvas c,float m,float w,float h)',title)

# 2.5x navigation label scale. Keep existing touch rectangles so functionality is unchanged.
nav=r'''        private void drawStorybookBottomNavV1140(Canvas c){
            float w=getWidth(),h=getHeight();setFourNav(w,h);p.setAlpha(255);p.setStyle(Paint.Style.FILL);
            RectF bar=new RectF(w*.018f,h*.868f,w*.982f,h*.992f);softShadow(c,bar,bar.height()*.25f);p.setColor(Color.rgb(13,91,57));c.drawRoundRect(bar,bar.height()*.25f,bar.height()*.25f,p);
            p.setColor(Color.argb(38,255,255,255));c.drawRoundRect(new RectF(bar.left+4,bar.top+4,bar.right-4,bar.top+bar.height()*.43f),bar.height()*.20f,bar.height()*.20f,p);
            RectF[] rr={homeBtn,mapTab,prev,scoreTab,next};String[] tx={"스코어","코스","타겟","홈","메뉴"};
            for(int i=0;i<5;i++){
                float cx=rr[i].centerX(),cy=bar.top+bar.height()*.29f;p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4.2f);p.setColor(Color.WHITE);float q=14.5f;
                if(i==0){p.setStyle(Paint.Style.FILL);Path z=new Path();z.moveTo(cx-q*.72f,cy+q*.40f);z.lineTo(cx-q*.38f,cy-q*.18f);z.lineTo(cx+q*.72f,cy-q*.92f);p.setColor(Color.WHITE);c.drawPath(z,p);p.setStyle(Paint.Style.STROKE);c.drawRect(cx-q*.62f,cy-q*.22f,cx+q*.62f,cy+q*.52f,p);c.drawLine(cx-q*.34f,cy+q*.30f,cx+q*.42f,cy-q*.46f,p);}
                else if(i==1){c.drawCircle(cx,cy-3,13,p);c.drawLine(cx-12,cy+12,cx+12,cy+12,p);c.drawCircle(cx-5,cy-6,3,p);c.drawCircle(cx+5,cy-6,3,p);}
                else if(i==2){c.drawCircle(cx,cy-3,13,p);c.drawCircle(cx,cy-3,4,p);c.drawLine(cx-18,cy-3,cx+18,cy-3,p);c.drawLine(cx,cy-21,cx,cy+15,p);}
                else if(i==3){Path z=new Path();z.moveTo(cx-14,cy-2);z.lineTo(cx,cy-17);z.lineTo(cx+14,cy-2);z.lineTo(cx+14,cy+13);z.lineTo(cx-14,cy+13);z.close();c.drawPath(z,p);}
                else{for(int k=-1;k<=1;k++){c.drawCircle(cx-14,cy-10+k*10,2.1f,p);c.drawLine(cx-7,cy-10+k*10,cx+14,cy-10+k*10,p);}}
                p.setStyle(Paint.Style.FILL);text(c,tx[i],cx,bar.bottom-11,23.5f,Color.WHITE,true,Paint.Align.CENTER);
            }p.setAlpha(255);
        }'''
s=replace_method(s,'        private void drawStorybookBottomNavV1140(Canvas c)',nav)

# Score screen: enlarge title, names, quick-score numbers, action labels and hole ribbon.
repls={
    'text(c,"스코어 입력",w/2,h*.082f,23.0f':'text(c,"스코어 입력",w/2,h*.082f,27.0f',
    '"라운드 정보",Color.rgb(86,65,36),8.8f':'"라운드 정보",Color.rgb(86,65,36),13.5f',
    'scene.right-10,10.5f,DEEP,true':'scene.right-10,15.5f,DEEP,true',
    'scene.centerY()+28,35,Color.rgb(52,65,40)':'scene.centerY()+30,44,Color.rgb(52,65,40)',
    'scene.centerY()+20,11.5f,Color.rgb(50,58,41)':'scene.centerY()+21,16.0f,Color.rgb(50,58,41)',
    'yard.top+25,9.0f,Color.rgb(255,239,190)':'yard.top+25,13.0f,Color.rgb(255,239,190)',
    'yard.centerY()+22,27.0f,Color.WHITE':'yard.centerY()+24,34.0f,Color.WHITE',
    'row.left+116,row.centerY()+20':'row.left+152,row.centerY()+20',
    'nr.right-6,10.5f,Color.WHITE,true':'nr.right-6,15.5f,Color.WHITE,true',
    'float x0=w*.325f,g=(w*.970f-x0)/6f':'float x0=w*.385f,g=(w*.970f-x0)/6f',
    'cy+7,15.0f,Color.rgb(73,54,33)':'cy+8,21.0f,Color.rgb(73,54,33)',
    'scorePrevV1140.centerY()+6,11.0f,Color.rgb(92,70,41)':'scorePrevV1140.centerY()+7,15.5f,Color.rgb(92,70,41)',
    'scoreNextV1140.centerY()+7,17.0f,Color.WHITE':'scoreNextV1140.centerY()+8,21.0f,Color.WHITE',
    'ribbon.top+34,a?16.0f:14.0f':'ribbon.top+36,a?20.0f:18.0f',
    'ribbon.bottom-11,8.4f,Color.rgb(72,88,48)':'ribbon.bottom-10,11.5f,Color.rgb(72,88,48)'
}
for a,b in repls.items():
    if a in s:s=s.replace(a,b,1)

# Remove technical strategy copy from the live yardage area; illustration + target/GPS are the hierarchy.
s=s.replace('text(c,"공략",strategy.left+10,h*.870f,9.6f,GREEN,true);','')
s=s.replace('textFit(c,fieldGuideV1100(),strategy.left+56,h*.870f,strategy.right-8,9.1f,INK,true);','')

p.write_text(s)
print('V1.14.6 ILLUSTRATED MASTER: full-art yardage + 2.5x nav labels + enlarged score typography')
