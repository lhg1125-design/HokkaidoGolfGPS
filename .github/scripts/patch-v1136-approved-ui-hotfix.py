from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

MARK='V1.13.6 APPROVED UI HOTFIX'
if MARK in s:
    print('approved UI hotfix already applied')
    raise SystemExit(0)

def replace_method(src, signature, body):
    start=src.find(signature)
    if start<0:
        raise SystemExit('missing method '+signature)
    brace=src.find('{',start)
    if brace<0:
        raise SystemExit('missing opening brace '+signature)
    depth=0
    end=None
    for i in range(brace,len(src)):
        ch=src[i]
        if ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:
                end=i+1
                break
    if end is None:
        raise SystemExit('unbalanced method '+signature)
    return src[:start]+body+src[end:]

round_body=r'''        private void round(Canvas c){
            // V1.13.6 APPROVED UI HOTFIX
            float w=getWidth(),h=getHeight();
            int par=currentPar();
            int totalM=(int)Math.round(currentYards()*.9144);
            GeoRef green=greenCenterRef(hole);
            Distances ds=distances(green);
            int distM=ds.center>=0?ds.center:totalM;
            c.drawColor(Color.rgb(254,253,237));

            // Sky header and exact approved hierarchy.
            RectF sky=new RectF(0,0,w,h*.056f);box(c,sky,Color.rgb(75,174,218),0);
            textFit(c,ko[selected],w*.040f,h*.025f,w*.545f,13.8f,Color.WHITE,true);
            textFit(c,variants[selected][variant],w*.040f,h*.049f,w*.550f,15.5f,Color.WHITE,true);
            drawApprovedWeatherGpsV1136(c,w,h);

            RectF metrics=new RectF(w*.035f,h*.056f,w*.965f,h*.098f);
            box(c,metrics,Color.rgb(58,145,91),18);
            holePrevBtn.set(w*.040f,h*.059f,w*.135f,h*.095f);
            holeNextBtn.set(w*.865f,h*.059f,w*.960f,h*.095f);
            drawApprovedArrowV1136(c,holePrevBtn,false);
            drawApprovedArrowV1136(c,holeNextBtn,true);
            drawApprovedMetricV1136(c,"TOTAL",totalM+"m",w*.295f,h*.072f,h*.091f);
            drawApprovedMetricV1136(c,"DIST",distM+"m",w*.515f,h*.072f,h*.091f);
            drawApprovedMetricV1136(c,"PAR",""+par,w*.720f,h*.072f,h*.091f);

            RectF panel=new RectF(w*.035f,h*.103f,w*.965f,h*.842f);
            box(c,panel,Color.rgb(243,249,220),28);
            RectF greenTag=new RectF(w*.050f,h*.109f,w*.127f,h*.132f);
            box(c,greenTag,Color.rgb(28,112,72),13);
            text(c,"GREEN",greenTag.centerX(),greenTag.centerY()+3,6.6f,Color.WHITE,true,Paint.Align.CENTER);

            RectF hc=new RectF(w*.052f,h*.176f,w*.168f,h*.238f);
            RectF pc=new RectF(w*.178f,h*.176f,w*.258f,h*.238f);
            drawApprovedNumberCardV1136(c,hc,"HOLE","H"+hole,22.5f);
            drawApprovedNumberCardV1136(c,pc,"PAR",""+par,24.0f);

            Bitmap b=fullHoleBitmapV1102();
            RectF imgFrame=new RectF(w*.285f,h*.145f,w*.685f,h*.790f);
            box(c,imgFrame,Color.rgb(255,255,248),0);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.2f);p.setColor(Color.rgb(209,217,190));c.drawRect(imgFrame,p);p.setStyle(Paint.Style.FILL);
            RectF imgInner=new RectF(imgFrame.left+w*.012f,imgFrame.top+h*.015f,imgFrame.right-w*.008f,imgFrame.bottom-h*.010f);
            if(b!=null){
                RectF dst=fitCenterV1102(b,imgInner);
                Paint bp=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
                c.drawBitmap(b,null,dst,bp);
            }else{
                drawActualYardageV190(c,imgInner,par,totalM);
            }
            courseRect.set(imgInner);
            drawApprovedRulerV1136(c,w,h,imgFrame,totalM);

            RectF teeTag=new RectF(w*.050f,h*.807f,w*.113f,h*.830f);
            box(c,teeTag,Color.rgb(28,112,72),13);
            text(c,"TEE",teeTag.centerX(),teeTag.centerY()+3,6.4f,Color.WHITE,true,Paint.Align.CENTER);
            String src=selected==2?"RAKUTEN GORA FULL HOLE":"PRINCE OFFICIAL FULL HOLE";
            textFit(c,src+" · TEE → GREEN",w*.052f,h*.835f,w*.930f,6.8f,Color.rgb(70,122,78),true);

            greenSave.set(w*.035f,h*.850f,w*.355f,h*.910f);
            teeSave.set(w*.370f,h*.850f,w*.670f,h*.910f);
            mapLaunch.set(w*.685f,h*.850f,w*.965f,h*.910f);
            drawApprovedActionV1136(c,greenSave,"GREEN CENTER",Color.rgb(165,178,167),Color.WHITE);
            drawApprovedActionV1136(c,teeSave,"TEE 저장",Color.rgb(165,178,167),Color.WHITE);
            drawApprovedActionV1136(c,mapLaunch,"외부 지도",Color.rgb(255,255,247),INK);

            setFourNav(w,h);
            drawApprovedNavV1136(c,w,h);
        }'''

