from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.10.1 · FIELD YARDAGE SAFE' not in s:
    raise SystemExit('v1.10.2 requires v1.10.1 field yardage safe')
s=s.replace('V1.10.1 · FIELD YARDAGE SAFE','V1.10.2 · FULL HOLE YARDAGE',1)

# Bitmap course-map resources are generated at CI build time.
if 'import android.graphics.Bitmap;' not in s:
    s=s.replace('import android.graphics.Canvas;','import android.graphics.Bitmap;\nimport android.graphics.BitmapFactory;\nimport android.graphics.Canvas;',1)

marker='        private void roundJapanPremium(Canvas c){roundUnifiedYardageV190(c);}'
pos=s.find(marker)
if pos<0: raise SystemExit('v1.10.2 renderer marker missing')

helpers=r'''        private String fullHoleResourceV1102(){
            String hh=hole<10?("0"+hole):(""+hole);
            if(selected==0)return variant==0?("yardage_kamishihoro_c"+hh):("yardage_kamishihoro_m"+hh);
            if(selected==1)return variant==0?("yardage_furano_palmer"+hh):("yardage_furano_king"+hh);
            return null;
        }
        private Bitmap fullHoleBitmapV1102(){
            String n=fullHoleResourceV1102();if(n==null)return null;
            int id=getResources().getIdentifier(n,"drawable",ctx.getPackageName());
            if(id==0)return null;
            try{return BitmapFactory.decodeResource(getResources(),id);}catch(Exception e){return null;}
        }
        private RectF fitCenterV1102(Bitmap b,RectF box){
            float sw=b.getWidth(),sh=b.getHeight();if(sw<=0||sh<=0)return new RectF(box);
            float sc=Math.min(box.width()/sw,box.height()/sh);float dw=sw*sc,dh=sh*sc;
            return new RectF(box.centerX()-dw/2f,box.centerY()-dh/2f,box.centerX()+dw/2f,box.centerY()+dh/2f);
        }
        private void drawDistanceRulerV1102(Canvas c,RectF a,int totalM){
            if(totalM<=0)return;int max=Math.max(100,totalM);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.5f);p.setColor(Color.argb(125,28,76,45));
            for(int d=50;d<max;d+=50){float t=d/(float)max;float y=a.bottom-t*a.height();c.drawLine(a.right-28,y,a.right-8,y,p);text(c,d+"m",a.right-32,y+3,5.7f,Color.rgb(55,86,62),true,Paint.Align.RIGHT);}
            p.setStyle(Paint.Style.FILL);
        }
        private void drawFullHoleYardageV1102(Canvas c,RectF r,int par,int totalM){
            Bitmap b=fullHoleBitmapV1102();
            if(b==null){
                drawActualYardageV190(c,r,par,totalM);
                RectF tag=new RectF(r.left+18,r.top+55,r.left+135,r.top+83);box(c,tag,Color.argb(225,255,247,218),14);text(c,"SCHEMATIC FULL HOLE",tag.centerX(),tag.centerY()+3,5.8f,DEEP,true,Paint.Align.CENTER);
                return;
            }
            softShadow(c,r,30);box(c,r,Color.rgb(244,248,238),30);
            RectF title=new RectF(r.left+12,r.top+9,r.right-12,r.top+48);box(c,title,Color.argb(244,255,255,255),18);
            textFit(c,"H"+hole+" · PAR "+par+" · "+verifiedDistanceLabelV190(),title.left+12,title.centerY()+3,title.right-12,9.5f,DEEP,true);

            RectF stage=new RectF(r.left+10,r.top+54,r.right-10,r.bottom-50);
            p.setColor(Color.rgb(229,240,221));c.drawRoundRect(stage,21,21,p);
            RectF dst=fitCenterV1102(b,new RectF(stage.left+5,stage.top+5,stage.right-5,stage.bottom-5));
            Paint bp=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);c.drawBitmap(b,null,dst,bp);

            RectF greenTag=new RectF(stage.left+8,stage.top+7,stage.left+73,stage.top+31);box(c,greenTag,Color.argb(232,24,111,68),12);text(c,"GREEN",greenTag.centerX(),greenTag.centerY()+3,6.3f,Color.WHITE,true,Paint.Align.CENTER);
            RectF teeTag=new RectF(stage.left+8,stage.bottom-31,stage.left+63,stage.bottom-7);box(c,teeTag,Color.argb(232,8,79,52),12);text(c,"TEE",teeTag.centerX(),teeTag.centerY()+3,6.3f,Color.WHITE,true,Paint.Align.CENTER);
            drawDistanceRulerV1102(c,new RectF(stage.left+4,stage.top+12,stage.right-4,stage.bottom-12),totalM);

            RectF src=new RectF(r.left+12,r.bottom-42,r.right-12,r.bottom-9);box(c,src,Color.argb(242,255,255,255),16);
            textFit(c,"OFFICIAL FULL HOLE MAP · TEE → GREEN · "+yardageSourceV190(),src.left+10,src.centerY()+3,src.right-10,7.2f,GREEN,true);
        }

'''
s=s[:pos]+helpers+s[pos:]

