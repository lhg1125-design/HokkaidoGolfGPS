from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.13.6 · ROUND LOG' not in s:
    raise SystemExit('v1.13.7 requires V1.13.6 round log')
s=s.replace('V1.13.6 · ROUND LOG','V1.13.7 · PLAY HUD',1)

# PLAY HUD: prioritize glance readability on phone and Flip cover displays.
# Course + variant share one line; H/P duplicate subtitle is removed.
old='''            text(c,"FIELD NAV",m,h*.016f,6.4f,Color.rgb(215,241,222),true);'''
new='''            text(c,"FIELD NAV",m,h*.017f,8.0f,Color.rgb(235,250,239),true);'''
if old not in s: raise SystemExit('FIELD NAV anchor missing')
s=s.replace(old,new,1)

old='''            text(c,ko[selected],m,h*.043f,14.2f,Color.WHITE,true);'''
if old not in s: raise SystemExit('course title anchor missing')
s=s.replace(old,'''            drawPlayTitleV1137(c,m,w,h);''',1)

old='''            String sub=variants[selected][variant]+" · H"+hole+" · P"+par;text(c,sub,m,h*.064f,7.0f,Color.rgb(218,242,222),true);'''
if old not in s: raise SystemExit('duplicate H/P subtitle anchor missing')
s=s.replace(old,'',1)

old='''            pill(c,new RectF(w*.755f,h*.009f,w*.94f,h*.034f),Color.rgb(235,247,229),gpsStatusShort(),gpsColor(),5.7f);'''
if old not in s: raise SystemExit('GPS pill anchor missing')
s=s.replace(old,'',1)
old='''            pill(c,new RectF(w*.715f,h*.038f,w*.94f,h*.064f),fieldReadyBgV1114(),fieldReadyLabelV1114(),Color.WHITE,5.6f);'''
if old not in s: raise SystemExit('CAL pill anchor missing')
s=s.replace(old,'''            drawPlayStatusV1137(c,w,h);''',1)

# Add large HOLE number to every primary metric configuration.
old='''metric(c,"TOTAL",totalM+"m",w*.25f,h*.083f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"DIST",(nr>=0?nr:totalM)+"m",w*.50f,h*.083f);metric(c,"PAR",""+par,w*.75f,h*.083f);'''
new='''metric(c,"HOLE","H"+hole,w*.18f,h*.083f);metric(c,"TOTAL",totalM+"m",w*.39f,h*.083f);metric(c,nr>=0?(navEstimatedV1113()?"EST":"REMAIN"):"DIST",(nr>=0?nr:totalM)+"m",w*.61f,h*.083f);metric(c,"PAR",""+par,w*.82f,h*.083f);'''
if old not in s: raise SystemExit('JP metrics anchor missing')
s=s.replace(old,new,1)

old='''metric(c,"TOTAL",totalM+"m",w*.25f,h*.083f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"DIST",nr>=0?(nr+"m"):(totalM+"m"),w*.50f,h*.083f);metric(c,"PAR",""+par,w*.75f,h*.083f);'''
new='''metric(c,"HOLE","H"+hole,w*.18f,h*.083f);metric(c,"TOTAL",totalM+"m",w*.39f,h*.083f);metric(c,nr>=0?(navEstimatedV1113()?"EST":"REMAIN"):"DIST",nr>=0?(nr+"m"):(totalM+"m"),w*.61f,h*.083f);metric(c,"PAR",""+par,w*.82f,h*.083f);'''
if old not in s: raise SystemExit('Royal metrics anchor missing')
s=s.replace(old,new,1)

old='''metric(c,"TOTAL",totalM>0?totalM+"m":"--",w*.25f,h*.083f);metric(c,"PAR",""+par,w*.50f,h*.083f);metric(c,"CAL",totalM>0?"OK":"NEED",w*.75f,h*.083f);'''
new='''metric(c,"HOLE","H"+hole,w*.18f,h*.083f);metric(c,"TOTAL",totalM>0?totalM+"m":"--",w*.39f,h*.083f);metric(c,"PAR",""+par,w*.61f,h*.083f);metric(c,"CAL",totalM>0?"OK":"NEED",w*.82f,h*.083f);'''
if old not in s: raise SystemExit('field metrics anchor missing')
s=s.replace(old,new,1)

old='''metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.083f);metric(c,"CENTER",ds.center+"m",w*.50f,h*.083f);metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.083f);'''
new='''metric(c,"H"+hole+" · P"+par,"LIVE",w*.18f,h*.083f);metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.39f,h*.083f);metric(c,"CENTER",ds.center+"m",w*.61f,h*.083f);metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.82f,h*.083f);'''
if old not in s: raise SystemExit('calibrated metrics anchor missing')
s=s.replace(old,new,1)

