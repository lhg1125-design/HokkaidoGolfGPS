from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.13.7 · PLAY HUD' not in s:
    raise SystemExit('v1.13.8 requires V1.13.7 play HUD')
s=s.replace('V1.13.7 · PLAY HUD','V1.13.8 · COVER HUD',1)

# Cover-display mode: near-square external screens need more vertical breathing
# room for title/status/HUD. Tall phones keep the max-map layout unchanged.
old='''            RectF head=new RectF(0,0,w,h*.070f);gradient(c,head,Color.rgb(48,164,229),Color.rgb(91,190,228),0);'''
new='''            RectF head=new RectF(0,0,w,h*(coverHudV1138()? .105f:.070f));gradient(c,head,Color.rgb(48,164,229),Color.rgb(91,190,228),0);'''
if old not in s: raise SystemExit('head anchor missing')
s=s.replace(old,new,1)

old='''            text(c,"FIELD NAV",m,h*.017f,8.0f,Color.rgb(235,250,239),true);'''
new='''            text(c,"FIELD NAV",m,h*(coverHudV1138()? .024f:.017f),coverHudV1138()?8.8f:8.0f,Color.rgb(235,250,239),true);'''
if old not in s: raise SystemExit('field nav label anchor missing')
s=s.replace(old,new,1)

old='''            RectF range=new RectF(m,h*.073f,w-m,h*.126f);gradient(c,range,Color.rgb(34,126,72),Color.rgb(87,159,98),18);sheen(c,range,18);'''
new='''            RectF range=new RectF(m,h*(coverHudV1138()? .108f:.073f),w-m,h*(coverHudV1138()? .185f:.126f));gradient(c,range,Color.rgb(34,126,72),Color.rgb(87,159,98),18);sheen(c,range,18);'''
if old not in s: raise SystemExit('range anchor missing')
s=s.replace(old,new,1)

s=s.replace('h*.083f','metricYV1138(h)')

old='''            courseRect.set(m,h*.132f,w-m,h*.852f);drawFullHoleYardageV1102(c,courseRect,par,totalM);'''
new='''            courseRect.set(m,h*(coverHudV1138()? .191f:.132f),w-m,h*.852f);drawFullHoleYardageV1102(c,courseRect,par,totalM);'''
if old not in s: raise SystemExit('course rect anchor missing')
s=s.replace(old,new,1)

old='''metric(c,"H"+hole+" · P"+par,"LIVE",w*.18f,metricYV1138(h));metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.39f,metricYV1138(h));metric(c,"CENTER",ds.center+"m",w*.61f,metricYV1138(h));metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.82f,metricYV1138(h));'''
new='''metric(c,"PAR "+par,"H"+hole,w*.18f,metricYV1138(h));metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.39f,metricYV1138(h));metric(c,"CENTER",ds.center+"m",w*.61f,metricYV1138(h));metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.82f,metricYV1138(h));'''
if old not in s: raise SystemExit('LIVE metric anchor missing')
s=s.replace(old,new,1)

old='''        private void metric(Canvas c,String lab,String val,float x,float y){text(c,lab,x,y,10.6f,Color.rgb(228,246,231),true,Paint.Align.CENTER);float z=lab.equals("HOLE")||lab.startsWith("H")?24.5f:22.0f;text(c,val,x,y+getHeight()*.039f,z,Color.WHITE,true,Paint.Align.CENTER);}'''
new='''        private void metric(Canvas c,String lab,String val,float x,float y){float lz=coverHudV1138()?11.2f:10.6f;text(c,lab,x,y,lz,Color.rgb(228,246,231),true,Paint.Align.CENTER);float z=(lab.equals("HOLE")||val.startsWith("H"))?(coverHudV1138()?26.5f:24.5f):(coverHudV1138()?23.0f:22.0f);text(c,val,x,y+getHeight()*(coverHudV1138()? .041f:.039f),z,Color.WHITE,true,Paint.Align.CENTER);}'''
if old not in s: raise SystemExit('metric helper anchor missing')
s=s.replace(old,new,1)

