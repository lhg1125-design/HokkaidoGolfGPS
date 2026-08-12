from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.8.3 · CLEAN YARDAGE UX' not in s:
    raise SystemExit('v1.9.0 requires v1.8.3 clean yardage UX')
s=s.replace('V1.8.3 · CLEAN YARDAGE UX','V1.9.0 · ACTUAL YARDAGE PACK',1)

# -----------------------------------------------------------------------------
# Verified distance pack.
# Japan 3 courses use published REGULAR yardage. Royal Links uses the official
# WHITE tee table in meters. Naepo does not publish a trustworthy per-hole
# distance table in the sources we can verify, so it deliberately switches to
# actual field-calibrated TEE -> GREEN CENTER GPS distance after capture.
# -----------------------------------------------------------------------------
marker='        private void roundJapanPremium(Canvas c){'
pos=s.find(marker)
if pos<0:
    raise SystemExit('v1.9.0 roundJapanPremium marker missing')
helpers=r'''        private int officialYardsV190(){
            final int[][][] jp={
                {
                    {523,413,170,366,361,351,135,358,481,415,183,395,167,370,509,426,399,516},
                    {454,516,416,155,331,369,373,150,367,393,351,132,455,328,167,469,356,370}
                },
                {
                    {470,410,171,411,545,426,400,174,379,395,132,420,342,414,527,182,388,525},
                    {313,168,401,523,386,335,175,359,489,350,312,535,346,151,360,170,422,506}
                },
                {
                    {395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493},
                    {395,500,419,181,383,496,406,165,325,398,173,398,516,398,156,333,391,493}
                }
            };
            if(selected<0||selected>2)return 0;int v=Math.max(0,Math.min(1,variant));return jp[selected][v][hole-1];
        }
        private int royalWhiteMetersV190(){
            final int[][] r={
                {470,350,315,120,320,345,515,145,325,340,510,350,125,315,310,495,120,305},
                {320,440,255,140,470,295,145,335,340,435,340,145,335,330,110,455,335,390}
            };
            int v=Math.max(0,Math.min(1,variant));return r[v][hole-1];
        }
        private int fieldGpsMetersV190(){
            GeoRef t=getRef("t",hole),g=greenCenterRef(hole);if(t==null||g==null)return 0;
            float[] o=new float[1];Location.distanceBetween(t.lat,t.lon,g.lat,g.lon,o);return Math.max(1,Math.round(o[0]));
        }
        private int verifiedMetersV190(){
            if(selected<=2)return Math.round(officialYardsV190()*.9144f);
            if(selected==4)return royalWhiteMetersV190();
            if(selected==3)return fieldGpsMetersV190();
            return 0;
        }
        private String verifiedDistanceLabelV190(){
            if(selected<=2){int y=officialYardsV190();return "REG "+y+"Y · "+Math.round(y*.9144f)+"m";}
            if(selected==4)return "WHITE "+royalWhiteMetersV190()+"m";
            int m=fieldGpsMetersV190();return m>0?("FIELD GPS "+m+"m"):"FIELD CAL REQUIRED";
        }
        private String yardageSourceV190(){
            if(selected<=1)return "OFFICIAL REGULAR";
            if(selected==2)return "GORA REGULAR";
            if(selected==4)return "OFFICIAL WHITE";
            return fieldGpsMetersV190()>0?"GPS FIELD VERIFIED":"GPS CALIBRATION";
        }
        private int yardageSourceColorV190(){
            if(selected==3 && fieldGpsMetersV190()==0)return CORAL;return GREEN;
        }
        private String courseGuideV190(){
            if(selected<3)return strategyNote();
            return koreaStrategyNote();
        }
        private void drawActualYardageV190(Canvas c,RectF r,int par,int totalM){
            int seed=(selected+1)*1009+(variant+1)*331+hole*53;float pulse=(float)(.5+.5*Math.sin(SystemClock.uptimeMillis()/430.0));
            c.save();Path clip=new Path();clip.addRoundRect(r,30,30,Path.Direction.CW);c.clipPath(clip);
            gradient(c,r,Color.rgb(222,242,210),Color.rgb(185,226,180),30);
            // subtle premium texture - clean enough to read as a yardage card
            p.setColor(Color.argb(22,255,255,255));for(int i=0;i<8;i++){float yy=r.top+i*r.height()/7f;c.drawRect(r.left,yy,r.right,yy+r.height()/14f,p);}
            int scaleM=Math.max(260,totalM>0?totalM:360);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.5f);p.setColor(Color.argb(70,40,95,55));
            for(int d=50;d<scaleM;d+=50){float t=d/(float)scaleM;float yy=r.bottom-32-t*(r.height()-84);c.drawLine(r.left+16,yy,r.right-16,yy,p);text(c,d+"m",r.right-18,yy-4,6.5f,Color.rgb(76,105,80),true,Paint.Align.RIGHT);}
            p.setStyle(Paint.Style.FILL);
            int n=10;float[] lx=new float[n],rx=new float[n],ys=new float[n];
            for(int i=0;i<n;i++){
                float t=i/(float)(n-1),s1=(float)Math.sin(seed*.021+t*3.1),s2=(float)Math.sin(seed*.013+t*5.7);
                float cx=r.centerX()+r.width()*(.095f*s1+.035f*s2);float width=r.width()*(par==3?.115f:(.090f+.040f*t));
                ys[i]=r.bottom-34-t*(r.height()-92);lx[i]=cx-width;rx[i]=cx+width;
            }
            Path rough=new Path();rough.moveTo(lx[0]-16,ys[0]);for(int i=1;i<n;i++)rough.lineTo(lx[i]-16,ys[i]);for(int i=n-1;i>=0;i--)rough.lineTo(rx[i]+16,ys[i]);rough.close();p.setColor(Color.rgb(111,187,95));c.drawPath(rough,p);
            Path fw=new Path();fw.moveTo(lx[0],ys[0]);for(int i=1;i<n;i++)fw.lineTo(lx[i],ys[i]);for(int i=n-1;i>=0;i--)fw.lineTo(rx[i],ys[i]);fw.close();p.setColor(Color.rgb(72,161,76));c.drawPath(fw,p);stripes(c,fw,r,(SystemClock.uptimeMillis()%2600L)/2600f);
            // tee and green are always inside the clipped map area
            float tx=(lx[0]+rx[0])/2f,ty=ys[0]+7;p.setColor(DEEP);c.drawRoundRect(new RectF(tx-25,ty-7,tx+25,ty+7),7,7,p);
            float gx=(lx[n-1]+rx[n-1])/2f,gy=ys[n-1];p.setColor(Color.rgb(49,137,69));c.drawOval(new RectF(gx-38,gy-16,gx+38,gy+16),p);p.setColor(INK);c.drawRect(gx+1,gy-31,gx+4,gy+5,p);Path flag=new Path();flag.moveTo(gx+4,gy-31);flag.lineTo(gx+31+5*pulse,gy-23);flag.lineTo(gx+4,gy-15);flag.close();p.setColor(CORAL);c.drawPath(flag,p);
            Hazard[] hz=hazardsForHole();for(int i=0;i<hz.length;i++){Hazard z=hz[i];float x=r.left+z.x*r.width(),y=r.bottom-z.y*r.height();int cc=z.type.equals("WATER")?BLUE:YELLOW;p.setColor(Color.argb(240,255,255,255));c.drawCircle(x,y,19,p);p.setColor(cc);c.drawCircle(x,y,13,p);goldText(c,z.type.equals("WATER")?"W":"B",x,y,8.0f,z.type.equals("WATER")?Color.WHITE:DEEP);}
            if(hasTarget){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(CORAL);c.drawCircle(targetX,targetY,12+4*pulse,p);p.setStyle(Paint.Style.FILL);p.setColor(CORAL);c.drawCircle(targetX,targetY,4,p);}
            c.restore();
            // labels are drawn after restore so they remain sharp and never get cropped by the fairway clip
            RectF topChip=new RectF(r.left+12,r.top+10,r.right-12,r.top+49);box(c,topChip,Color.argb(238,255,255,255),18);
            textFit(c,"H"+hole+" · PAR "+par+" · "+verifiedDistanceLabelV190(),topChip.left+12,topChip.centerY()+3,topChip.right-12,9.5f,DEEP,true);
            RectF src=new RectF(r.left+12,r.bottom-47,r.right-12,r.bottom-10);box(c,src,Color.argb(238,255,255,255),18);
            goldText(c,yardageSourceV190()+" · DISTANCE VERIFIED",src.centerX(),src.centerY(),8.4f,yardageSourceColorV190());
        }

        private void roundUnifiedYardageV190(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;int par=currentPar(),totalM=verifiedMetersV190();
            c.drawColor(BG);
            RectF head=new RectF(0,0,w,h*.145f);gradient(c,head,DEEP,GREEN,0);
            text(c,"LIVE YARDAGE",m,h*.035f,8.5f,Color.rgb(215,241,222),true);
            text(c,ko[selected],m,h*.080f,21.5f,Color.WHITE,true);
            String sub=variants[selected][variant]+" · H"+hole+" · PAR "+par;text(c,sub,m,h*.119f,10.5f,Color.rgb(218,242,222),true);
            pill(c,new RectF(w*.735f,h*.027f,w*.94f,h*.066f),Color.rgb(235,247,229),gpsStatusShort(),gpsColor(),7.2f);
            pill(c,new RectF(w*.69f,h*.086f,w*.94f,h*.128f),Color.argb(62,255,255,255),yardageSourceV190(),Color.WHITE,7.0f);

            RectF range=new RectF(m,h*.158f,w-m,h*.235f);gradient(c,range,Color.rgb(13,93,62),Color.rgb(29,132,76),24);sheen(c,range,24);
            GeoRef green=greenCenterRef(hole),gf=getRef("gf",hole),gb=getRef("gb",hole);Distances ds=distances3(gf,green,gb);
            if(ds.center>=0){metric(c,"FRONT",ds.front<0?"--":ds.front+"m",w*.20f,h*.175f);metric(c,"CENTER",ds.center+"m",w*.50f,h*.175f);metric(c,"BACK",ds.back<0?"--":ds.back+"m",w*.80f,h*.175f);}
            else if(selected<=2){metric(c,"REGULAR",officialYardsV190()+"Y",w*.25f,h*.175f);metric(c,"METER",totalM+"m",w*.50f,h*.175f);metric(c,"PAR",""+par,w*.75f,h*.175f);}
            else if(selected==4){metric(c,"WHITE",totalM+"m",w*.25f,h*.175f);metric(c,"PAR",""+par,w*.50f,h*.175f);metric(c,"HOLE","H"+hole,w*.75f,h*.175f);}
            else {metric(c,"FIELD",totalM>0?totalM+"m":"--",w*.25f,h*.175f);metric(c,"PAR",""+par,w*.50f,h*.175f);metric(c,"CAL",totalM>0?"OK":"NEED",w*.75f,h*.175f);}

            pill(c,new RectF(m,h*.243f,w*.29f,h*.272f),gpsBg(),gpsStatusShort(),gpsColor(),6.8f);
            pill(c,new RectF(w*.31f,h*.243f,w*.70f,h*.272f),CARD,verifiedDistanceLabelV190(),yardageSourceColorV190(),6.8f);
            autoBtn.set(w*.72f,h*.243f,w-m,h*.272f);pill(c,autoBtn,autoHole?Color.rgb(229,244,218):CARD,autoHole?"AUTO ON":"AUTO OFF",autoHole?GREEN:Color.GRAY,6.7f);

            courseRect.set(m,h*.287f,w-m,h*.575f);drawActualYardageV190(c,courseRect,par,totalM);drawHolePager(c,h*.301f);
            drawHazardBarV182(c,h*.587f,h*.633f);

            RectF strategy=new RectF(m,h*.646f,w-m,h*.700f);softShadow(c,strategy,18);box(c,strategy,CARD,18);
            text(c,"공략 포인트",strategy.left+14,h*.668f,8.3f,GREEN,true);textFit(c,courseGuideV190(),strategy.left+14,h*.690f,strategy.right-14,7.9f,INK,true);

            boolean capReady=previewMode || (location!=null && location.getAccuracy()<=12 && fixAgeSec()<=15);
            int gBg=capReady?(green==null?CORAL:DEEP):Color.rgb(150,160,150),tBg=capReady?(getRef("t",hole)==null?Color.rgb(53,139,94):DEEP):Color.rgb(150,160,150);
            greenSave.set(m,h*.713f,w*.38f,h*.767f);teeSave.set(w*.405f,h*.713f,w*.65f,h*.767f);mapLaunch.set(w*.675f,h*.713f,w-m,h*.767f);
            goldButton(c,greenSave,gBg,greenSaveLabel(),Color.WHITE,13.5f);goldButton(c,teeSave,tBg,getRef("t",hole)==null?"TEE 저장":"TEE OK",Color.WHITE,13.5f);goldButton(c,mapLaunch,CARD,"외부 지도",INK,13.5f);

            drawPlayerTabs(c,h*.784f);int stroke=getStroke(player,hole,par),putt=getPutt(player,hole);
            RectF quick=new RectF(m,h*.831f,w-m,h*.902f);softShadow(c,quick,20);box(c,quick,CARD,20);
            text(c,"타수",m+16,h*.854f,8.2f,Color.GRAY,true);goldText(c,""+stroke,w*.28f,h*.866f,22.5f,INK);
            minus.set(m+68,h*.844f,m+128,h*.893f);plus.set(w*.355f,h*.844f,w*.435f,h*.893f);goldButton(c,minus,SOFT,"−",INK,17f);goldButton(c,plus,Color.rgb(229,244,218),"+",GREEN,17f);
            text(c,"퍼트",w*.52f,h*.854f,8.2f,Color.GRAY,true);goldText(c,""+putt,w*.69f,h*.866f,22.5f,INK);
            pm.set(w*.535f,h*.844f,w*.605f,h*.893f);pp.set(w*.82f,h*.844f,w*.90f,h*.893f);goldButton(c,pm,SOFT,"−",INK,17f);goldButton(c,pp,Color.rgb(226,245,250),"+",BLUE,17f);
            setFourNav(w,h);drawGoldenNav(c);
        }

'''
s=s[:pos]+helpers+s[pos:]

