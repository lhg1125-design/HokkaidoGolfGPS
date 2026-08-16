from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'GOLDEN MASTER V1.16.2' not in s or 'goldenCourseV1162' not in s:
    raise SystemExit('V1.16.3 requires V1.16.2 golden renderer')
if 'CONCEPT REFERENCE LOCK V1.16.3' in s:
    print('V1.16.3 already applied'); raise SystemExit(0)

# Match the approved image master: cleaner rounded type and no duplicate top distance board.
s=s.replace('Math.max(2.2f,z*.105f)','Math.max(2.0f,z*.070f)',1)

old='''                if(seen[i]!=0){px[i]=px[i]&0x00ffffff;continue;}\n                if(Color.alpha(px[i])!=0){int x=i%w,y=i/w;if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y;}'''
new='''                if(seen[i]!=0){px[i]=px[i]&0x00ffffff;continue;}\n                if(Color.alpha(px[i])!=0){\n                    int cc=px[i],aa=Color.alpha(cc),rr=Color.red(cc),gg=Color.green(cc),bb=Color.blue(cc);\n                    if(gg>rr*.92f && gg>bb*1.05f && (gg-bb)>12){rr=Math.max(0,Math.min(255,Math.round(rr*.56f)));gg=Math.max(0,Math.min(255,Math.round(gg*.78f+2f)));bb=Math.max(0,Math.min(255,Math.round(bb*.30f)));}\n                    else if(bb>rr*1.10f && bb>gg*1.02f){rr=Math.max(0,Math.min(255,Math.round(rr*.72f)));gg=Math.max(0,Math.min(255,Math.round(gg*.86f)));bb=Math.max(0,Math.min(255,Math.round(bb*1.04f)));}\n                    else if(rr>165 && gg>145 && bb>105){rr=Math.max(0,Math.min(255,Math.round(rr*.90f)));gg=Math.max(0,Math.min(255,Math.round(gg*.86f)));bb=Math.max(0,Math.min(255,Math.round(bb*.78f)));}\n                    else{rr=Math.max(0,Math.min(255,Math.round(rr*.88f)));gg=Math.max(0,Math.min(255,Math.round(gg*.88f)));bb=Math.max(0,Math.min(255,Math.round(bb*.84f)));}\n                    px[i]=Color.argb(aa,rr,gg,bb);int x=i%w,y=i/w;if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y;\n                }'''
if old not in s: raise SystemExit('V1.16.3 course color-grade anchor missing')
s=s.replace(old,new,1)
s=s.replace('if(top>=200){','if(totalM>=200){',1)

# MASTER MATCH: remove the large FRONT/CENTER/BACK wood distance board from runtime.
# Header flows directly into the course canvas, as requested from the approved image master.
s=s.replace('goldenMetricV1162(c,ds.front,166,Color.rgb(30,145,255));goldenMetricV1162(c,center,470,Color.WHITE);goldenMetricV1162(c,ds.back,775,Color.rgb(255,80,72));','',1)

# Enlarge and raise the actual course artwork; keep aspect ratio and raw geometry untouched.
s=s.replace('RectF slot=new RectF(260,365,680,1422)','RectF slot=new RectF(220,205,735,1435)',1)

# Remaining-distance bubble is the single distance readout.
s=s.replace('goldenTextV1162(c,remain+"m",816,500,48,Color.rgb(25,25,20),Paint.Align.CENTER,false);','goldenTextV1162(c,remain+"m",816,500,48,Color.rgb(25,25,20),Paint.Align.CENTER,false);',1)

s=s.replace('        // GOLDEN MASTER V1.16.2','        // CONCEPT REFERENCE LOCK V1.16.3\n        // MASTER MATCH: duplicate top distance board removed; course art enlarged.\n        // GOLDEN MASTER V1.16.2',1)
p.write_text(s)
print('V1.16.3 MASTER MATCH: no duplicate top distance board + enlarged runtime course art')
