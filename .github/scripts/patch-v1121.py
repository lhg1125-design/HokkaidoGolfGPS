from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.12.0 · FIELD BETA KIT' not in s:
    raise SystemExit('v1.12.1 requires v1.12.0 field beta kit')
s=s.replace('V1.12.0 · FIELD BETA KIT','V1.12.1 · YARDAGE FOCUS',1)

# -----------------------------------------------------------------------------
# YARDAGE-FIRST SCREEN
# The map + YOU marker is the primary UI. Compress the header, remove redundant
# status cards and move secondary controls into slim bars below the map.
# -----------------------------------------------------------------------------
repls={
'''            RectF head=new RectF(0,0,w,h*.145f);gradient(c,head,DEEP,GREEN,0);''':
'''            RectF head=new RectF(0,0,w,h*.086f);gradient(c,head,DEEP,GREEN,0);''',
'''            text(c,"FIELD NAV · FULL HOLE",m,h*.035f,8.5f,Color.rgb(215,241,222),true);''':
'''            text(c,"FIELD NAV · FULL HOLE",m,h*.020f,7.2f,Color.rgb(215,241,222),true);''',
'''            text(c,ko[selected],m,h*.080f,21.5f,Color.WHITE,true);''':
'''            text(c,ko[selected],m,h*.051f,15.8f,Color.WHITE,true);''',
'''            String sub=variants[selected][variant]+" · H"+hole+" · PAR "+par;text(c,sub,m,h*.119f,10.5f,Color.rgb(218,242,222),true);''':
'''            String sub=variants[selected][variant]+" · H"+hole+" · PAR "+par;text(c,sub,m,h*.077f,8.0f,Color.rgb(218,242,222),true);''',
'''            pill(c,new RectF(w*.735f,h*.027f,w*.94f,h*.066f),Color.rgb(235,247,229),gpsStatusShort(),gpsColor(),7.2f);''':
'''            pill(c,new RectF(w*.745f,h*.013f,w*.94f,h*.043f),Color.rgb(235,247,229),gpsStatusShort(),gpsColor(),6.3f);''',
'''            pill(c,new RectF(w*.69f,h*.086f,w*.94f,h*.128f),fieldReadyBgV1114(),fieldReadyLabelV1114(),Color.WHITE,7.0f);''':
'''            pill(c,new RectF(w*.70f,h*.048f,w*.94f,h*.079f),fieldReadyBgV1114(),fieldReadyLabelV1114(),Color.WHITE,6.2f);''',
'''            RectF range=new RectF(m,h*.158f,w-m,h*.235f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),24);sheen(c,range,24);''':
'''            RectF range=new RectF(m,h*.092f,w-m,h*.146f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),20);sheen(c,range,20);''',
'''metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.175f);metric(c,"CENTER",ds.center+"m",w*.50f,h*.175f);metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.175f);''':
'''metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.101f);metric(c,"CENTER",ds.center+"m",w*.50f,h*.101f);metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.101f);''',
'''metric(c,"REGULAR",officialYardsV190()+"Y",w*.25f,h*.175f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"METER",(nr>=0?nr:totalM)+"m",w*.50f,h*.175f);metric(c,"PAR",""+par,w*.75f,h*.175f);''':
'''metric(c,"REGULAR",officialYardsV190()+"Y",w*.25f,h*.101f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"METER",(nr>=0?nr:totalM)+"m",w*.50f,h*.101f);metric(c,"PAR",""+par,w*.75f,h*.101f);''',
'''metric(c,"WHITE",totalM+"m",w*.25f,h*.175f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"PAR",nr>=0?(nr+"m"):(""+par),w*.50f,h*.175f);metric(c,"HOLE","H"+hole,w*.75f,h*.175f);''':
'''metric(c,"WHITE",totalM+"m",w*.25f,h*.101f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"PAR",nr>=0?(nr+"m"):(""+par),w*.50f,h*.101f);metric(c,"HOLE","H"+hole,w*.75f,h*.101f);''',
'''metric(c,"FIELD",totalM>0?totalM+"m":"--",w*.25f,h*.175f);metric(c,"PAR",""+par,w*.50f,h*.175f);metric(c,"CAL",totalM>0?"OK":"NEED",w*.75f,h*.175f);''':
'''metric(c,"FIELD",totalM>0?totalM+"m":"--",w*.25f,h*.101f);metric(c,"PAR",""+par,w*.50f,h*.101f);metric(c,"CAL",totalM>0?"OK":"NEED",w*.75f,h*.101f);''',
'''            pill(c,new RectF(m,h*.243f,w*.29f,h*.272f),gpsBg(),gpsStatusShort(),gpsColor(),6.8f);\n            pill(c,new RectF(w*.31f,h*.243f,w*.70f,h*.272f),CARD,verifiedDistanceLabelV190(),yardageSourceColorV190(),6.8f);\n            autoBtn.set(w*.72f,h*.243f,w-m,h*.272f);pill(c,autoBtn,autoHole?Color.rgb(229,244,218):CARD,autoHole?"AUTO ON":"AUTO OFF",autoHole?GREEN:Color.GRAY,6.7f);''':
'''            autoBtn.set(-1,-1,-1,-1);''',
'''            courseRect.set(m,h*.300f,w-m,h*.650f);drawFullHoleYardageV1102(c,courseRect,par,totalM);drawHolePager(c,h*.286f);''':
'''            courseRect.set(m,h*.153f,w-m,h*.795f);drawFullHoleYardageV1102(c,courseRect,par,totalM);drawHolePager(c,h*.160f);''',
'''            drawHazardBarV182(c,h*.658f,h*.694f);''':
'''            drawHazardBarV182(c,h*.801f,h*.824f);''',
'''            RectF strategy=new RectF(m,h*.701f,w-m,h*.747f);''':
'''            RectF strategy=new RectF(m,h*.829f,w-m,h*.856f);''',
'''            text(c,"공략 포인트",strategy.left+14,h*.718f,8.0f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+14,h*.739f,strategy.right-14,7.4f,INK,true);''':
'''            text(c,"공략",strategy.left+12,h*.840f,6.7f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+48,h*.840f,strategy.right-10,6.5f,INK,true);''',
'''            greenSave.set(m,h*.754f,w*.38f,h*.800f);teeSave.set(w*.405f,h*.754f,w*.65f,h*.800f);mapLaunch.set(w*.675f,h*.754f,w-m,h*.800f);''':
'''            greenSave.set(m,h*.861f,w*.38f,h*.897f);teeSave.set(w*.405f,h*.861f,w*.65f,h*.897f);mapLaunch.set(w*.675f,h*.861f,w-m,h*.897f);'''
}
for a,b in repls.items():
    if a not in s:
        raise SystemExit('v1.12.1 yardage-focus anchor missing: '+a[:70])
    s=s.replace(a,b,1)

