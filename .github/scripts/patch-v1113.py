from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
if 'V1.11.2 · SIM WALK BETA' not in s:
    raise SystemExit('v1.11.3 requires v1.11.2 sim walk beta')
s=s.replace('V1.11.2 · SIM WALK BETA','V1.11.3 · FIRST ROUND NAV',1)

old='''        private float navProgressV1110(){
            if(previewMode)return simProgressV1112;
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
'''
new='''        private boolean navEstimatedV1113(){
            return !previewMode && gpsUsable() && getRef("t",hole)!=null && greenCenterRef(hole)==null && verifiedMetersV190()>0;
        }
        private float navProgressV1110(){
            if(previewMode)return simProgressV1112;
            if(location==null || !gpsUsable())return -1f;
            GeoRef t=getRef("t",hole),g=greenCenterRef(hole);
            if(t==null)return -1f;
            if(g==null){
                int total=verifiedMetersV190();if(total<=0)return -1f;
                float walked=distance(location,t.lat,t.lon);
                return Math.max(0f,Math.min(1f,walked/Math.max(1f,total)));
            }
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
            GeoRef g=greenCenterRef(hole);if(g!=null && location!=null)return Math.max(0,Math.round(distance(location,g.lat,g.lon)));
            if(navEstimatedV1113())return Math.max(0,Math.round(Math.max(1,totalM)*(1f-q)));
            return -1;
        }
        private boolean navReadyV1110(){
            return previewMode || (gpsUsable() && getRef("t",hole)!=null && (greenCenterRef(hole)!=null || verifiedMetersV190()>0));
        }
'''
if old not in s:
    raise SystemExit('v1.11.3 nav core anchor missing')
s=s.replace(old,new,1)

old='''                textFit(c,"LIVE NAV · TEE+GREEN 저장 필요",wait.left+8,wait.centerY()+3,wait.right-8,6.2f,AMBER,true);'''
new='''                textFit(c,"LIVE NAV · TEE 저장 필요",wait.left+8,wait.centerY()+3,wait.right-8,6.2f,AMBER,true);'''
if old not in s:
    raise SystemExit('v1.11.3 wait message anchor missing')
s=s.replace(old,new,1)

old='''            String mode=previewMode?"SIM AXIS":"GPS AXIS";
            String msg=previewMode?(mode+" · "+(remain>=0?remain+"m":"--")+" · TAP"):(mode+" · "+(remain>=0?remain+"m":"--")+" · "+navAccuracyV1110());'''
new='''            String mode=previewMode?"SIM AXIS":(navEstimatedV1113()?"EST AXIS":"GPS AXIS");
            String msg=previewMode?(mode+" · "+(remain>=0?remain+"m":"--")+" · TAP"):(mode+" · "+(remain>=0?remain+"m":"--")+" · "+navAccuracyV1110());'''
if old not in s:
    raise SystemExit('v1.11.3 nav mode anchor missing')
s=s.replace(old,new,1)

# Promote remaining distance to the main metric row when navigation is available.
old='''            else if(selected<=2){metric(c,"REGULAR",officialYardsV190()+"Y",w*.25f,h*.175f);metric(c,"METER",totalM+"m",w*.50f,h*.175f);metric(c,"PAR",""+par,w*.75f,h*.175f);}'''
new='''            else if(selected<=2){int nr=navRemainV1110(totalM);metric(c,"REGULAR",officialYardsV190()+"Y",w*.25f,h*.175f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"METER",(nr>=0?nr:totalM)+"m",w*.50f,h*.175f);metric(c,"PAR",""+par,w*.75f,h*.175f);}'''
if old not in s:
    raise SystemExit('v1.11.3 Japan main metric anchor missing')
s=s.replace(old,new,1)

old='''            else if(selected==4){metric(c,"WHITE",totalM+"m",w*.25f,h*.175f);metric(c,"PAR",""+par,w*.50f,h*.175f);metric(c,"HOLE","H"+hole,w*.75f,h*.175f);}'''
new='''            else if(selected==4){int nr=navRemainV1110(totalM);metric(c,"WHITE",totalM+"m",w*.25f,h*.175f);metric(c,nr>=0?(navEstimatedV1113()?"EST REMAIN":"REMAIN"):"PAR",nr>=0?(nr+"m"):(""+par),w*.50f,h*.175f);metric(c,"HOLE","H"+hole,w*.75f,h*.175f);}'''
if old not in s:
    raise SystemExit('v1.11.3 Royal main metric anchor missing')
s=s.replace(old,new,1)

p.write_text(s)
print('applied v1.11.3 first-round tee-only EST navigation with LIVE upgrade')
