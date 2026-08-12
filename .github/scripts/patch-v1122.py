from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.12.1 · YARDAGE FOCUS' not in s:
    raise SystemExit('v1.12.2 requires v1.12.1 yardage focus')
s=s.replace('V1.12.1 · YARDAGE FOCUS','V1.12.2 · MAP PIN FOCUS',1)

# -----------------------------------------------------------------------------
# 1) METERS ONLY on every live-yardage surface.
# Keep published yard arrays internally for source fidelity, but never expose Y
# on the field screen. All operational distance UI is meters.
# -----------------------------------------------------------------------------
old='''        private String verifiedDistanceLabelV190(){
            if(selected<=2){int y=officialYardsV190();return "REG "+y+"Y · "+Math.round(y*.9144f)+"m";}
            if(selected==4)return "WHITE "+royalWhiteMetersV190()+"m";
            int m=fieldGpsMetersV190();return m>0?("FIELD GPS "+m+"m"):"FIELD CAL REQUIRED";
        }'''
new='''        private String verifiedDistanceLabelV190(){
            if(selected<=2)return "TOTAL "+Math.round(officialYardsV190()*.9144f)+"m";
            if(selected==4)return "TOTAL "+royalWhiteMetersV190()+"m";
            int m=fieldGpsMetersV190();return m>0?("FIELD GPS "+m+"m"):"FIELD CAL REQUIRED";
        }'''
if old not in s:
    raise SystemExit('v1.12.2 verified distance label anchor missing')
s=s.replace(old,new,1)

old='''metric(c,"REGULAR",officialYardsV190()+"Y",w*.25f,h*.101f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"METER",(nr>=0?nr:totalM)+"m",w*.50f,h*.101f);metric(c,"PAR",""+par,w*.75f,h*.101f);'''
new='''metric(c,"TOTAL",totalM+"m",w*.25f,h*.083f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"DIST",(nr>=0?nr:totalM)+"m",w*.50f,h*.083f);metric(c,"PAR",""+par,w*.75f,h*.083f);'''
if old not in s:
    raise SystemExit('v1.12.2 Japan meter metric anchor missing')
s=s.replace(old,new,1)

old='''metric(c,"WHITE",totalM+"m",w*.25f,h*.101f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"PAR",nr>=0?(nr+"m"):(""+par),w*.50f,h*.101f);metric(c,"HOLE","H"+hole,w*.75f,h*.101f);'''
new='''metric(c,"TOTAL",totalM+"m",w*.25f,h*.083f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"DIST",nr>=0?(nr+"m"):(totalM+"m"),w*.50f,h*.083f);metric(c,"PAR",""+par,w*.75f,h*.083f);'''
if old not in s:
    raise SystemExit('v1.12.2 Royal meter metric anchor missing')
s=s.replace(old,new,1)

old='''metric(c,"FIELD",totalM>0?totalM+"m":"--",w*.25f,h*.101f);metric(c,"PAR",""+par,w*.50f,h*.101f);metric(c,"CAL",totalM>0?"OK":"NEED",w*.75f,h*.101f);'''
new='''metric(c,"TOTAL",totalM>0?totalM+"m":"--",w*.25f,h*.083f);metric(c,"PAR",""+par,w*.50f,h*.083f);metric(c,"CAL",totalM>0?"OK":"NEED",w*.75f,h*.083f);'''
if old not in s:
    raise SystemExit('v1.12.2 field meter metric anchor missing')
s=s.replace(old,new,1)

old='''metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.101f);metric(c,"CENTER",ds.center+"m",w*.50f,h*.101f);metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.101f);'''
new='''metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.083f);metric(c,"CENTER",ds.center+"m",w*.50f,h*.083f);metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.083f);'''
if old not in s:
    raise SystemExit('v1.12.2 calibrated meter metric anchor missing')
s=s.replace(old,new,1)

