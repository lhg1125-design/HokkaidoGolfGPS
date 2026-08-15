from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

# V1.15.4 user-approved visual lock:
# - real fullscreen app viewport (no Android status/navigation bars)
# - Furano KING H1 official center distance restored to 412m (451yd source)
# - preview remaining distances match the reviewed screenshots
# - preview never adds the live GPS position dot on top of the reviewed art

old_h1='{313,168,401,523,386,335,175,359,489,350,312,535,346,151,360,170,422,506}'
new_h1='{451,168,401,523,386,335,175,359,489,350,312,535,346,151,360,170,422,506}'
if old_h1 in s:
    s=s.replace(old_h1,new_h1,1)
elif new_h1 not in s:
    raise SystemExit('V1.15.4 Furano KING yards anchor missing')

old_remain='if(previewMode)return totalM;'
new_remain='if(previewMode){if(hole==1)return 286;if(hole==2)return 154;return 367;}'
if old_remain in s:
    s=s.replace(old_remain,new_remain,1)
elif new_remain not in s:
    raise SystemExit('V1.15.4 Furano preview remain anchor missing')

marker_start='            float q=totalM<=0?0f:Math.max(0f,Math.min(1f,1f-remain/(float)totalM));float px=mr.centerX(),py=mr.bottom-q*mr.height();'
target_start='            if(hasTarget){float tx=targetX/sx,ty=targetY/sy;'
if '// V1154 live GPS marker only' not in s:
    if marker_start not in s or target_start not in s:
        raise SystemExit('V1.15.4 Furano marker anchors missing')
    s=s.replace(marker_start,'            // V1154 live GPS marker only; reviewed preview art stays untouched.\n            if(!previewMode){\n'+marker_start,1)
    s=s.replace(target_start,'            }\n'+target_start,1)

if 'private void applyImmersiveV1154()' not in s:
    set_content='        setContentView(view);'
    if set_content not in s:
        raise SystemExit('V1.15.4 setContentView anchor missing')
    s=s.replace(set_content,set_content+'\n        applyImmersiveV1154();',1)
    anchor='    private void startGps() {'
    if anchor not in s:
        raise SystemExit('V1.15.4 startGps anchor missing')
    immersive='''    private void applyImmersiveV1154() {\n        getWindow().getDecorView().setSystemUiVisibility(\n                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY\n                | View.SYSTEM_UI_FLAG_FULLSCREEN\n                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION\n                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN\n                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION\n                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);\n    }\n\n    @Override public void onWindowFocusChanged(boolean hasFocus) {\n        super.onWindowFocusChanged(hasFocus);\n        if (hasFocus) applyImmersiveV1154();\n    }\n\n'''
    s=s.replace(anchor,immersive+anchor,1)

if 'V1.15.4 · USER GOLDEN VISUAL LOCK' not in s:
    if 'V1.15.3 · FURANO H1 MASTER RECT' not in s:
        raise SystemExit('V1.15.4 version anchor missing')
    s=s.replace('V1.15.3 · FURANO H1 MASTER RECT','V1.15.3 · FURANO H1 MASTER RECT / V1.15.4 · USER GOLDEN VISUAL LOCK',1)

p.write_text(s)
print('V1.15.4 USER GOLDEN VISUAL LOCK: fullscreen + H1 412m + reviewed preview remain + no preview GPS dot')
