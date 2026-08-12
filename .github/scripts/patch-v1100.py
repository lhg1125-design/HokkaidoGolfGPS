from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.9.0 · ACTUAL YARDAGE PACK' not in s:
    raise SystemExit('v1.10.0 requires v1.9.0 actual yardage pack')
s=s.replace('V1.9.0 · ACTUAL YARDAGE PACK','V1.10.0 · FIELD BETA',1)

# -----------------------------------------------------------------------------
# V1.10 field-beta policy
# - Keep every published distance from V1.9 exactly intact.
# - Remove decorative/random dogleg movement from the yardage renderer.
# - Only bend the fairway where an official guide explicitly confirms a shape.
# - Add clearly labelled guide hazards for the trip holes that have official
#   narrative evidence. These are strategy-guide positions, NOT GPS claims.
# - Show current-hole TEE/GREEN calibration readiness in the map footer.
# -----------------------------------------------------------------------------
marker='        private void roundJapanPremium(Canvas c){roundUnifiedYardageV190(c);}'
pos=s.find(marker)
if pos<0:
    raise SystemExit('v1.10.0 v1.9 renderer marker missing')

helpers=r'''        private float smoothV1100(float x){
            x=Math.max(0f,Math.min(1f,x));return x*x*(3f-2f*x);
        }
        private float shapeOffsetV1100(float t){
            // Kamishihoro MASTERS H13: official guide = gentle right dogleg.
            if(selected==0 && variant==1 && hole==13){
                float k=smoothV1100((t-.30f)/.70f);return .165f*k;
            }
            // Other holes stay neutral instead of inventing a dogleg.
            return 0f;
        }
        private boolean officialShapeV1100(){
            return selected==0 && variant==1 && hole==13;
        }
        private String shapeLabelV1100(){return officialShapeV1100()?"SHAPE OFFICIAL":"SHAPE GUIDE";}
        private String calStatusV1100(){
            boolean g=greenCenterRef(hole)!=null,t=getRef("t",hole)!=null;
            if(g&&t)return "GPS G✓ T✓";
            if(g)return "GPS G✓ T-";
            if(t)return "GPS G- T✓";
            return "GPS G- T-";
        }
        private String fieldGuideV1100(){
            if(selected==0 && variant==0){
                if(hole==4)return "공식 가이드 · 우측 큰 연못 + 그린 앞 크리크. 티샷 위치를 확보하고 세컨드 각도를 만든다.";
                if(hole==7)return "공식 가이드 · 업힐. 조금 큰 클럽으로 좌측 포트벙커를 피한다.";
                if(hole==9)return "공식 가이드 · 우측으로 흐르는 지형. 티샷은 좌측, 2타째부터는 약간 오르막.";
                if(hole==11)return "공식 가이드 · 그린 앞 길고 큰 벙커. 벙커를 피해 우측 공략이 안전.";
                if(hole==18)return "공식 가이드 · 페어웨이 벙커 방향 티샷 후 오르막. 그린 좌우 가드벙커 주의.";
            }
            if(selected==0 && variant==1){
                if(hole==12)return "공식 가이드 · 내리막 PAR3. 좌측 앞 연못을 확실히 피한다.";
                if(hole==13)return "공식 가이드 · 완만한 우도그렉 PAR5. 2타째 구간의 크리크가 핵심.";
                if(hole==15)return "공식 가이드 · 그린 반주변 연못 + 양쪽 대형 벙커. 핀보다 안전면 우선.";
                if(hole==18)return "공식 가이드 · 티샷은 페어웨이 우측. 2타째는 그린 뒤쪽을 기준으로 공략.";
            }
            if(selected==1 && variant==0 && hole==15)return "공식 가이드 · 그린을 둘러싼 연못 + 크로스벙커. 무리한 직공략보다 레이업 위치 선정.";
            if(selected==1 && variant==1 && hole==17)return "공식 가이드 · 그린 좌측 연못 + 벙커. 우측 공략이 안전한 대표 전략 홀.";
            if(selected==2)return "GORA 코스가이드 · 넓은 페어웨이지만 3개의 소하천과 다수의 연못이 핵심. 현장 GPS 저장값을 우선한다.";
            return courseGuideV190();
        }
        private void guideWaterV1100(Canvas c,RectF r,float x,float y,float ww,float hh,String tag){
            RectF q=new RectF(r.left+r.width()*x-r.width()*ww*.5f,r.top+r.height()*y-r.height()*hh*.5f,r.left+r.width()*x+r.width()*ww*.5f,r.top+r.height()*y+r.height()*hh*.5f);
            p.setColor(Color.rgb(76,174,212));c.drawOval(q,p);text(c,tag,q.centerX(),q.centerY()+3,5.8f,Color.WHITE,true,Paint.Align.CENTER);
        }
        private void guideCreekV1100(Canvas c,RectF r,float y){
            float yy=r.top+r.height()*y;p.setColor(Color.rgb(76,174,212));c.drawRoundRect(new RectF(r.left+r.width()*.23f,yy-4,r.right-r.width()*.18f,yy+5),5,5,p);
        }
        private void guideBunkerV1100(Canvas c,RectF r,float x,float y,float ww,float hh){
            RectF q=new RectF(r.left+r.width()*x-r.width()*ww*.5f,r.top+r.height()*y-r.height()*hh*.5f,r.left+r.width()*x+r.width()*ww*.5f,r.top+r.height()*y+r.height()*hh*.5f);
            p.setColor(Color.rgb(238,219,153));c.drawOval(q,p);
        }
        private void drawOfficialGuideTerrainV1100(Canvas c,RectF r){
            // Positions are intentionally schematic and labelled as GUIDE: the
            // official text verifies hazard side/type, not precise GPS geometry.
            if(selected==0 && variant==0 && hole==4){guideWaterV1100(c,r,.76f,.56f,.23f,.29f,"GUIDE");guideCreekV1100(c,r,.27f);}
            if(selected==0 && variant==0 && hole==7){guideBunkerV1100(c,r,.34f,.28f,.10f,.07f);}
            if(selected==0 && variant==0 && hole==11){guideBunkerV1100(c,r,.43f,.26f,.28f,.08f);}
            if(selected==0 && variant==0 && hole==18){guideBunkerV1100(c,r,.55f,.58f,.12f,.07f);guideBunkerV1100(c,r,.39f,.22f,.10f,.06f);guideBunkerV1100(c,r,.62f,.22f,.10f,.06f);}
            if(selected==0 && variant==1 && hole==12){guideWaterV1100(c,r,.30f,.25f,.20f,.18f,"GUIDE");}
            if(selected==0 && variant==1 && hole==13){guideCreekV1100(c,r,.48f);}
            if(selected==0 && variant==1 && hole==15){guideWaterV1100(c,r,.50f,.20f,.45f,.22f,"GUIDE");guideBunkerV1100(c,r,.34f,.19f,.10f,.07f);guideBunkerV1100(c,r,.67f,.19f,.10f,.07f);}
            if(selected==1 && variant==0 && hole==15){guideWaterV1100(c,r,.51f,.19f,.43f,.21f,"GUIDE");guideBunkerV1100(c,r,.46f,.48f,.15f,.07f);}
            if(selected==1 && variant==1 && hole==17){guideWaterV1100(c,r,.28f,.22f,.24f,.20f,"GUIDE");guideBunkerV1100(c,r,.38f,.22f,.10f,.07f);}
        }

'''
s=s[:pos]+helpers+s[pos:]

