from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

# Route all three Japan trip courses through a fresh premium renderer. This
# deliberately bypasses the old coarse 2D map path, while leaving data/GPS,
# score and field-capture logic intact.
needle='        private void round(Canvas c){\n            if(selected>=3){roundKorea(c);return;}'
if needle not in s:
    raise SystemExit('v1.8.1 round routing anchor missing')
s=s.replace(needle,'        private void round(Canvas c){\n            if(selected<3){roundJapanPremium(c);return;}\n            if(selected>=3){roundKorea(c);return;}',1)

marker='        private void roundKorea(Canvas c){'
pos=s.find(marker)
if pos<0:
    raise SystemExit('v1.8.1 Korea renderer marker missing')

method=r'''        private void roundJapanPremium(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;int par=currentPar();int officialM=currentOfficialM();
            c.drawColor(BG);

            RectF head=new RectF(0,0,w,h*.151f);gradient(c,head,DEEP,GREEN,0);
            text(c,"LIVE COURSE",m,h*.040f,9.5f,Color.rgb(215,241,222),true);
            text(c,"GPS 캐디",m,h*.073f,17.5f,Color.WHITE,true);
            text(c,ko[selected],m,h*.110f,21.5f,Color.WHITE,true);
            text(c,variants[selected][variant]+" · H"+hole,m,h*.139f,10.5f,Color.rgb(218,242,222),true);
            pill(c,new RectF(w*.735f,h*.028f,w*.94f,h*.069f),Color.rgb(235,247,229),gpsStatusShort(),gpsColor(),7.4f);
            pill(c,new RectF(w*.735f,h*.087f,w*.94f,h*.130f),Color.argb(55,255,255,255),"PAR "+par,Color.WHITE,11.5f);

            GeoRef green=greenCenterRef(hole),gf=getRef("gf",hole),gb=getRef("gb",hole);Distances ds=distances3(gf,green,gb);
            RectF range=new RectF(m,h*.162f,w-m,h*.246f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),26);sheen(c,range,26);
            if(ds.center>=0){
                metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.180f);
                metric(c,"CENTER",ds.center+"m",w*.50f,h*.180f);
                metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.180f);
            }else{
                metric(c,"FRONT","--",w*.20f,h*.180f);
                metric(c,"OFFICIAL",officialM+"m",w*.50f,h*.180f);
                metric(c,"BACK","--",w*.80f,h*.180f);
            }
            pill(c,new RectF(m,h*.252f,w*.29f,h*.281f),gpsBg(),gpsStatusShort(),gpsColor(),6.9f);
            pill(c,new RectF(w*.31f,h*.252f,w*.70f,h*.281f),CARD,selected==0?"TOKACHI PREMIUM":selected==1?"FURANO PREMIUM":"SAHORO PREMIUM",GREEN,6.5f);
            autoBtn.set(w*.72f,h*.252f,w-m,h*.281f);pill(c,autoBtn,autoHole?Color.rgb(229,244,218):CARD,autoHole?"AUTO ON":"AUTO OFF",autoHole?GREEN:Color.GRAY,6.7f);

            courseRect.set(m,h*.292f,w-m,h*.610f);
            drawPremiumCourseArt(c,courseRect);
            RectF stat=new RectF(courseRect.left+16,courseRect.bottom-68,courseRect.right-16,courseRect.bottom-18);box(c,stat,Color.argb(226,255,255,255),22);
            goldText(c,"H"+hole+" · PAR "+par+" · REG "+officialM+"m",stat.centerX(),stat.centerY(),12.0f,DEEP);

            // Verified guide hazards stay lightweight on the scenic artwork; they
            // remain guide marks, not fabricated GPS points.
            Hazard[] hz=hazardsForHole();
            for(int i=0;i<hz.length;i++){
                Hazard z=hz[i];float x=courseRect.left+z.x*courseRect.width(),y=courseRect.bottom-z.y*courseRect.height();
                int cc=z.type.equals("WATER")?BLUE:YELLOW;
                p.setColor(Color.argb(226,255,255,255));c.drawCircle(x,y,25,p);p.setColor(cc);c.drawCircle(x,y,18,p);
                goldText(c,z.type.equals("WATER")?"W":"B",x,y,10.5f,z.type.equals("WATER")?Color.WHITE:DEEP);
            }
            drawHolePager(c,h*.304f);
            drawHazardCaptureButtons(c,courseRect);

            RectF strategy=new RectF(m,h*.626f,w-m,h*.688f);softShadow(c,strategy,20);box(c,strategy,CARD,20);
            text(c,"공략 포인트",m+14,h*.649f,8.6f,GREEN,true);
            textFit(c,strategyNote(),m+14,h*.674f,w*.70f,8.2f,INK,true);
            pill(c,new RectF(w*.72f,h*.638f,w-m-10,h*.671f),Color.rgb(236,246,228),hazardSourceLabel(),GREEN,6.1f);

            boolean capReady=previewMode || (location!=null && location.getAccuracy()<=12 && fixAgeSec()<=15);
            int gBg=capReady?(green==null?CORAL:DEEP):Color.rgb(150,160,150),tBg=capReady?(getRef("t",hole)==null?Color.rgb(53,139,94):DEEP):Color.rgb(150,160,150);
            greenSave.set(m,h*.704f,w*.38f,h*.762f);teeSave.set(w*.405f,h*.704f,w*.65f,h*.762f);mapLaunch.set(w*.675f,h*.704f,w-m,h*.762f);
            goldButton(c,greenSave,gBg,greenSaveLabel(),Color.WHITE,14.5f);goldButton(c,teeSave,tBg,getRef("t",hole)==null?"TEE 저장":"TEE OK",Color.WHITE,14.5f);goldButton(c,mapLaunch,CARD,"외부 지도",INK,14.5f);

            drawPlayerTabs(c,h*.782f);int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);
            RectF quick=new RectF(m,h*.833f,w-m,h*.902f);softShadow(c,quick,22);box(c,quick,CARD,22);
            text(c,"타수",m+18,h*.855f,8.7f,Color.GRAY,true);goldText(c,""+stroke,w*.28f,h*.867f,23f,INK);
            minus.set(m+72,h*.845f,m+132,h*.893f);plus.set(w*.355f,h*.845f,w*.435f,h*.893f);
            goldButton(c,minus,SOFT,"−",INK,18f);goldButton(c,plus,Color.rgb(229,244,218),"+",GREEN,18f);
            text(c,"퍼트",w*.52f,h*.855f,8.7f,Color.GRAY,true);goldText(c,""+putt,w*.69f,h*.867f,23f,INK);
            pm.set(w*.535f,h*.845f,w*.605f,h*.893f);pp.set(w*.82f,h*.845f,w*.90f,h*.893f);
            goldButton(c,pm,SOFT,"−",INK,18f);goldButton(c,pp,Color.rgb(226,245,250),"+",BLUE,18f);
            setFourNav(w,h);drawGoldenNav(c);
        }

'''
s=s[:pos]+method+s[pos:]

# Version badge update for the new Japan renderer.
s=s.replace('"V1.8 · PREMIUM COURSE ART"','"V1.8.1 · PREMIUM COURSE ART"')
p.write_text(s)
print('applied v1.8.1 premium Japan renderer')
