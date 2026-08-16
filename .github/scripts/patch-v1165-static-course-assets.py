from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'GOLDEN MASTER V1.16.2' not in s or 'drawGoldenMasterV1162' not in s:
    raise SystemExit('V1.16.5 requires golden master renderer')
if 'STATIC COURSE ASSET V1.16.5' in s:
    print('V1.16.5 already applied'); raise SystemExit(0)

def bounds(src,signature):
    a=src.find(signature)
    if a<0: raise SystemExit('missing '+signature)
    br=src.find('{',a); dep=0
    for i in range(br,len(src)):
        if src[i]=='{': dep+=1
        elif src[i]=='}':
            dep-=1
            if dep==0: return a,i+1
    raise SystemExit('unclosed '+signature)

def replace_method(src,signature,repl):
    a,b=bounds(src,signature)
    return src[:a]+repl+src[b:]

def remove_method(src,signature):
    a,b=bounds(src,signature)
    return src[:a]+src[b:]

# Remove the old runtime neutral-pixel classifier entirely.
if '        private boolean goldenNeutralV1162(int cc)' in s:
    s=remove_method(s,'        private boolean goldenNeutralV1162(int cc)')

# Replace all runtime flood-fill / recolor / alpha editing with a static-resource loader.
s=replace_method(s,'        private android.graphics.Bitmap goldenCourseV1162()',r'''        // STATIC COURSE ASSET V1.16.5
        // Approved course pixels are prepared before APK packaging.
        // Runtime does decode -> contain-fit -> draw only. No pixel mutation.
        private android.graphics.Bitmap goldenCourseV1162(){
            String key=fullHoleResourceV1102();
            if(key==null)return null;
            if(key.equals(masterGoldenKeyV1162) && masterGoldenCourseV1162!=null && !masterGoldenCourseV1162.isRecycled())return masterGoldenCourseV1162;
            if(masterGoldenCourseV1162!=null && !masterGoldenCourseV1162.isRecycled())try{masterGoldenCourseV1162.recycle();}catch(Exception ignored){}
            masterGoldenCourseV1162=null;masterGoldenCropV1162=null;masterGoldenKeyV1162=key;
            String approved="approved_"+key;
            int id=getResources().getIdentifier(approved,"drawable",ctx.getPackageName());
            if(id==0)id=getResources().getIdentifier(key,"drawable",ctx.getPackageName());
            if(id==0)return null;
            try{
                android.graphics.BitmapFactory.Options opt=new android.graphics.BitmapFactory.Options();
                opt.inPreferredConfig=android.graphics.Bitmap.Config.ARGB_8888;opt.inMutable=false;
                masterGoldenCourseV1162=android.graphics.BitmapFactory.decodeResource(getResources(),id,opt);
            }catch(Throwable ignored){masterGoldenCourseV1162=null;}
            if(masterGoldenCourseV1162!=null)masterGoldenCropV1162=new android.graphics.Rect(0,0,masterGoldenCourseV1162.getWidth(),masterGoldenCourseV1162.getHeight());
            return masterGoldenCourseV1162;
        }''')

# Disable legacy source scanning as well: it now returns the full static bitmap rect.
if '        private android.graphics.Rect masterSourceRectV1161(Bitmap im)' in s:
    s=replace_method(s,'        private android.graphics.Rect masterSourceRectV1161(Bitmap im)',r'''        private android.graphics.Rect masterSourceRectV1161(Bitmap im){
            if(im==null)return null;
            return new android.graphics.Rect(0,0,im.getWidth(),im.getHeight());
        }''')

# Remove obsolete crop cache state left by V1.16.1. No runtime crop state remains.
s=s.replace('        private android.graphics.Rect masterRawCropV1161;\n','')
s=s.replace('masterRawKeyV1161=key;masterRawBitmapV1161=null;masterRawCropV1161=null;','masterRawKeyV1161=key;masterRawBitmapV1161=null;')

# Restore the approved master top wood metrics if an earlier patch suppressed them.
needle='int center=ds.center>=0?ds.center:totalM;'
metrics='goldenMetricV1162(c,ds.front,166,Color.rgb(30,145,255));goldenMetricV1162(c,center,470,Color.WHITE);goldenMetricV1162(c,ds.back,775,Color.rgb(255,80,72));'
pos=s.find(needle)
if pos<0: raise SystemExit('center metric anchor missing')
segment=s[pos:pos+500]
if 'goldenMetricV1162(c,ds.front' not in segment:
    s=s[:pos+len(needle)]+metrics+s[pos+len(needle):]

# Approved master layout: full tee-to-green image must fit above bottom nav.
for old in ['RectF slot=new RectF(220,205,735,1435)','RectF slot=new RectF(250,355,690,1435)','RectF slot=new RectF(260,365,680,1422)','RectF slot=new RectF(238,350,704,1442)']:
    if old in s:
        s=s.replace(old,'RectF slot=new RectF(240,350,700,1428)',1)
        break
else:
    raise SystemExit('course slot anchor missing')

# Mark provenance and make the runtime contract explicit.
mark='        // GOLDEN MASTER V1.16.2'
if mark in s:
    s=s.replace(mark,'        // STATIC COURSE ASSET V1.16.5\n        // Runtime contract: decode + contain-fit + draw only; no course-pixel mutation.\n'+mark,1)

p.write_text(s)
print('V1.16.5 STATIC COURSE ASSET: runtime image mutation removed; approved static resources only')