old='''                float t=i/(float)(n-1),s1=(float)Math.sin(seed*.021+t*3.1),s2=(float)Math.sin(seed*.013+t*5.7);\n                float cx=r.centerX()+r.width()*(.095f*s1+.035f*s2);float width=r.width()*(par==3?.115f:(.090f+.040f*t));'''
new='''                float t=i/(float)(n-1);\n                float cx=r.centerX()+r.width()*shapeOffsetV1100(t);float width=r.width()*(par==3?.115f:(.090f+.040f*t));'''
if old not in s:
    raise SystemExit('v1.10.0 random fairway centerline anchor missing')
s=s.replace(old,new,1)

stripe='''            Path fw=new Path();fw.moveTo(lx[0],ys[0]);for(int i=1;i<n;i++)fw.lineTo(lx[i],ys[i]);for(int i=n-1;i>=0;i--)fw.lineTo(rx[i],ys[i]);fw.close();p.setColor(Color.rgb(72,161,76));c.drawPath(fw,p);stripes(c,fw,r,(SystemClock.uptimeMillis()%2600L)/2600f);'''
if stripe not in s:
    raise SystemExit('v1.10.0 fairway draw anchor missing')
s=s.replace(stripe,stripe+'\n            drawOfficialGuideTerrainV1100(c,r);',1)

old_footer='''            goldText(c,yardageSourceV190()+" · DISTANCE VERIFIED",src.centerX(),src.centerY(),8.4f,yardageSourceColorV190());'''
new_footer='''            textFit(c,"DIST OK · "+shapeLabelV1100()+" · "+calStatusV1100(),src.left+10,src.centerY()+3,src.right-10,8.1f,yardageSourceColorV190(),true);'''
if old_footer not in s:
    raise SystemExit('v1.10.0 source footer anchor missing')
s=s.replace(old_footer,new_footer,1)

old_strategy='''textFit(c,courseGuideV190(),strategy.left+14,h*.690f,strategy.right-14,7.9f,INK,true);'''
new_strategy='''textFit(c,fieldGuideV1100(),strategy.left+14,h*.690f,strategy.right-14,7.9f,INK,true);'''
if old_strategy not in s:
    raise SystemExit('v1.10.0 strategy anchor missing')
s=s.replace(old_strategy,new_strategy,1)

s=s.replace('text(c,"LIVE YARDAGE",m,h*.035f,8.5f,Color.rgb(215,241,222),true);','text(c,"LIVE FIELD BETA",m,h*.035f,8.5f,Color.rgb(215,241,222),true);',1)

p.write_text(s)
print('applied v1.10.0 field beta: verified-shape policy + guide terrain + calibration footer')