# Increase the common metric typography for glance readability.
old='''        private void metric(Canvas c,String lab,String val,float x,float y){text(c,lab,x,y,9,Color.rgb(212,237,219),true,Paint.Align.CENTER);text(c,val,x,y+getHeight()*.040f,19,Color.WHITE,true,Paint.Align.CENTER);}'''
new='''        private void metric(Canvas c,String lab,String val,float x,float y){text(c,lab,x,y,10.6f,Color.rgb(228,246,231),true,Paint.Align.CENTER);float z=lab.equals("HOLE")||lab.startsWith("H")?24.5f:22.0f;text(c,val,x,y+getHeight()*.039f,z,Color.WHITE,true,Paint.Align.CENTER);}'''
if old not in s: raise SystemExit('metric helper anchor missing')
s=s.replace(old,new,1)

# Small operational labels on the live screen also get a readable floor.
s=s.replace('textFit(c,naepoRealMapLabelV1132(),ng.left+7,ng.centerY()+3,ng.right-7,5.8f,nc,true);','textFit(c,naepoRealMapLabelV1132(),ng.left+7,ng.centerY()+4,ng.right-7,7.0f,nc,true);')
s=s.replace('textFit(c,liveGeoChipV1135(),chip.left+7,chip.centerY()+3,chip.right-7,5.2f,liveGeoColorV1135(),true);','textFit(c,liveGeoChipV1135(),chip.left+7,chip.centerY()+4,chip.right-7,6.8f,liveGeoColorV1135(),true);')
s=s.replace('textFit(c,srcLabel+" · TEE → GREEN",src.left+8,src.centerY()+2,src.right-8,5.7f,GREEN,true);','textFit(c,srcLabel+" · TEE → GREEN",src.left+8,src.centerY()+3,src.right-8,6.8f,GREEN,true);')
s=s.replace('text(c,"공략",strategy.left+10,h*.870f,6.0f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+42,h*.870f,strategy.right-8,5.8f,INK,true);','text(c,"공략",strategy.left+10,h*.870f,7.0f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+48,h*.870f,strategy.right-8,6.7f,INK,true);')

anchor='        private String fieldReadyLabelV1114(){'
pos=s.find(anchor)
if pos<0: raise SystemExit('helper insertion anchor missing')
helpers=r'''        private void drawPlayTitleV1137(Canvas c,float m,float w,float h){
            String title=ko[selected],course=variants[selected][variant];
            float z=17.2f,sd=getResources().getDisplayMetrics().scaledDensity;
            p.setTypeface(conceptTypefaceV1130(title,true));p.setTextSize(z*sd);
            while(p.measureText(title)>w*.41f && z>13f){z-=.25f;p.setTextSize(z*sd);}
            text(c,title,m,h*.049f,z,Color.WHITE,true);
            p.setTypeface(conceptTypefaceV1130(title,true));p.setTextSize(z*sd);float tw=p.measureText(title);
            float x=Math.min(m+tw+10f,w*.47f);float cz=z*.80f;
            textFit(c,course,x,h*.049f,w*.695f,cz,Color.rgb(235,250,239),true);
        }
        private void drawGpsGlyphV1137(Canvas c,float x,float y,int col){
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.6f);p.setColor(col);c.drawCircle(x,y-2,5.2f,p);c.drawLine(x,y+3,x,y+8,p);p.setStyle(Paint.Style.FILL);p.setColor(col);c.drawCircle(x,y-2,1.8f,p);
        }
        private void drawCalGlyphV1137(Canvas c,float x,float y,int col){
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.4f);p.setColor(col);c.drawCircle(x,y,6f,p);c.drawCircle(x,y,2.4f,p);c.drawLine(x-8,y,x-5,y,p);c.drawLine(x+5,y,x+8,y,p);p.setStyle(Paint.Style.FILL);
        }
        private void drawPlayStatusV1137(Canvas c,float w,float h){
            RectF gpsR=new RectF(w*.715f,h*.007f,w*.955f,h*.034f);int gc=gpsColor();box(c,gpsR,Color.rgb(239,249,226),gpsR.height()/2);drawGpsGlyphV1137(c,gpsR.left+15,gpsR.centerY(),gc);textFit(c,gpsStatusShort(),gpsR.left+29,gpsR.centerY()+4,gpsR.right-7,7.5f,gc,true);
            RectF calR=new RectF(w*.695f,h*.039f,w*.955f,h*.067f);int cc=liveGeoColorV1135();box(c,calR,fieldReadyBgV1114(),calR.height()/2);drawCalGlyphV1137(c,calR.left+15,calR.centerY(),Color.WHITE);textFit(c,fieldReadyLabelV1114(),calR.left+29,calR.centerY()+4,calR.right-7,7.5f,Color.WHITE,true);
        }

'''
s=s[:pos]+helpers+s[pos:]

p.write_text(s)
print('applied V1.13.7 PLAY HUD: large hole ID + title/course merge + icon status + cover-display legibility')