old='courseRect.set(m,h*.318f,w-m,h*.575f);drawActualYardageV190(c,courseRect,par,totalM);drawHolePager(c,h*.292f);'
new='courseRect.set(m,h*.300f,w-m,h*.650f);drawFullHoleYardageV1102(c,courseRect,par,totalM);drawHolePager(c,h*.286f);'
if old not in s: raise SystemExit('v1.10.2 full-hole card anchor missing')
s=s.replace(old,new,1)

repls={
'drawHazardBarV182(c,h*.587f,h*.633f);':'drawHazardBarV182(c,h*.658f,h*.694f);',
'RectF strategy=new RectF(m,h*.646f,w-m,h*.700f);':'RectF strategy=new RectF(m,h*.701f,w-m,h*.747f);',
'text(c,"공략 포인트",strategy.left+14,h*.668f,8.3f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+14,h*.690f,strategy.right-14,7.9f,INK,true);':'text(c,"공략 포인트",strategy.left+14,h*.718f,8.0f,GREEN,true);textFit(c,fieldGuideV1100(),strategy.left+14,h*.739f,strategy.right-14,7.4f,INK,true);',
'greenSave.set(m,h*.713f,w*.38f,h*.767f);teeSave.set(w*.405f,h*.713f,w*.65f,h*.767f);mapLaunch.set(w*.675f,h*.713f,w-m,h*.767f);':'greenSave.set(m,h*.754f,w*.38f,h*.800f);teeSave.set(w*.405f,h*.754f,w*.65f,h*.800f);mapLaunch.set(w*.675f,h*.754f,w-m,h*.800f);',
'drawPlayerTabs(c,h*.784f);int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);':'drawPlayerTabs(c,h*.811f);int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);',
'RectF quick=new RectF(m,h*.831f,w-m,h*.902f);':'RectF quick=new RectF(m,h*.848f,w-m,h*.913f);',
'text(c,"타수",m+16,h*.854f,8.2f,Color.GRAY,true);goldText(c,""+stroke,w*.28f,h*.866f,22.5f,INK);':'text(c,"타수",m+16,h*.869f,8.0f,Color.GRAY,true);goldText(c,""+stroke,w*.28f,h*.882f,21.0f,INK);',
'minus.set(m+68,h*.844f,m+128,h*.893f);plus.set(w*.355f,h*.844f,w*.435f,h*.893f);':'minus.set(m+68,h*.857f,m+128,h*.904f);plus.set(w*.355f,h*.857f,w*.435f,h*.904f);',
'text(c,"퍼트",w*.52f,h*.854f,8.2f,Color.GRAY,true);goldText(c,""+putt,w*.69f,h*.866f,22.5f,INK);':'text(c,"퍼트",w*.52f,h*.869f,8.0f,Color.GRAY,true);goldText(c,""+putt,w*.69f,h*.882f,21.0f,INK);',
'pm.set(w*.535f,h*.844f,w*.605f,h*.893f);pp.set(w*.82f,h*.844f,w*.90f,h*.893f);':'pm.set(w*.535f,h*.857f,w*.605f,h*.904f);pp.set(w*.82f,h*.857f,w*.90f,h*.904f);'
}
for a,b in repls.items():
    if a not in s: raise SystemExit('v1.10.2 lower-layout anchor missing: '+a[:45])
    s=s.replace(a,b,1)

s=s.replace('text(c,"LIVE FIELD BETA",m,h*.035f,8.5f,Color.rgb(215,241,222),true);','text(c,"FULL HOLE YARDAGE",m,h*.035f,8.5f,Color.rgb(215,241,222),true);',1)

p.write_text(s)
print('applied v1.10.2 full tee-to-green yardage renderer')
