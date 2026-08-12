from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.4.3 · FIVE SCREEN GPS' not in s:
    raise SystemExit('v1.5 base version not found')
s=s.replace('V1.4.3 · FIVE SCREEN GPS','V1.5 · COURSE DATA PACK')

# Compact data-pack coverage in the live status row.
s=s.replace('"DB  G "+gc+"/18 · T "+tc+"/18"', '"PACK D18 · G"+gc+" · T"+tc')

# Source badge on the strategy card so guide data is never confused with field GPS.
old='''            String note=strategyNote();
            textFit(c,note,m+14,h*.620f,w-m-14,8.2f,INK,true);'''
new='''            String note=strategyNote();
            textFit(c,note,m+14,h*.620f,w-m-14,8.2f,INK,true);
            pill(c,new RectF(w*.69f,h*.585f,w-m-10,h*.607f),Color.rgb(236,246,228),hazardSourceLabel(),GREEN,6.7f);'''
if old in s: s=s.replace(old,new,1)

# Official-guide strategy highlights verified for the trip courses.
s=s.replace('''            if(selected==0 && variant==0){
                if(hole==7) return "업힐 · 조금 큰 클럽으로 왼쪽 포트벙커 회피";''','''            if(selected==0 && variant==0){
                if(hole==4) return "우측 큰 연못 + 그린 앞 크리크 · 티샷 위치와 세컨드 각도 우선";
                if(hole==7) return "업힐 · 조금 큰 클럽으로 왼쪽 포트벙커 회피";''',1)
s=s.replace('''            if(selected==1 && variant==0){
                if(hole==15) return "명물 PAR5 · 그린 주변 연못, 무리한 직공략보다 위치 선정";''','''            if(selected==1 && variant==0){
                if(hole==15) return "명물홀 · 그린 주변 연못 + 크로스벙커, 무리한 직공략보다 위치 선정";''',1)
s=s.replace('''            if(selected==1 && variant==1) return "KING · 비교적 짧은 코스, 티샷 정확도로 스코어 메이킹";''','''            if(selected==1 && variant==1){
                if(hole==17) return "그린 좌측 연못 + 벙커 · 우측 공략이 안전";
                return "KING · 비교적 짧은 코스, 티샷 정확도로 스코어 메이킹";
            }''',1)

# Replace generic/synthetic hazard hints with verified guide highlights only.
s=s.replace('''        private Hazard[] hazardsForHole(){
            if(selected==0&&variant==0&&hole==11)return new Hazard[]{new Hazard("BUNKER",.43f,.22f)};''','''        private Hazard[] hazardsForHole(){
            if(selected==0&&variant==0&&hole==4)return new Hazard[]{new Hazard("WATER",.69f,.52f),new Hazard("WATER",.50f,.18f)};
            if(selected==0&&variant==0&&hole==11)return new Hazard[]{new Hazard("BUNKER",.43f,.22f)};''',1)
s=s.replace('''            if(selected==1&&variant==0&&hole==15)return new Hazard[]{new Hazard("WATER",.60f,.26f)};''','''            if(selected==1&&variant==0&&hole==15)return new Hazard[]{new Hazard("WATER",.60f,.26f),new Hazard("BUNKER",.46f,.48f)};
            if(selected==1&&variant==1&&hole==17)return new Hazard[]{new Hazard("WATER",.34f,.22f),new Hazard("BUNKER",.43f,.19f)};''',1)
# Near-pin recommendations are not hazard evidence; do not draw fake bunkers.
s=s.replace('''            if(selected==2&&(hole==8||hole==15))return new Hazard[]{new Hazard("BUNKER",.40f,.23f)};
''','',1)
# Remove deterministic synthetic hazards from non-verified holes.
s=s.replace('''            int seed=(hole*37+selected*11+variant*7)%5;
            if(seed==0)return new Hazard[]{new Hazard("BUNKER",.35f,.42f)};
            if(seed==1)return new Hazard[]{new Hazard("WATER",.66f,.52f)};
            return new Hazard[0];''','''            return new Hazard[0];''',1)

# Hazard marker distances are calibrated-map estimates unless a real hazard GPS ref exists.
old_h='''                GeoRef gr=greenCenterRef(hole);
                if(gr!=null&&gpsUsable()){
                    int d=Math.round(distance(location,gr.lat,gr.lon));pill(c,new RectF(x-42,y+24,x+42,y+51),Color.argb(228,255,255,255),d+"m",INK,7.2f);
                }'''
new_h='''                GeoRef hr=calibratedMapRef(r,x,y);
                if(hr!=null&&gpsUsable()){
                    int d=Math.round(distance(location,hr.lat,hr.lon));pill(c,new RectF(x-48,y+24,x+48,y+51),Color.argb(228,255,255,255),"약 "+d+"m",INK,7.2f);
                }else{
                    pill(c,new RectF(x-44,y+24,x+44,y+51),Color.argb(228,255,255,255),"GUIDE",INK,6.5f);
                }'''
if old_h in s: s=s.replace(old_h,new_h,1)

# Insert provenance helpers before hazardsForHole().
marker='        private Hazard[] hazardsForHole(){'
if marker not in s:
    raise SystemExit('v1.5 hazard helper marker not found')
helper='''        private boolean officialGuideHole(){
            return (selected==0&&variant==0&&hole==4)
                || (selected==0&&variant==1&&(hole==13||hole==15))
                || (selected==1&&variant==0&&hole==15)
                || (selected==1&&variant==1&&hole==17);
        }
        private String hazardSourceLabel(){
            if(officialGuideHole()) return "OFFICIAL GUIDE";
            if(hazardsForHole().length>0) return "LAYOUT GUIDE";
            return "DIST VERIFIED";
        }

'''
s=s.replace(marker,helper+marker,1)

p.write_text(s)
print('applied v1.5 course data pack + verified hazard provenance')