# Remove score-entry furniture from the yardage screen. Scoring remains fully
# available on the dedicated score tab, giving the map almost the whole screen.
old='''            drawPlayerTabs(c,h*.811f);int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);\n            RectF quick=new RectF(m,h*.848f,w-m,h*.913f);softShadow(c,quick,20);box(c,quick,CARD,20);\n            text(c,"타수",m+16,h*.869f,8.0f,Color.GRAY,true);goldText(c,""+stroke,w*.28f,h*.882f,21.0f,INK);\n            minus.set(m+68,h*.857f,m+128,h*.904f);plus.set(w*.355f,h*.857f,w*.435f,h*.904f);goldButton(c,minus,SOFT,"−",INK,17f);goldButton(c,plus,Color.rgb(229,244,218),"+",GREEN,17f);\n            text(c,"퍼트",w*.52f,h*.869f,8.0f,Color.GRAY,true);goldText(c,""+putt,w*.69f,h*.882f,21.0f,INK);\n            pm.set(w*.535f,h*.857f,w*.605f,h*.904f);pp.set(w*.82f,h*.857f,w*.90f,h*.904f);goldButton(c,pm,SOFT,"−",INK,17f);goldButton(c,pp,Color.rgb(226,245,250),"+",BLUE,17f);'''
new='''            for(RectF tab:playerTabs)tab.set(-1,-1,-1,-1);minus.set(-1,-1,-1,-1);plus.set(-1,-1,-1,-1);pm.set(-1,-1,-1,-1);pp.set(-1,-1,-1,-1);'''
if old not in s:
    raise SystemExit('v1.12.1 score furniture anchor missing')
