from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'GOLDEN MASTER V1.16.2' not in s or 'goldenCourseV1162' not in s:
    raise SystemExit('V1.16.3 requires V1.16.2 golden renderer')
if 'CONCEPT REFERENCE LOCK V1.16.3' in s:
    print('V1.16.3 already applied'); raise SystemExit(0)

# Less cartoon-heavy black stroke: match the uploaded concept's crisp rounded type.
s=s.replace('Math.max(2.2f,z*.105f)','Math.max(2.0f,z*.070f)',1)

# Display-only color grading. Official/raw source bytes are untouched and the alpha/shape,
# bunker/water/path coordinates and aspect ratio are unchanged.
old='''                if(seen[i]!=0){px[i]=px[i]&0x00ffffff;continue;}\n                if(Color.alpha(px[i])!=0){int x=i%w,y=i/w;if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y;}'''
new='''                if(seen[i]!=0){px[i]=px[i]&0x00ffffff;continue;}\n                if(Color.alpha(px[i])!=0){\n                    int cc=px[i],aa=Color.alpha(cc),rr=Color.red(cc),gg=Color.green(cc),bb=Color.blue(cc);\n                    if(gg>rr*.92f && gg>bb*1.05f && (gg-bb)>12){\n                        rr=Math.max(0,Math.min(255,Math.round(rr*.56f)));\n                        gg=Math.max(0,Math.min(255,Math.round(gg*.78f+2f)));\n                        bb=Math.max(0,Math.min(255,Math.round(bb*.30f)));\n                    }else if(bb>rr*1.10f && bb>gg*1.02f){\n                        rr=Math.max(0,Math.min(255,Math.round(rr*.72f)));\n                        gg=Math.max(0,Math.min(255,Math.round(gg*.86f)));\n                        bb=Math.max(0,Math.min(255,Math.round(bb*1.04f)));\n                    }else if(rr>165 && gg>145 && bb>105){\n                        rr=Math.max(0,Math.min(255,Math.round(rr*.90f)));\n                        gg=Math.max(0,Math.min(255,Math.round(gg*.86f)));\n                        bb=Math.max(0,Math.min(255,Math.round(bb*.78f)));\n                    }else{\n                        rr=Math.max(0,Math.min(255,Math.round(rr*.88f)));\n                        gg=Math.max(0,Math.min(255,Math.round(gg*.88f)));\n                        bb=Math.max(0,Math.min(255,Math.round(bb*.84f)));\n                    }\n                    px[i]=Color.argb(aa,rr,gg,bb);\n                    int x=i%w,y=i/w;if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y;\n                }'''
if old not in s: raise SystemExit('V1.16.3 course color-grade anchor missing')
s=s.replace(old,new,1)

# A 200 m marker is meaningful only when the actual hole length reaches 200 m.
s=s.replace('if(top>=200){','if(totalM>=200){',1)

# Slightly larger central course viewport without warping the official aspect ratio.
s=s.replace('RectF slot=new RectF(260,365,680,1422)','RectF slot=new RectF(250,355,690,1435)',1)

# Explicit provenance marker for CI and future regressions.
s=s.replace('        // GOLDEN MASTER V1.16.2','        // CONCEPT REFERENCE LOCK V1.16.3\n        // User-supplied Furano H2/H3 concept is the visual source of truth.\n        // GOLDEN MASTER V1.16.2',1)

p.write_text(s)
print('V1.16.3 CONCEPT REFERENCE LOCK: richer Storybook palette + geometry-safe display grading + valid 200m marker logic')