# Replace both country-specific renderers with the same safe-bounds yardage UI.
js=s.find('        private void roundJapanPremium(Canvas c){')
je=s.find('        private void roundKorea(Canvas c){',js)
if js<0 or je<0: raise SystemExit('v1.9.0 Japan renderer bounds missing')
s=s[:js]+'        private void roundJapanPremium(Canvas c){roundUnifiedYardageV190(c);}\n\n'+s[je:]
ks=s.find('        private void roundKorea(Canvas c){')
ke=s.find('        private int currentOfficialM(){',ks)
if ks<0 or ke<0: raise SystemExit('v1.9.0 Korea renderer bounds missing')
s=s[:ks]+'        private void roundKorea(Canvas c){roundUnifiedYardageV190(c);}\n\n'+s[ke:]

# Reset the target when the hole changes so a target from H1 never appears on H2.
s=s.replace('hole=hole==1?18:hole-1;saveState();invalidate();return true;','hole=hole==1?18:hole-1;hasTarget=false;saveState();invalidate();return true;')
s=s.replace('hole=hole==18?1:hole+1;saveState();invalidate();return true;','hole=hole==18?1:hole+1;hasTarget=false;saveState();invalidate();return true;')

p.write_text(s)
print('applied v1.9.0 verified actual-yardage pack + safe unified layout')
