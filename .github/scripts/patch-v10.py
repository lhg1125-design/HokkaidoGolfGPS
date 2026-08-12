from pathlib import Path

path = Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s = path.read_text()


def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'v1.0 patch pattern missing: {label}')
    s = s.replace(old, new)

rep('"V0.9 · SAFETY + STRATEGY"', '"V1.0 · COURSE MAP"', 'version badge')
rep('"코스 공략 탑재!"', '"플레이어가 움직여!"', 'home speech')
rep('"공식 정규 거리 · GPS 안전잠금 · 현장 좌표 DB · 4인 스코어"',
    '"실제 GPS 진행률 · GREEN 3점 구조 · 안전잠금 · 4인 스코어"', 'home subtitle')
rep('"모든 거리 m · 정규 티 거리 데이터 검증 완료"',
    '"모든 거리 m · GREEN Front / Center / Back 구조"', 'home footer')

rep('GeoRef green=getRef("g",hole); Distances ds=distances(green);',
    'GeoRef green=greenCenterRef(hole); GeoRef greenFront=getRef("gf",hole), greenBack=getRef("gb",hole); Distances ds=distances3(greenFront,green,greenBack);',
    'round green refs')

rep('int gc=savedCount("g"),tc=savedCount("t");',
    'int gc=savedGreenCenters(),tc=savedCount("t");', 'db counts')
rep('"DB  G "+gc+"/18 · T "+tc+"/18"',
    '"DB  G "+gc+"/18 · T "+tc+"/18"', 'db text noop')

rep('pillButton(c,greenSave,green==null?CORAL:DEEP,confirmKind==1&&SystemClock.uptimeMillis()<confirmUntil?"한 번 더 눌러 저장":"GREEN 저장",Color.WHITE);',
    'pillButton(c,greenSave,green==null?CORAL:DEEP,greenSaveLabel(),Color.WHITE);', 'green save button')

rep('if(greenSave.contains(x,y)){saveRef(1);return true;}',
    'if(greenSave.contains(x,y)){saveGreenPoint();return true;}', 'green save touch')

rep('int base=distances(getRef("g",hole)).center;',
    'int base=distances3(getRef("gf",hole),greenCenterRef(hole),getRef("gb",hole)).center;', 'target estimate')

rep('float youX=cx,youY=r.bottom-30; dashRoute(c,youX,youY,flagX,flagY+8,phase);',
    'float prog=playerProgress(); float youX=cx,youY=r.bottom-30-prog*Math.max(0,r.height()-118); dashRoute(c,youX,youY,flagX,flagY+8,phase);',
    'player position')
rep('text(c,"YOU",youX,r.bottom-6,8,GREEN,true,Paint.Align.CENTER);',
    'text(c,"YOU",youX,Math.min(r.bottom-6,youY+28),8,GREEN,true,Paint.Align.CENTER); if(prog>0.02f) pill(c,new RectF(r.left+12,r.top+12,r.left+104,r.top+39),Color.argb(225,255,255,255),"진행 "+Math.round(prog*100)+"%",GREEN,7.6f);',
    'progress badge')

rep('String bubble = !gpsUsable() ? "GPS 품질 확인!" : (green==null ? "GREEN 좌표 필요" : (ds.center>=0 ? "CENTER "+ds.center+"m" : "거리 계산 중"));',
    'String bubble = !gpsUsable() ? "GPS 품질 확인!" : (green==null ? "GREEN 좌표 필요" : (ds.center>=0 ? "CENTER "+ds.center+"m · "+greenMode() : "거리 계산 중"));',
    'green mode bubble')

# Replace preview reference block with explicit GREEN Front/Center/Back sample points.
rep('''if(previewMode && selected==0 && variant==0 && h==11){
                if(type.equals("g")) return new GeoRef(43.25982,143.22836,true);
                if(type.equals("t")) return new GeoRef(43.25720,143.22836,true);
            }''',
'''if(previewMode && selected==0 && variant==0 && h==11){
                if(type.equals("gf")) return new GeoRef(43.25970,143.22836,true);
                if(type.equals("g") || type.equals("gc")) return new GeoRef(43.25982,143.22836,true);
                if(type.equals("gb")) return new GeoRef(43.25994,143.22836,true);
                if(type.equals("t")) return new GeoRef(43.25720,143.22836,true);
            }''', 'preview green 3pt')

