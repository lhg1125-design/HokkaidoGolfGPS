from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'masterSourceRectV1161' in s:
    print('V1.16.1 runtime source mapping already applied')
    raise SystemExit(0)
if 'roundMasterMappedV1160' not in s:
    raise SystemExit('V1.16.1 requires V1.16.0 Master Renderer')

# Runtime-only bitmap/crop cache. Raw source JPG bytes are never rewritten.
# Decode and exterior-page scanning happen only when course/variant/hole changes,
# never on every Canvas frame.
anchor='        private void roundMasterMappedV1160(Canvas c){'
if anchor not in s:
    raise SystemExit('V1.16.1 master renderer anchor missing')
helpers=r'''        private boolean masterSourceMappedV1161(){
            // Course-agnostic dispatch: adding a course only requires registering
            // its raw yardage resource/data. No per-course finished UI image.
            return screen==1 && selected>=0 && fullHoleResourceV1102()!=null;
        }
        private String masterRawKeyV1161;
        private Bitmap masterRawBitmapV1161;
        private android.graphics.Rect masterRawCropV1161;
        private Bitmap masterCourseBitmapV1161(){
            String key=fullHoleResourceV1102();
            if(key==null)return null;
            if(key.equals(masterRawKeyV1161) && masterRawBitmapV1161!=null && !masterRawBitmapV1161.isRecycled())return masterRawBitmapV1161;
            if(masterRawBitmapV1161!=null && !masterRawBitmapV1161.isRecycled()){
                try{masterRawBitmapV1161.recycle();}catch(Exception ignored){}
            }
            masterRawKeyV1161=key;masterRawBitmapV1161=null;masterRawCropV1161=null;
            int id=getResources().getIdentifier(key,"drawable",ctx.getPackageName());
            if(id==0)return null;
            try{
                BitmapFactory.Options opt=new BitmapFactory.Options();
                opt.inPreferredConfig=Bitmap.Config.ARGB_8888;opt.inMutable=false;
                masterRawBitmapV1161=BitmapFactory.decodeResource(getResources(),id,opt);
            }catch(Throwable ignored){masterRawBitmapV1161=null;}
            return masterRawBitmapV1161;
        }
        private android.graphics.Rect masterSourceRectV1161(Bitmap im){
            if(im==null)return null;
            if(im==masterRawBitmapV1161 && masterRawCropV1161!=null)return masterRawCropV1161;
            int w=im.getWidth(),h=im.getHeight();
            Bitmap scan=im;boolean recycleScan=false;
            if(im.getConfig()==Bitmap.Config.HARDWARE){
                scan=im.copy(Bitmap.Config.ARGB_8888,false);recycleScan=scan!=null && scan!=im;
            }
            if(scan==null){
                android.graphics.Rect full=new android.graphics.Rect(0,0,w,h);
                masterRawCropV1161=full;return full;
            }
            int[] px=new int[w*h];scan.getPixels(px,0,w,0,0,w,h);
            if(recycleScan)scan.recycle();
            int minX=w,minY=h,maxX=-1,maxY=-1;
            // Only crop the neutral white/cream exterior page. Internal bunkers,
            // paths and every course pixel remain untouched.
            for(int y=0;y<h;y+=2){
                int row=y*w;
                for(int x=0;x<w;x+=2){
                    int cc=px[row+x];int r=Color.red(cc),g=Color.green(cc),b=Color.blue(cc);
                    int hi=Math.max(r,Math.max(g,b)),lo=Math.min(r,Math.min(g,b));
                    boolean neutral=r>=238 && g>=238 && b>=232 && (hi-lo)<=26;
                    if(!neutral){if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y;}
                }
            }
            android.graphics.Rect out;
            if(maxX<minX || maxY<minY){out=new android.graphics.Rect(0,0,w,h);}
            else{
                int pad=Math.max(4,Math.min(w,h)/80);
                int l=Math.max(0,minX-pad),t=Math.max(0,minY-pad),r=Math.min(w,maxX+pad+2),b=Math.min(h,maxY+pad+2);
                out=new android.graphics.Rect(l,t,r,b);
            }
            masterRawCropV1161=out;return out;
        }
        private RectF masterFitSourceV1161(android.graphics.Rect src,RectF box){
            if(src==null||src.width()<=0||src.height()<=0)return new RectF(box);
            float sc=Math.min(box.width()/src.width(),box.height()/src.height());
            float ww=src.width()*sc,hh=src.height()*sc;
            float l=box.centerX()-ww/2f,t=box.centerY()-hh/2f;
            return new RectF(l,t,l+ww,t+hh);
        }
'''
s=s.replace(anchor,helpers+anchor,1)

