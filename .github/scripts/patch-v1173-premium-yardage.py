from pathlib import Path
import re

p = Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s = p.read_text()

if 'import android.graphics.Bitmap;' not in s:
    s = s.replace('import android.graphics.Canvas;\n', 'import android.graphics.Bitmap;\nimport android.graphics.BitmapFactory;\nimport android.graphics.Canvas;\n')

pattern = re.compile(r'        private void drawCourse\(Canvas c,RectF r,int par,int officialM,GeoRef green,Distances ds,float pulse\)\{.*?\n        \}\n\n        private int estimateTargetM', re.S)
replacement = '''        private void drawCourse(Canvas c,RectF r,int par,int officialM,GeoRef green,Distances ds,float pulse){
            long now=SystemClock.uptimeMillis();
            float slide=holeSlideOffset(now);
            c.save();
            c.translate(slide,0);

            // V1.17.3 PREMIUM YARDAGE: use the verified Hokkaido source image as the visual master.
            p.setColor(Color.rgb(226,213,174));
            c.drawRoundRect(r,28,28,p);

            String asset=yardageAssetName();
            int resId=ctx.getResources().getIdentifier(asset,"drawable",ctx.getPackageName());
            Bitmap map=resId==0?null:BitmapFactory.decodeResource(ctx.getResources(),resId);
            RectF imageRect=new RectF(r);
            imageRect.inset(8,8);

            if(map!=null){
                float src=(float)map.getWidth()/Math.max(1,map.getHeight());
                float dst=imageRect.width()/Math.max(1f,imageRect.height());
                if(src>dst){
                    float nh=imageRect.width()/src;
                    float cy=imageRect.centerY();
                    imageRect.top=cy-nh/2f; imageRect.bottom=cy+nh/2f;
                } else {
                    float nw=imageRect.height()*src;
                    float cx=imageRect.centerX();
                    imageRect.left=cx-nw/2f; imageRect.right=cx+nw/2f;
                }
                p.setFilterBitmap(true);
                c.drawBitmap(map,null,imageRect,p);
            } else {
                p.setColor(Color.rgb(30,73,40));
                p.setTextAlign(Paint.Align.CENTER);
                p.setTextSize(18);
                c.drawText("YARDAGE IMAGE LOADING",r.centerX(),r.centerY(),p);
            }

            // Player marker stays on the tee side until hole-image georeferencing is calibrated.
            float youX=imageRect.centerX();
            float youY=imageRect.bottom-Math.max(18f,imageRect.height()*.055f);
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(4);
            p.setColor(Color.argb(160+(int)(70*pulse),255,214,0));
            c.drawCircle(youX,youY,13+7*pulse,p);
            p.setStyle(Paint.Style.FILL);
            p.setColor(Color.rgb(22,74,205)); c.drawCircle(youX,youY,9,p);
            p.setColor(Color.WHITE); c.drawCircle(youX,youY,3,p);
            text(c,"YOU",youX,youY-17,8,Color.WHITE,true,Paint.Align.CENTER);

            if(hasTarget){
                p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(4); p.setColor(CORAL);
                c.drawCircle(targetX,targetY,12+4*pulse,p); p.setStyle(Paint.Style.FILL);
                p.setColor(CORAL); c.drawCircle(targetX,targetY,4,p);
                int est=estimateTargetM(r,officialM);
                speech(c,Math.max(r.left+8,Math.min(targetX-70,r.right-150)),Math.max(r.top+8,targetY-52),"공략 약 "+est+"m",CORAL);
            }

            String bubble=!gpsUsable()?"GPS 품질 확인!":(green==null?"GREEN 좌표 필요":(ds.center>=0?"CENTER "+ds.center+"m":"거리 계산 중"));
            speech(c,r.left+12,r.top+12,bubble,green==null?CORAL:DEEP);
            if(previewMode) pill(c,new RectF(r.left+13,r.bottom-41,r.left+112,r.bottom-14),Color.argb(225,255,255,255),"PREVIEW GPS",CORAL,7.3f);
            c.restore();
        }

        private String yardageAssetName(){
            String h=String.format(java.util.Locale.US,"%02d",hole);
            if(selected==0) return "yardage_kamishihoro_"+(variant==0?"c":"m")+h;
            if(selected==1) return "yardage_furano_"+(variant==0?"palmer":"king")+h;
            return "yardage_sahoro_"+h;
        }

        private int estimateTargetM'''

s2, n = pattern.subn(replacement, s, count=1)
if n != 1:
    raise SystemExit(f'drawCourse patch failed: {n}')

p.write_text(s2)
print('V1.17.3 premium yardage renderer patched')