s=s.replace(old,new,1)

# Give the actual hole art more of its card by shrinking its own title/source chrome.
inner={
'''            RectF title=new RectF(r.left+12,r.top+9,r.right-12,r.top+48);box(c,title,Color.argb(244,255,255,255),18);''':
'''            RectF title=new RectF(r.left+12,r.top+6,r.right-12,r.top+34);box(c,title,Color.argb(238,255,255,255),14);''',
'''            textFit(c,"H"+hole+" · PAR "+par+" · "+verifiedDistanceLabelV190(),title.left+12,title.centerY()+3,title.right-12,9.5f,DEEP,true);''':
'''            textFit(c,"H"+hole+" · P"+par+" · "+verifiedDistanceLabelV190(),title.left+10,title.centerY()+3,title.right-10,8.0f,DEEP,true);''',
'''            RectF stage=new RectF(r.left+10,r.top+54,r.right-10,r.bottom-50);''':
'''            RectF stage=new RectF(r.left+8,r.top+38,r.right-8,r.bottom-28);''',
'''            RectF src=new RectF(r.left+12,r.bottom-42,r.right-12,r.bottom-9);box(c,src,Color.argb(242,255,255,255),16);''':
'''            RectF src=new RectF(r.left+12,r.bottom-23,r.right-12,r.bottom-5);box(c,src,Color.argb(230,255,255,255),10);''',
'''            textFit(c,srcLabel+" · TEE → GREEN · "+yardageSourceV190(),src.left+10,src.centerY()+3,src.right-10,7.2f,GREEN,true);''':
'''            textFit(c,srcLabel+" · TEE → GREEN",src.left+8,src.centerY()+2,src.right-8,5.7f,GREEN,true);'''
}
for a,b in inner.items():
    if a not in s:
        raise SystemExit('v1.12.1 inner-map anchor missing: '+a[:70])
    s=s.replace(a,b,1)

# YOU must visually dominate the map, not the surrounding cards.
marker_repls={
'''            p.setColor(Color.argb(245,255,255,255));c.drawCircle(x,y,13,p);\n            p.setColor(CORAL);c.drawCircle(x,y,9,p);\n            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.0f);p.setColor(Color.argb(180,255,126,92));c.drawCircle(x,y,15,p);p.setStyle(Paint.Style.FILL);''':
'''            p.setColor(Color.argb(248,255,255,255));c.drawCircle(x,y,17,p);\n            p.setColor(CORAL);c.drawCircle(x,y,12,p);\n            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.6f);p.setColor(Color.argb(205,255,126,92));c.drawCircle(x,y,21,p);p.setStyle(Paint.Style.FILL);''',
'''            RectF you=new RectF(stage.right-116,y-14,stage.right-31,y+14);''':
'''            RectF you=new RectF(stage.right-150,y-18,stage.right-34,y+18);''',
'''            textFit(c,"YOU · "+Math.round(q*100f)+"%",you.left+8,you.centerY()+3,you.right-8,6.8f,CORAL,true);''':
'''            textFit(c,"YOU · "+Math.round(q*100f)+"%",you.left+9,you.centerY()+3,you.right-9,8.2f,CORAL,true);''',
'''            RectF live=new RectF(stage.right-191,stage.top+8,stage.right-8,stage.top+35);''':
'''            RectF live=new RectF(stage.right-175,stage.top+7,stage.right-8,stage.top+51);''',
'''            textFit(c,msg,live.left+8,live.centerY()+3,live.right-8,6.4f,DEEP,true);''':
'''            text(c,remain>=0?remain+"m":"--",live.centerX(),live.top+22,15.5f,DEEP,true,Paint.Align.CENTER);\n            text(c,previewMode?"SIM REMAIN":(navEstimatedV1113()?"EST REMAIN":"TO GREEN"),live.centerX(),live.bottom-7,6.1f,GREEN,true,Paint.Align.CENTER);'''
}
for a,b in marker_repls.items():
    if a not in s:
        raise SystemExit('v1.12.1 YOU marker anchor missing: '+a[:70])
    s=s.replace(a,b,1)

p.write_text(s)
print('applied v1.12.1 yardage-first layout: 64% map + dominant YOU/remaining distance')