s=replace_method(s,'        private void round(Canvas c){',round_body)

marker='        private void scoreInput(Canvas c){'
pos=s.find(marker)
if pos<0:
    marker='        private void score(Canvas c){'
    pos=s.find(marker)
if pos<0:
    raise SystemExit('score insertion marker missing')

helpers=r'''        private void drawApprovedWeatherGpsV1136(Canvas c,float w,float h){
            RectF r=new RectF(w*.580f,h*.004f,w*.978f,h*.052f);
            softShadow(c,r,18);box(c,r,Color.rgb(255,255,248),18);
            float sy=r.top+r.height()*.36f;
            p.setColor(Color.rgb(246,190,51));c.drawCircle(r.left+r.width()*.10f,sy,7,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2);p.setColor(Color.rgb(228,171,34));
            for(int i=0;i<8;i++){double a=i*Math.PI/4;float x1=(float)(r.left+r.width()*.10f+11*Math.cos(a)),y1=(float)(sy+11*Math.sin(a)),x2=(float)(r.left+r.width()*.10f+15*Math.cos(a)),y2=(float)(sy+15*Math.sin(a));c.drawLine(x1,y1,x2,y2,p);}p.setStyle(Paint.Style.FILL);
            text(c,"19°",r.left+r.width()*.22f,r.top+r.height()*.40f,15.0f,INK,true);
            text(c,"맑음",r.left+r.width()*.35f,r.top+r.height()*.36f,6.2f,Color.rgb(75,90,73),true);
            text(c,"➜  E",r.left+r.width()*.08f,r.top+r.height()*.78f,9.4f,Color.rgb(58,115,132),true);
            text(c,"2.0 m/s",r.left+r.width()*.25f,r.top+r.height()*.78f,10.4f,INK,true);
            boolean good=gpsUsable();
            text(c,"GPS",r.left+r.width()*.66f,r.top+r.height()*.34f,10.5f,DEEP,true);
            int bars=1;if(location!=null){float a=location.getAccuracy();bars=a<=5?4:(a<=8?3:(a<=12?2:1));}
            for(int i=0;i<4;i++){float bh=4+i*4;RectF br=new RectF(r.left+r.width()*(.80f+i*.045f),r.top+r.height()*.36f-bh,r.left+r.width()*(.83f+i*.045f),r.top+r.height()*.36f);box(c,br,i<bars?Color.rgb(73,166,104):Color.rgb(207,218,205),3);}
            text(c,good?"GOOD":"WAIT",r.left+r.width()*.70f,r.top+r.height()*.79f,8.0f,good?Color.rgb(70,153,95):Color.rgb(190,122,62),true);
        }

        private void drawApprovedArrowV1136(Canvas c,RectF r,boolean right){
            p.setColor(Color.rgb(255,255,248));c.drawOval(r,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4.5f);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);p.setColor(Color.rgb(27,104,73));
            float cy=r.centerY(),cx=r.centerX();float dx=r.width()*.22f;
            if(right){c.drawLine(cx-dx,cy,cx+dx,cy,p);c.drawLine(cx+dx,cy,cx+dx*.35f,cy-dx*.65f,p);c.drawLine(cx+dx,cy,cx+dx*.35f,cy+dx*.65f,p);}else{c.drawLine(cx+dx,cy,cx-dx,cy,p);c.drawLine(cx-dx,cy,cx-dx*.35f,cy-dx*.65f,p);c.drawLine(cx-dx,cy,cx-dx*.35f,cy+dx*.65f,p);}
            p.setStyle(Paint.Style.FILL);p.setStrokeCap(Paint.Cap.BUTT);
        }

        private void drawApprovedMetricV1136(Canvas c,String lab,String val,float cx,float y1,float y2){
            text(c,lab,cx,y1,12.0f,Color.WHITE,true,Paint.Align.CENTER);
            text(c,val,cx,y2,18.5f,Color.WHITE,true,Paint.Align.CENTER);
        }

        private void drawApprovedNumberCardV1136(Canvas c,RectF r,String lab,String val,float vs){
            softShadow(c,r,12);box(c,r,Color.rgb(255,255,247),12);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3.4f);p.setColor(Color.rgb(196,145,45));c.drawRoundRect(r,12,12,p);
            RectF in=new RectF(r.left+4,r.top+4,r.right-4,r.bottom-4);p.setStrokeWidth(1.2f);p.setColor(Color.rgb(229,197,117));c.drawRoundRect(in,9,9,p);p.setStyle(Paint.Style.FILL);
            text(c,lab,r.centerX(),r.top+r.height()*.27f,6.4f,Color.rgb(131,96,36),true,Paint.Align.CENTER);
            text(c,val,r.centerX(),r.top+r.height()*.78f,vs,DEEP,true,Paint.Align.CENTER);
        }

        private void drawApprovedRulerV1136(Canvas c,float w,float h,RectF img,int totalM){
            if(totalM<=0)return;
            int max=Math.max(100,totalM);
            for(int d=50;d<max;d+=50){
                float y=img.bottom-(d/(float)max)*img.height();
                p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.3f);p.setColor(Color.rgb(64,92,68));c.drawLine(w*.925f,y,w*.945f,y,p);p.setStyle(Paint.Style.FILL);
                text(c,d+"m",w*.905f,y+5,12.8f,Color.rgb(48,76,54),true,Paint.Align.RIGHT);
            }
            text(c,"TEE 0",w*.885f,img.top+4,5.8f,Color.rgb(175,126,53),true,Paint.Align.CENTER);
        }

        private void drawApprovedActionV1136(Canvas c,RectF r,String label,int bg,int fg){
            softShadow(c,r,20);box(c,r,bg,20);
            if(bg==Color.rgb(255,255,247)){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.2f);p.setColor(Color.rgb(213,217,201));c.drawRoundRect(r,20,20,p);p.setStyle(Paint.Style.FILL);}
            text(c,label,r.centerX(),r.centerY()+5,13.8f,fg,true,Paint.Align.CENTER);
        }

        private void drawApprovedNavV1136(Canvas c,float w,float h){
            RectF bar=new RectF(w*.023f,h*.916f,w*.977f,h*.997f);softShadow(c,bar,28);box(c,bar,Color.rgb(255,255,250),28);
            RectF[] rr={homeBtn,mapTab,prev,scoreTab,next};String[] lab={"홈","코스","입력","카드","요약"};
            for(int i=0;i<5;i++){
                float cx=rr[i].centerX();RectF icon=new RectF(cx-w*.055f,h*.920f,cx+w*.055f,h*.956f);
                box(c,icon,i==1?Color.rgb(235,248,240):Color.rgb(239,247,250),11);
                if(i==1){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.2f);p.setColor(Color.rgb(91,177,112));c.drawRoundRect(icon,11,11,p);p.setStyle(Paint.Style.FILL);}
                drawApprovedNavIconV1136(c,icon,i);
                text(c,lab[i],cx,h*.982f,15.2f,i==1?Color.rgb(46,135,75):INK,true,Paint.Align.CENTER);
            }
            RectF ul=new RectF(mapTab.centerX()-w*.040f,h*.992f,mapTab.centerX()+w*.040f,h*.995f);box(c,ul,Color.rgb(54,145,83),2);
        }

        private void drawApprovedNavIconV1136(Canvas c,RectF r,int i){
            float cx=r.centerX(),cy=r.centerY();
            p.setColor(Color.rgb(105,185,83));c.drawOval(new RectF(r.left+4,r.bottom-12,r.right-4,r.bottom+2),p);
            if(i==0){
                p.setColor(Color.WHITE);c.drawRect(cx-11,cy-5,cx+11,cy+9,p);Path roof=new Path();roof.moveTo(cx-15,cy-5);roof.lineTo(cx,cy-15);roof.lineTo(cx+15,cy-5);roof.close();p.setColor(Color.rgb(235,108,80));c.drawPath(roof,p);p.setColor(Color.rgb(169,112,65));c.drawRect(cx-3,cy+1,cx+4,cy+9,p);
            }else if(i==1){
                p.setColor(Color.rgb(55,124,88));p.setStrokeWidth(2);c.drawLine(cx+2,cy-14,cx+2,cy+7,p);Path f=new Path();f.moveTo(cx+2,cy-14);f.lineTo(cx+16,cy-10);f.lineTo(cx+2,cy-5);f.close();p.setColor(Color.rgb(236,102,86));c.drawPath(f,p);p.setColor(Color.WHITE);c.drawCircle(cx-11,cy+4,4,p);p.setColor(Color.LTGRAY);c.drawCircle(cx-12,cy+3,1,p);
            }else if(i==2){
                p.setColor(Color.WHITE);c.drawRoundRect(new RectF(cx-13,cy-13,cx+9,cy+10),3,3,p);p.setColor(Color.rgb(76,139,157));p.setStrokeWidth(1.5f);for(int k=0;k<3;k++)c.drawLine(cx-8,cy-6+k*6,cx+5,cy-6+k*6,p);p.setColor(Color.rgb(239,151,58));c.drawRect(cx+7,cy-12,cx+11,cy+8,p);
            }else if(i==3){
                p.setColor(Color.WHITE);c.drawRoundRect(new RectF(cx-14,cy-13,cx+14,cy+10),4,4,p);p.setColor(Color.rgb(195,144,192));for(int k=0;k<3;k++){c.drawCircle(cx-8,cy-6+k*6,2,p);c.drawRect(cx-3,cy-8+k*6,cx+9,cy-5+k*6,p);}
            }else{
                p.setColor(Color.rgb(230,180,55));c.drawOval(new RectF(cx-8,cy-12,cx+8,cy+3),p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);c.drawArc(new RectF(cx-16,cy-10,cx-4,cy+3),90,180,false,p);c.drawArc(new RectF(cx+4,cy-10,cx+16,cy+3),-90,180,false,p);p.setStyle(Paint.Style.FILL);c.drawRect(cx-2,cy+2,cx+2,cy+8,p);c.drawRect(cx-8,cy+8,cx+8,cy+11,p);
            }
        }

'''
s=s[:pos]+helpers+s[pos:]

p.write_text(s)
print('applied',MARK)
