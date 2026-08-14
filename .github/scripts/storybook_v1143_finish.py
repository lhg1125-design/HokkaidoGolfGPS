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

# Remove engineering ruler. The top FRONT/CENTER/BACK board is the only distance hierarchy.
s=replace_method(s,'        private void drawDistanceRulerV1102(Canvas c,RectF a,int totalM)',r'''        private void drawDistanceRulerV1102(Canvas c,RectF a,int totalM){ }''')

# Full-hole card: image dominates like the approved reference; no nested title/ruler/source jargon.
full=r'''        private void drawFullHoleYardageV1102(Canvas c,RectF r,int par,int totalM){
            Bitmap b=fullHoleBitmapV1102();if(b==null){drawActualYardageV190(c,r,par,totalM);return;}
            softShadow(c,r,28);box(c,r,Color.rgb(232,243,207),28);
            RectF stage=new RectF(r.left+7,r.top+7,r.right-7,r.bottom-38);box(c,stage,Color.rgb(34,107,57),24);
            RectF dst=fitCenterV1102(b,new RectF(stage.left+3,stage.top+3,stage.right-3,stage.bottom-3));Paint bp=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);c.drawBitmap(b,null,dst,bp);
            RectF src=new RectF(r.left+10,r.bottom-34,r.right-10,r.bottom-6);box(c,src,Color.rgb(242,248,220),14);textFit(c,"동화풍 홀맵  ·  실제 GPS 위치 연동",src.left+10,src.centerY()+4,src.right-10,8.8f,Color.rgb(35,103,61),true);
        }'''
s=replace_method(s,'        private void drawFullHoleYardageV1102(Canvas c,RectF r,int par,int totalM)',full)

# Replace the reused screenshot inside the score header with a clean hand-drawn landscape.
old='c.save();c.clipRect(scene);c.drawBitmap(v12Course,null,scene,p);c.restore();'
if old in s:s=s.replace(old,'drawScoreLandscapeV1143(c,scene);',1)

# Dark green, high-contrast bottom nav. Direct fills avoid Paint alpha leakage seen in emulator captures.
nav=r'''        private void drawStorybookBottomNavV1140(Canvas c){
            float w=getWidth(),h=getHeight();setFourNav(w,h);p.setAlpha(255);p.setStyle(Paint.Style.FILL);
            RectF bar=new RectF(w*.025f,h*.884f,w*.975f,h*.985f);softShadow(c,bar,bar.height()*.28f);p.setColor(Color.rgb(16,93,61));c.drawRoundRect(bar,bar.height()*.28f,bar.height()*.28f,p);
            p.setColor(Color.argb(35,255,255,255));c.drawRoundRect(new RectF(bar.left+4,bar.top+4,bar.right-4,bar.top+bar.height()*.48f),bar.height()*.22f,bar.height()*.22f,p);
            RectF[] rr={homeBtn,mapTab,prev,scoreTab,next};String[] tx={"스코어","코스","타겟","홈","메뉴"};
            for(int i=0;i<5;i++){float cx=rr[i].centerX(),cy=bar.top+bar.height()*.38f;p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3.1f);p.setColor(Color.WHITE);float z=10.5f;
                if(i==0){p.setStyle(Paint.Style.FILL);Path q=new Path();q.moveTo(cx-9,cy+7);q.lineTo(cx-5,cy-3);q.lineTo(cx+10,cy-15);p.setColor(Color.WHITE);c.drawPath(q,p);p.setStyle(Paint.Style.STROKE);c.drawRect(cx-8,cy-4,cx+8,cy+9,p);c.drawLine(cx-5,cy+4,cx+6,cy-7,p);}
                else if(i==1){c.drawCircle(cx,cy-3,9,p);c.drawLine(cx-8,cy+9,cx+8,cy+9,p);c.drawCircle(cx-4,cy-5,2,p);c.drawCircle(cx+4,cy-5,2,p);}
                else if(i==2){c.drawCircle(cx,cy-3,9,p);c.drawCircle(cx,cy-3,3,p);c.drawLine(cx-13,cy-3,cx+13,cy-3,p);c.drawLine(cx,cy-16,cx,cy+10,p);}
                else if(i==3){Path q=new Path();q.moveTo(cx-10,cy-2);q.lineTo(cx,cy-13);q.lineTo(cx+10,cy-2);q.lineTo(cx+10,cy+9);q.lineTo(cx-10,cy+9);q.close();c.drawPath(q,p);}
                else{for(int k=-1;k<=1;k++){c.drawCircle(cx-10,cy-7+k*7,1.5f,p);c.drawLine(cx-5,cy-7+k*7,cx+10,cy-7+k*7,p);}}
                p.setStyle(Paint.Style.FILL);text(c,tx[i],cx,bar.bottom-10,10.4f,Color.WHITE,true,Paint.Align.CENTER);
            }p.setAlpha(255);
        }'''