# Master renderer must use the cached raw bitmap rather than decoding the JPG
# again on every 50 ms draw frame.
old_course='            Bitmap course=fullHoleBitmapV1102();'
new_course='            Bitmap course=masterCourseBitmapV1161();'
if old_course not in s:
    raise SystemExit('V1.16.1 master bitmap decode anchor missing')
s=s.replace(old_course,new_course,1)

old='''            if(course!=null){
                RectF dst=fitCenterV1102(course,slot);Paint bp=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);c.drawBitmap(course,null,dst,bp);
            }else{'''
new='''            if(course!=null){
                android.graphics.Rect src=masterSourceRectV1161(course);
                RectF dst=masterFitSourceV1161(src,slot);
                Paint bp=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);
                c.drawBitmap(course,src,dst,bp);
            }else{'''
if old not in s:
    raise SystemExit('V1.16.1 raw course draw anchor missing')
s=s.replace(old,new,1)

# Route every registered raw course through the same Master Renderer before any
# legacy country/course-specific renderer. Future courses only extend the raw
# source registry/data, not the UI rendering code.
round_sig='        private void round(Canvas c){'
if round_sig not in s:
    raise SystemExit('V1.16.1 round dispatch anchor missing')
if 'if(masterSourceMappedV1161())' not in s:
    s=s.replace(round_sig,round_sig+'\n            if(masterSourceMappedV1161()){roundMasterMappedV1160(c);return;}',1)
# Reuse the same generic predicate for target/nav touch routing.
s=s.replace('if(screen==1 && selected==4){','if(screen==1 && masterSourceMappedV1161()){',1)

# True edge-to-edge including display cutout. This is a single app-level policy,
# not a per-course image workaround.
activity='    @Override protected void onCreate(Bundle b) {'
if activity not in s:
    raise SystemExit('V1.16.1 activity anchor missing')
method=r'''    private void applyMasterEdgeToEdgeV1161() {
        getWindow().setFlags(android.view.WindowManager.LayoutParams.FLAG_FULLSCREEN,
                android.view.WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS);
        if (android.os.Build.VERSION.SDK_INT >= 28) {
            android.view.WindowManager.LayoutParams lp=getWindow().getAttributes();
            lp.layoutInDisplayCutoutMode=android.view.WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            getWindow().setAttributes(lp);
        }
        if (android.os.Build.VERSION.SDK_INT >= 30) {
            getWindow().setDecorFitsSystemWindows(false);
            android.view.WindowInsetsController ic=getWindow().getInsetsController();
            if(ic!=null){
                ic.hide(android.view.WindowInsets.Type.statusBars() | android.view.WindowInsets.Type.navigationBars());
                ic.setSystemBarsBehavior(android.view.WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            }
        }
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                View.SYSTEM_UI_FLAG_FULLSCREEN |
                View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    @Override public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if(hasFocus) applyMasterEdgeToEdgeV1161();
    }

'''
if 'applyMasterEdgeToEdgeV1161' not in s:
    s=s.replace(activity,method+activity,1)
    s=s.replace(activity,activity+'\n        applyMasterEdgeToEdgeV1161();',1)

p.write_text(s)
print('V1.16.1 MASTER SOURCE MAP: course-agnostic registry + one-time raw bitmap/crop cache; raw SHA preserved; edge-to-edge')