# -----------------------------------------------------------------------------
# 2) Compress top chrome and remove duplicate map pager arrows.
# One bottom navigation row remains; the second arrow layer on top of the map is
# removed. The recovered area is given back to the full-hole image.
# -----------------------------------------------------------------------------
repls={
'''            RectF head=new RectF(0,0,w,h*.086f);gradient(c,head,DEEP,GREEN,0);''':
'''            RectF head=new RectF(0,0,w,h*.070f);gradient(c,head,DEEP,GREEN,0);''',
'''            text(c,"FIELD NAV · FULL HOLE",m,h*.020f,7.2f,Color.rgb(215,241,222),true);''':
'''            text(c,"FIELD NAV",m,h*.016f,6.4f,Color.rgb(215,241,222),true);''',
'''            text(c,ko[selected],m,h*.051f,15.8f,Color.WHITE,true);''':
'''            text(c,ko[selected],m,h*.043f,14.2f,Color.WHITE,true);''',
'''            String sub=variants[selected][variant]+" · H"+hole+" · PAR "+par;text(c,sub,m,h*.077f,8.0f,Color.rgb(218,242,222),true);''':
'''            String sub=variants[selected][variant]+" · H"+hole+" · P"+par;text(c,sub,m,h*.064f,7.0f,Color.rgb(218,242,222),true);''',
'''            pill(c,new RectF(w*.745f,h*.013f,w*.94f,h*.043f),Color.rgb(235,247,229),gpsStatusShort(),gpsColor(),6.3f);''':
'''            pill(c,new RectF(w*.755f,h*.009f,w*.94f,h*.034f),Color.rgb(235,247,229),gpsStatusShort(),gpsColor(),5.7f);''',
'''            pill(c,new RectF(w*.70f,h*.048f,w*.94f,h*.079f),fieldReadyBgV1114(),fieldReadyLabelV1114(),Color.WHITE,6.2f);''':
'''            pill(c,new RectF(w*.715f,h*.038f,w*.94f,h*.064f),fieldReadyBgV1114(),fieldReadyLabelV1114(),Color.WHITE,5.6f);''',
'''            RectF range=new RectF(m,h*.092f,w-m,h*.146f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),20);sheen(c,range,20);''':
'''            RectF range=new RectF(m,h*.073f,w-m,h*.126f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),18);sheen(c,range,18);''',
'''            courseRect.set(m,h*.153f,w-m,h*.795f);drawFullHoleYardageV1102(c,courseRect,par,totalM);drawHolePager(c,h*.160f);''':
'''            courseRect.set(m,h*.132f,w-m,h*.852f);drawFullHoleYardageV1102(c,courseRect,par,totalM);''',
'''            drawHazardBarV182(c,h*.801f,h*.824f);''':
'''            // Official full-hole art already shows hazards; redundant hazard strip removed.''',
'''            RectF strategy=new RectF(m,h*.829f,w-m,h*.856f);softShadow(c,strategy,18);box(c,strategy,CARD,18);''':
'''            RectF strategy=new RectF(m,h*.858f,w-m,h*.881f);softShadow(c,strategy,12);box(c,strategy,CARD,12);''',
'''            text(c,"공략",strategy.left+12,h*.840f,6.7f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+48,h*.840f,strategy.right-10,6.5f,INK,true);''':
'''            text(c,"공략",strategy.left+10,h*.870f,6.0f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+42,h*.870f,strategy.right-8,5.8f,INK,true);''',
'''            greenSave.set(m,h*.861f,w*.38f,h*.897f);teeSave.set(w*.405f,h*.861f,w*.65f,h*.897f);mapLaunch.set(w*.675f,h*.861f,w-m,h*.897f);''':
'''            greenSave.set(m,h*.886f,w*.38f,h*.916f);teeSave.set(w*.405f,h*.886f,w*.65f,h*.916f);mapLaunch.set(w*.675f,h*.886f,w-m,h*.916f);'''
}
for a,b in repls.items():
    if a not in s:
        raise SystemExit('v1.12.2 layout anchor missing: '+a[:72])
    s=s.replace(a,b,1)

# -----------------------------------------------------------------------------
# 3) DIRECT POSITION PIN.
# Delete the separate GPS axis / YOU legend. Navigation progress is now drawn as
# a pulsing orange point directly over the hole image. Remaining distance stays
# in the single top metric row, avoiding duplicate labels.
# -----------------------------------------------------------------------------
a=s.find('        private void drawFieldNavV1110(Canvas c,RectF stage,int totalM){')
b=s.find('        private String fieldReadyLabelV1114(){',a)
if a<0 or b<0:
    raise SystemExit('v1.12.2 field-nav method boundary missing')
new_method=r'''        private void drawFieldNavV1110(Canvas c,RectF stage,int totalM){
            if(!navReadyV1110()){
                RectF wait=new RectF(stage.right-112,stage.top+7,stage.right-8,stage.top+29);
                box(c,wait,Color.argb(224,255,247,218),11);
                textFit(c,"TEE 저장",wait.left+8,wait.centerY()+3,wait.right-8,5.6f,AMBER,true);
                return;
            }
            float q=navProgressV1110();
            if(q<0)return;
            float top=stage.top+28f,bottom=stage.bottom-18f;
            float y=bottom-q*(bottom-top);
            float x=stage.centerX();
            float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/260.0));
            int orange=Color.rgb(255,132,35);

            // Soft animated halo -> white separator -> solid orange core.
            p.setColor(Color.argb((int)(32+42*pulse),255,132,35));
            c.drawCircle(x,y,24f+6f*pulse,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4.0f);p.setColor(Color.argb(245,255,255,255));
            c.drawCircle(x,y,16f,p);
            p.setStyle(Paint.Style.FILL);p.setColor(orange);c.drawCircle(x,y,12f,p);
            p.setColor(Color.argb(235,255,235,220));c.drawCircle(x,y,3.4f,p);
        }

'''
s=s[:a]+new_method+s[b:]

# Simulator: replace the previous narrow right-side axis touch block by locating
# its header and closing brace, so wording/indent changes in older patches do
# not break the update.
hdr='if(screen==1 && previewMode && courseRect.contains(x,y) && x>courseRect.right-92f){'
ha=s.find(hdr)
if ha<0:
    raise SystemExit('v1.12.2 SIM axis header missing')
line_start=s.rfind('\n',0,ha)+1
indent=s[line_start:ha]
close='\n'+indent+'}'
hb=s.find(close,ha)
if hb<0:
    raise SystemExit('v1.12.2 SIM axis block end missing')
hb += len(close)
new_touch=(
    indent+'if(screen==1 && previewMode && courseRect.contains(x,y)){\n'
    +indent+'    float nt=courseRect.top+42f,nb=courseRect.bottom-30f;\n'
    +indent+'    simProgressV1112=Math.max(0f,Math.min(1f,(nb-y)/Math.max(1f,nb-nt)));\n'
    +indent+'    showToast("SIM · "+Math.round(simProgressV1112*100f)+"%");invalidate();return true;\n'
    +indent+'}'
)
s=s[:line_start]+new_touch+s[hb:]

p.write_text(s)
print('applied v1.12.2: meters-only + direct glowing orange map pin + 72% full-hole map')
