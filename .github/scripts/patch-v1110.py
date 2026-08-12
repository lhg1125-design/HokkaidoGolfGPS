from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.10.6 · HOKKAIDO 126 HOLE PACK' not in s:
    raise SystemExit('v1.11.0 requires v1.10.6 126-hole pack')
s=s.replace('V1.10.6 · HOKKAIDO 126 HOLE PACK','V1.11.0 · FIELD NAV BETA',1)

marker='        private void roundJapanPremium(Canvas c){roundUnifiedYardageV190(c);}'
pos=s.find(marker)
if pos<0:
    raise SystemExit('v1.11.0 renderer marker missing')

helpers=r'''        private float navProgressV1110(){
            if(previewMode)return .42f;
            if(location==null || !gpsUsable())return -1f;
            GeoRef t=getRef("t",hole),g=greenCenterRef(hole);
            if(t==null || g==null)return -1f;
            double lat0=Math.toRadians((t.lat+g.lat)*.5);
            double gx=(g.lon-t.lon)*Math.cos(lat0),gy=g.lat-t.lat;
            double px=(location.getLongitude()-t.lon)*Math.cos(lat0),py=location.getLatitude()-t.lat;
            double den=gx*gx+gy*gy;if(den<1e-15)return -1f;
            float q=(float)((px*gx+py*gy)/den);
            return Math.max(0f,Math.min(1f,q));
        }
        private int navRemainV1110(int totalM){
            float q=navProgressV1110();if(q<0)return -1;
            if(previewMode)return Math.max(1,Math.round(Math.max(1,totalM)*(1f-q)));
            GeoRef g=greenCenterRef(hole);if(g==null || location==null)return -1;
            return Math.max(0,Math.round(distance(location,g.lat,g.lon)));
        }
        private boolean navReadyV1110(){
            return previewMode || (gpsUsable() && getRef("t",hole)!=null && greenCenterRef(hole)!=null);
        }
        private String navAccuracyV1110(){
            if(previewMode)return "SIM";
            if(location==null)return "GPS --";
            return "±"+Math.round(location.getAccuracy())+"m";
        }
        private void drawFieldNavV1110(Canvas c,RectF stage,int totalM){
            float top=stage.top+42,bottom=stage.bottom-42,x=stage.right-17;
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3.2f);p.setColor(Color.argb(145,8,79,52));
            c.drawLine(x,top,x,bottom,p);p.setStyle(Paint.Style.FILL);
            p.setColor(Color.rgb(24,111,68));c.drawCircle(x,top,4.5f,p);
            p.setColor(Color.rgb(8,79,52));c.drawCircle(x,bottom,4.5f,p);

            if(!navReadyV1110()){
                RectF wait=new RectF(stage.right-178,stage.top+8,stage.right-8,stage.top+35);
                box(c,wait,Color.argb(238,255,247,218),13);
                textFit(c,"LIVE NAV · TEE+GREEN 저장 필요",wait.left+8,wait.centerY()+3,wait.right-8,6.2f,AMBER,true);
                return;
            }
            float q=navProgressV1110();int remain=navRemainV1110(totalM);
            float y=bottom-q*(bottom-top);
            p.setColor(Color.argb(245,255,255,255));c.drawCircle(x,y,13,p);
            p.setColor(CORAL);c.drawCircle(x,y,9,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.0f);p.setColor(Color.argb(180,255,126,92));c.drawCircle(x,y,15,p);p.setStyle(Paint.Style.FILL);

            RectF you=new RectF(stage.right-116,y-14,stage.right-31,y+14);
            box(c,you,Color.argb(244,255,255,255),14);
            textFit(c,"YOU · "+Math.round(q*100f)+"%",you.left+8,you.centerY()+3,you.right-8,6.8f,CORAL,true);

            RectF live=new RectF(stage.right-191,stage.top+8,stage.right-8,stage.top+35);
            box(c,live,Color.argb(242,255,255,255),13);
            String mode=previewMode?"SIM AXIS":"GPS AXIS";
            String msg=mode+" · "+(remain>=0?remain+"m TO GREEN":"--")+" · "+navAccuracyV1110();
            textFit(c,msg,live.left+8,live.centerY()+3,live.right-8,6.4f,DEEP,true);
        }

'''
s=s[:pos]+helpers+s[pos:]

anchor='''            drawDistanceRulerV1102(c,new RectF(stage.left+4,stage.top+12,stage.right-4,stage.bottom-12),totalM);'''
if anchor not in s:
    raise SystemExit('v1.11.0 distance-ruler anchor missing')
s=s.replace(anchor,anchor+'\n            drawFieldNavV1110(c,stage,totalM);',1)

# Keep the product claim precise: this is a progress axis, not a geo-registered map marker.
s=s.replace('text(c,"FULL HOLE YARDAGE",m,h*.035f,8.5f,Color.rgb(215,241,222),true);','text(c,"FIELD NAV · FULL HOLE",m,h*.035f,8.5f,Color.rgb(215,241,222),true);',1)

p.write_text(s)
print('applied v1.11.0 honest GPS-axis field navigation beta')