old='''            text(c,title,m,h*.049f,z,Color.WHITE,true);'''
new='''            float ty=h*(coverHudV1138()? .073f:.049f);text(c,title,m,ty,z,Color.WHITE,true);'''
if old not in s: raise SystemExit('title y anchor missing')
s=s.replace(old,new,1)
old='''            textFit(c,course,x,h*.049f,w*.695f,cz,Color.rgb(235,250,239),true);'''
new='''            textFit(c,course,x,ty,w*.695f,cz,Color.rgb(235,250,239),true);'''
if old not in s: raise SystemExit('course y anchor missing')
s=s.replace(old,new,1)

old='''            RectF gpsR=new RectF(w*.715f,h*.007f,w*.955f,h*.034f);int gc=gpsColor();box(c,gpsR,Color.rgb(239,249,226),gpsR.height()/2);drawGpsGlyphV1137(c,gpsR.left+15,gpsR.centerY(),gc);textFit(c,gpsStatusShort(),gpsR.left+29,gpsR.centerY()+4,gpsR.right-7,7.5f,gc,true);\n            RectF calR=new RectF(w*.695f,h*.039f,w*.955f,h*.067f);int cc=liveGeoColorV1135();box(c,calR,fieldReadyBgV1114(),calR.height()/2);drawCalGlyphV1137(c,calR.left+15,calR.centerY(),Color.WHITE);textFit(c,fieldReadyLabelV1114(),calR.left+29,calR.centerY()+4,calR.right-7,7.5f,Color.WHITE,true);'''
new='''            RectF gpsR=new RectF(w*.715f,h*(coverHudV1138()? .010f:.007f),w*.955f,h*(coverHudV1138()? .047f:.034f));int gc=gpsColor();box(c,gpsR,Color.rgb(239,249,226),gpsR.height()/2);drawGpsGlyphV1137(c,gpsR.left+15,gpsR.centerY(),gc);textFit(c,gpsStatusShort(),gpsR.left+29,gpsR.centerY()+4,gpsR.right-7,coverHudV1138()?8.4f:7.5f,gc,true);\n            RectF calR=new RectF(w*.695f,h*(coverHudV1138()? .055f:.039f),w*.955f,h*(coverHudV1138()? .098f:.067f));int cc=liveGeoColorV1135();box(c,calR,fieldReadyBgV1114(),calR.height()/2);drawCalGlyphV1137(c,calR.left+15,calR.centerY(),Color.WHITE);textFit(c,fieldReadyLabelV1114(),calR.left+29,calR.centerY()+4,calR.right-7,coverHudV1138()?8.4f:7.5f,Color.WHITE,true);'''
if old not in s: raise SystemExit('status position anchor missing')
s=s.replace(old,new,1)

anchor='        private void drawPlayTitleV1137(Canvas c,float m,float w,float h){'
pos=s.find(anchor)
if pos<0: raise SystemExit('cover helper anchor missing')
helpers='''        private boolean coverHudV1138(){return getHeight()<getWidth()*1.35f;}\n        private float metricYV1138(float h){return h*(coverHudV1138()? .129f:.083f);}\n'''
s=s[:pos]+helpers+s[pos:]

p.write_text(s)
print('applied V1.13.8 COVER HUD: responsive near-square spacing + dominant H# in every live state')

# Final visual layer: approved storybook UI, imported as normal modules.
import storybook_v1139
import storybook_v1139_fix

# Keep the legacy gate token while also exposing the approved master marker.
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.14.0 · STORYBOOK MASTER' in s and 'V1.13.8 · COVER HUD' not in s:
    s=s.replace('V1.14.0 · STORYBOOK MASTER','V1.13.8 · COVER HUD / V1.14.0 · STORYBOOK MASTER',1)
p.write_text(s)

# Last runtime route fix: the app actually draws scoreInput(), not score().
import storybook_v1140_runtimefix