# Replace the old Center±12 distance function with exact-when-available 3-point logic.
rep('''private String refKey(String type,int h){return type+"_"+selected+"_"+variant+"_"+h;}
        private int savedCount(String type){int n=0;for(int h=1;h<=18;h++)if(getRef(type,h)!=null)n++;return n;}
        private Distances distances(GeoRef ref){
            if(ref==null || !gpsUsable()) return new Distances(-1,-1,-1);
            int center=Math.round(distance(location,ref.lat,ref.lon)); return new Distances(Math.max(0,center-12),center,center+12);
        }
        private float distance(Location l,double lat,double lon){float[] o=new float[1];Location.distanceBetween(l.getLatitude(),l.getLongitude(),lat,lon,o);return o[0];}''',
'''private String refKey(String type,int h){return type+"_"+selected+"_"+variant+"_"+h;}
        private int savedCount(String type){int n=0;for(int h=1;h<=18;h++)if(getRef(type,h)!=null)n++;return n;}
        private int savedGreenCenters(){int n=0;for(int h=1;h<=18;h++)if(greenCenterRef(h)!=null)n++;return n;}
        private GeoRef greenCenterRef(int h){GeoRef r=getRef("gc",h);return r!=null?r:getRef("g",h);}
        private int greenPointCountForHole(){int n=0;if(getRef("gf",hole)!=null)n++;if(greenCenterRef(hole)!=null)n++;if(getRef("gb",hole)!=null)n++;return n;}
        private String greenMode(){int n=greenPointCountForHole();return n>=3?"3점":"C±12";}
        private String greenSaveLabel(){
            long now=SystemClock.uptimeMillis(); if(confirmKind>=3 && now<confirmUntil)return "한 번 더 눌러 저장";
            if(getRef("gf",hole)==null)return "GREEN FRONT";
            if(greenCenterRef(hole)==null)return "GREEN CENTER";
            if(getRef("gb",hole)==null)return "GREEN BACK";
            return "GREEN 3점 ✓";
        }
        private Distances distances3(GeoRef front,GeoRef center,GeoRef back){
            if(center==null || !gpsUsable()) return new Distances(-1,-1,-1);
            int c=Math.round(distance(location,center.lat,center.lon));
            int f=front!=null?Math.round(distance(location,front.lat,front.lon)):Math.max(0,c-12);
            int b=back!=null?Math.round(distance(location,back.lat,back.lon)):c+12;
            return new Distances(f,c,b);
        }
        private float playerProgress(){
            GeoRef tee=getRef("t",hole),center=greenCenterRef(hole); if(!gpsUsable()||tee==null||center==null)return 0f;
            float[] total=new float[1]; Location.distanceBetween(tee.lat,tee.lon,center.lat,center.lon,total); if(total[0]<30)return 0f;
            float left=distance(location,center.lat,center.lon); return Math.max(0f,Math.min(1f,1f-left/total[0]));
        }
        private float distance(Location l,double lat,double lon){float[] o=new float[1];Location.distanceBetween(l.getLatitude(),l.getLongitude(),lat,lon,o);return o[0];}''', 'green distance engine')

# Insert 3-point save workflow before getRef().
marker = '        private GeoRef getRef(String type,int h){'
if marker not in s:
    raise SystemExit('v1.0 patch pattern missing: getRef marker')
insert = '''        private void saveGreenPoint(){
            if(getRef("gf",hole)==null){saveGreenRef("gf",3,"GREEN FRONT");return;}
            if(greenCenterRef(hole)==null){saveGreenRef("gc",4,"GREEN CENTER");return;}
            if(getRef("gb",hole)==null){saveGreenRef("gb",5,"GREEN BACK");return;}
            showToast("H"+hole+" GREEN Front / Center / Back 저장 완료");
        }

        private void saveGreenRef(String type,int kind,String label){
            if(location==null){showToast("GPS 위치를 먼저 잡아주세요");return;}
            if(!previewMode && (location.getAccuracy()>12 || fixAgeSec()>8)){showToast("GPS 품질 GOOD에서 저장해주세요");return;}
            long now=SystemClock.uptimeMillis();
            if(confirmKind!=kind || now>confirmUntil){confirmKind=kind;confirmUntil=now+3200;showToast(label+" 위치에서 한 번 더 눌러 저장");invalidate();return;}
            String k=refKey(type,hole);
            calPrefs.edit().putLong(k+"_lat",Double.doubleToRawLongBits(location.getLatitude())).putLong(k+"_lon",Double.doubleToRawLongBits(location.getLongitude())).apply();
            // Backward compatibility: CENTER also populates legacy g key.
            if(type.equals("gc")){String legacy=refKey("g",hole);calPrefs.edit().putLong(legacy+"_lat",Double.doubleToRawLongBits(location.getLatitude())).putLong(legacy+"_lon",Double.doubleToRawLongBits(location.getLongitude())).apply();}
            confirmKind=0;confirmUntil=0;showToast("H"+hole+" "+label+" 저장 완료 · "+greenPointCountForHole()+"/3");invalidate();
        }

'''
s = s.replace(marker, insert + marker)

# Add small F/C/B dots around the green whenever the 3-point structure is populated.
rep('p.setColor(Color.rgb(74,168,78)); c.drawOval(new RectF(cx-29,r.top+43,cx+50,r.top+79),p);',
'''p.setColor(Color.rgb(74,168,78)); c.drawOval(new RectF(cx-29,r.top+43,cx+50,r.top+79),p);
            if(greenPointCountForHole()>0){
                float gx=cx-47,gy=r.top+50; String[] gl={"F","C","B"}; int[] gc={SKY,GREEN,CORAL};
                for(int i=0;i<3;i++){p.setColor(gc[i]);c.drawCircle(gx,gy+i*14,4,p);text(c,gl[i],gx-8,gy+3+i*14,6.8f,gc[i],true,Paint.Align.RIGHT);}
            }''', 'green markers')

path.write_text(s)
print('Applied V1.0 Course Map patch')