s=replace_method(s,'        private void drawStorybookBottomNavV1140(Canvas c)',nav)

anchor='        private boolean coverHudV1138(){'
pos=s.find(anchor)
if pos<0:raise SystemExit('finish helper anchor missing')
helper=r'''        private void drawScoreLandscapeV1143(Canvas c,RectF r){
            p.setStyle(Paint.Style.FILL);LinearGradient sky=new LinearGradient(0,r.top,0,r.bottom,Color.rgb(99,199,225),Color.rgb(226,240,190),Shader.TileMode.CLAMP);p.setShader(sky);c.drawRoundRect(r,18,18,p);p.setShader(null);
            Path hill=new Path();hill.moveTo(r.left,r.bottom*.0f+r.top+r.height()*.57f);hill.quadTo(r.left+r.width()*.18f,r.top+r.height()*.31f,r.left+r.width()*.37f,r.top+r.height()*.55f);hill.quadTo(r.left+r.width()*.56f,r.top+r.height()*.26f,r.left+r.width()*.76f,r.top+r.height()*.56f);hill.quadTo(r.left+r.width()*.90f,r.top+r.height()*.39f,r.right,r.top+r.height()*.58f);hill.lineTo(r.right,r.bottom);hill.lineTo(r.left,r.bottom);hill.close();p.setColor(Color.rgb(91,166,91));c.drawPath(hill,p);
            Path fair=new Path();fair.moveTo(r.left+r.width()*.38f,r.bottom);fair.quadTo(r.left+r.width()*.42f,r.top+r.height()*.64f,r.left+r.width()*.54f,r.top+r.height()*.52f);fair.quadTo(r.left+r.width()*.62f,r.top+r.height()*.39f,r.left+r.width()*.58f,r.top+r.height()*.22f);fair.lineTo(r.left+r.width()*.72f,r.top+r.height()*.20f);fair.quadTo(r.left+r.width()*.75f,r.top+r.height()*.43f,r.left+r.width()*.62f,r.top+r.height()*.58f);fair.quadTo(r.left+r.width()*.53f,r.top+r.height()*.72f,r.left+r.width()*.60f,r.bottom);fair.close();p.setColor(Color.rgb(142,207,81));c.drawPath(fair,p);
            for(int i=0;i<7;i++){float x=r.left+r.width()*(.08f+i*.14f),y=r.bottom-r.height()*(.12f+(i%2)*.08f);p.setColor(Color.rgb(48,130+(i%3)*10,60));c.drawCircle(x,y,r.height()*.09f,p);p.setColor(Color.rgb(104,72,41));c.drawRect(x-2,y+r.height()*.05f,x+2,y+r.height()*.16f,p);}
            p.setColor(Color.rgb(249,224,157));c.drawOval(new RectF(r.left+r.width()*.25f,r.top+r.height()*.58f,r.left+r.width()*.34f,r.top+r.height()*.70f),p);p.setColor(Color.rgb(64,164,214));c.drawOval(new RectF(r.left+r.width()*.70f,r.top+r.height()*.58f,r.left+r.width()*.86f,r.top+r.height()*.78f),p);
        }

'''
s=s[:pos]+helper+s[pos:]

p.write_text(s)
print('V1.14.3 finish: dominant illustrated hole card, no ruler jargon, dark readable bottom nav')
