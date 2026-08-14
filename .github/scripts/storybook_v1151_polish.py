from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.15.0 · STORYBOOK RECOVERY' not in s:
    raise SystemExit('V1.15.1 requires V1.15.0 recovery')


def bounds(src,signature):
    a=src.find(signature)
    if a<0: raise SystemExit('missing method: '+signature)
    br=src.find('{',a);dep=0
    for i in range(br,len(src)):
        if src[i]=='{': dep+=1
        elif src[i]=='}':
            dep-=1
            if dep==0:return a,i+1
    raise SystemExit('unclosed method: '+signature)


def replace_method(src,signature,repl):
    a,b=bounds(src,signature);return src[:a]+repl+src[b:]

if 'V1.15.1 · REFERENCE POLISH' not in s:
    s=s.replace('V1.15.0 · STORYBOOK RECOVERY','V1.15.0 · STORYBOOK RECOVERY / V1.15.1 · REFERENCE POLISH',1)

# -----------------------------------------------------------------------------
# Live yardage: approved reference has H/PAR in the sky header and ONLY
# FRONT/CENTER/BACK on the wood board. Remove the fourth metric column.
# -----------------------------------------------------------------------------
title=r'''        private void drawPlayTitleV1137(Canvas c,float m,float w,float h){
            String title=ko[selected],course=variants[selected][variant];float ty=h*(coverHudV1138()? .061f:.050f);
            textFit(c,title,m,ty,w*.67f,coverHudV1138()?19.5f:18.7f,Color.WHITE,true);
            String sub=course+"  ·  H"+hole+" / PAR"+currentPar();
            textFit(c,sub,m,ty+h*(coverHudV1138()? .034f:.028f),w*.67f,10.6f,Color.rgb(246,253,240),true);
        }'''
s=replace_method(s,'        private void drawPlayTitleV1137(Canvas c,float m,float w,float h)',title)

old='metric(c,"PAR "+par,"H"+hole,w*.18f,metricYV1138(h));metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.39f,metricYV1138(h));metric(c,"CENTER",ds.center+"m",w*.61f,metricYV1138(h));metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.82f,metricYV1138(h));'
new='metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,metricYV1138(h));metric(c,"CENTER",ds.center+"m",w*.50f,metricYV1138(h));metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,metricYV1138(h));'
if old not in s:
    raise SystemExit('V1.15.1 calibrated metric row anchor missing')
s=s.replace(old,new,1)

# -----------------------------------------------------------------------------
# Paint-state hard reset. The map renderer legitimately uses translucent Paint;
# the footer must not inherit that alpha. Direct dark fill matches the master.
# -----------------------------------------------------------------------------
nav=r'''        private void drawCleanNavV1150(Canvas c){
            float w=getWidth(),h=getHeight();setPmNavV1148(w,h);
            p.setShader(null);p.clearShadowLayer();p.setAlpha(255);p.setStyle(Paint.Style.FILL);
            RectF bar=new RectF(w*.020f,h*.914f,w*.980f,h*.992f);softShadow(c,bar,bar.height()*.28f);
            p.setShader(null);p.clearShadowLayer();p.setAlpha(255);p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(12,82,54));c.drawRoundRect(bar,bar.height()*.28f,bar.height()*.28f,p);
            p.setColor(Color.argb(34,255,255,255));c.drawRoundRect(new RectF(bar.left+4,bar.top+4,bar.right-4,bar.top+bar.height()*.43f),bar.height()*.23f,bar.height()*.23f,p);
            String[] labs={"스코어","코스","타겟","메뉴"};for(int i=0;i<4;i++){RectF r=pmNavV1148[i];float cx=r.centerX(),iy=bar.top+bar.height()*.30f;drawNavIconV1150(c,i,cx,iy,bar.height()*.23f,Color.WHITE);text(c,labs[i],cx,bar.bottom-bar.height()*.12f,9.8f,Color.WHITE,true,Paint.Align.CENTER);}
            p.setShader(null);p.clearShadowLayer();p.setAlpha(255);p.setStyle(Paint.Style.FILL);
        }'''
s=replace_method(s,'        private void drawCleanNavV1150(Canvas c)',nav)

# Reset Paint before lower yardage furniture too, so badge/target never wash out.
a,b=bounds(s,'        private void drawYardageFooterV1150(Canvas c)')
chunk=s[a:b]
needle='            float w=getWidth(),h=getHeight();'
if needle not in chunk: raise SystemExit('yardage footer paint-reset anchor missing')
chunk=chunk.replace(needle,needle+'p.setShader(null);p.clearShadowLayer();p.setAlpha(255);p.setStyle(Paint.Style.FILL);',1)
s=s[:a]+chunk+s[b:]

# -----------------------------------------------------------------------------
# Score summary card: use the existing hand-drawn landscape helper (not a
# squeezed full-screen raster). YARDAGE shows CURRENT GREEN CENTER distance.
# -----------------------------------------------------------------------------
a,b=bounds(s,'        private void scoreInput(Canvas c)')
chunk=s[a:b]
old_scene='c.save();c.clipRect(scene);c.drawBitmap(v12Course,null,scene,p);c.restore();'
if old_scene not in chunk: raise SystemExit('score landscape anchor missing')
chunk=chunk.replace(old_scene,'drawScoreLandscapeV1143(c,scene);',1)

old_total='            int totalM=verifiedMetersV190();if(totalM<=0)totalM=(int)Math.round(currentYards()*.9144);'
new_total='''            int totalM=verifiedMetersV190();if(totalM<=0)totalM=(int)Math.round(currentYards()*.9144);\n            GeoRef scoreGreenV1151=greenCenterRef(hole);int centerM=totalM;if(previewMode)centerM=155;else if(scoreGreenV1151!=null&&gpsUsable())centerM=Math.round(distance(location,scoreGreenV1151.lat,scoreGreenV1151.lon));else{int rem=navRemainV1110(totalM);if(rem>=0)centerM=rem;}'''
if old_total not in chunk: raise SystemExit('score center-yardage calculation anchor missing')
chunk=chunk.replace(old_total,new_total,1)
chunk=chunk.replace('text(c,"YARDAGE",yard.centerX(),yard.top+24,8.4f,Color.rgb(255,239,195),true,Paint.Align.CENTER);text(c,totalM+"m",yard.centerX(),yard.centerY()+20,27.0f,Color.WHITE,true,Paint.Align.CENTER);',
                    'text(c,"CENTER",yard.centerX(),yard.top+24,8.4f,Color.rgb(255,239,195),true,Paint.Align.CENTER);text(c,centerM+"m",yard.centerX(),yard.centerY()+20,27.0f,Color.WHITE,true,Paint.Align.CENTER);',1)
s=s[:a]+chunk+s[b:]

# The old full-screen Pixel-Master rasters are no longer rendered in V1.15.x.
# Remove them from the packaged resources to prevent accidental regression and
# shrink the APK. Keep the 135 actual hole maps untouched.
for name in ['yardage_chrome_v1148.webp','score_pixel_master_v1148.webp','score_selected_v1148.webp']:
    fp=Path('app/src/main/res/drawable-nodpi')/name
    if fp.exists(): fp.unlink()

p.write_text(s)
print('V1.15.1 REFERENCE POLISH: 3-column yardage board + dark nav + clean score landscape + GREEN CENTER yardage')
