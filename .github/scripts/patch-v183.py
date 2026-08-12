from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.8.2 · YARDAGE + UX' not in s:
    raise SystemExit('v1.8.3 requires v1.8.2')
s=s.replace('V1.8.2 · YARDAGE + UX','V1.8.3 · CLEAN YARDAGE UX',1)

# -----------------------------------------------------------------------------
# Score input: remove baked artwork/background and rebuild the 3/4-player cards
# with a clear top name row and a separate control row. No text/button overlap.
# -----------------------------------------------------------------------------
start=s.find('        private void scoreInput(Canvas c){')
end=s.find('        private void summary(Canvas c){',start)
if start<0 or end<0:
    raise SystemExit('v1.8.3 scoreInput bounds missing')
score=r'''        private void scoreInput(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;int par=currentPar();int n=playerCount();if(player>=n)player=0;
            c.drawColor(BG);
            RectF head=new RectF(0,0,w,h*.158f);gradient(c,head,DEEP,GREEN,0);
            text(c,"SCORE INPUT",m,h*.037f,8.5f,Color.rgb(215,241,222),true);
            text(c,"스코어 입력",m,h*.083f,27,Color.WHITE,true);
            text(c,ko[selected]+" / H"+hole+" / PAR "+par+" · "+n+"명",m,h*.122f,11.5f,Color.rgb(218,242,222),true);
            playerNamesBtn.set(w*.68f,h*.062f,w*.945f,h*.122f);
            goldButton(c,playerNamesBtn,Color.argb(62,255,255,255),"플레이어 설정 · "+n+"명",Color.WHITE,12.0f);
            drawHolePager(c,h*.177f);
            text(c,"홀 이동",w*.50f,h*.183f,7.0f,Color.GRAY,true,Paint.Align.CENTER);

            float areaTop=h*.215f,areaBottom=h*.895f,gap=h*.012f;
            float rowH=(areaBottom-areaTop-gap*(n-1))/n;int[] dots={GREEN,SKY,CORAL,YELLOW};
            for(int i=0;i<4;i++){inputStrokeMinus[i].setEmpty();inputStrokePlus[i].setEmpty();inputPuttMinus[i].setEmpty();inputPuttPlus[i].setEmpty();}
            for(int pl=0;pl<n;pl++){
                float y=areaTop+pl*(rowH+gap);RectF card=new RectF(m,y,w-m,y+rowH);
                softShadow(c,card,24);box(c,card,CARD,24);
                float ch=card.height();
                RectF tag=new RectF(card.left+14,card.top+12,card.left+150,card.top+50);box(c,tag,dots[pl],18);
                goldText(c,playerName(pl),tag.centerX(),tag.centerY(),15.5f,Color.WHITE);
                int st=getStroke(pl,hole,par),pu=getPutt(pl,hole),delta=st-par;String rel=delta==0?"E":(delta>0?"+"+delta:""+delta);
                pill(c,new RectF(card.right-84,card.top+13,card.right-16,card.top+49),delta>0?Color.rgb(255,238,229):(delta<0?Color.rgb(229,244,218):SOFT),rel,delta>0?CORAL:(delta<0?GREEN:INK),8.8f);

                float labelY=card.top+ch*.50f,btnTop=card.bottom-57,btnBottom=card.bottom-10;
                float mid=card.centerX();
                text(c,"타수",card.left+22,labelY,8.2f,Color.GRAY,true);
                inputStrokeMinus[pl].set(card.left+82,btnTop,card.left+142,btnBottom);
                inputStrokePlus[pl].set(card.left+286,btnTop,card.left+346,btnBottom);
                goldButton(c,inputStrokeMinus[pl],SOFT,"−",INK,18f);goldText(c,""+st,card.left+218,(btnTop+btnBottom)/2f,25f,INK);goldButton(c,inputStrokePlus[pl],Color.rgb(229,244,218),"+",GREEN,18f);

                text(c,"퍼트",mid+8,labelY,8.2f,Color.GRAY,true);
                inputPuttMinus[pl].set(mid+62,btnTop,mid+122,btnBottom);
                inputPuttPlus[pl].set(card.right-78,btnTop,card.right-18,btnBottom);
                goldButton(c,inputPuttMinus[pl],SOFT,"−",INK,18f);goldText(c,""+pu,mid+188,(btnTop+btnBottom)/2f,25f,INK);goldButton(c,inputPuttPlus[pl],Color.rgb(226,245,250),"+",BLUE,18f);
            }
            setFourNav(w,h);drawGoldenNav(c);
        }

'''
s=s[:start]+score+s[end:]

# -----------------------------------------------------------------------------
# Korea 2D yardage: remove the white distance/calibration chips that sat on top
# of the fairway image. Factual distance remains in the dedicated metric card
# above; the map remains a clean hole guide.
# -----------------------------------------------------------------------------
ks=s.find('        private void drawKoreaYardage(Canvas c,RectF r,int par,int officialM){')
ke=s.find('        private void round(Canvas c){',ks)
if ks<0 or ke<0:
    raise SystemExit('v1.8.3 Korea yardage bounds missing')
clean=r'''        private void drawKoreaYardage(Canvas c,RectF r,int par,int officialM){
            float w=r.width(),hh=r.height();gradient(c,r,Color.rgb(228,246,216),Color.rgb(193,231,187),30);c.save();c.clipRect(r);
            int seed=hole*31+variant*17+selected*7;float bend=((seed%7)-3)*w*.020f,cx=r.centerX();
            Path fw=new Path();fw.moveTo(cx-w*.075f,r.bottom-22);fw.cubicTo(cx+w*.03f+bend,r.top+hh*.72f,cx-w*.10f+bend,r.top+hh*.38f,cx-w*.055f+bend,r.top+64);fw.lineTo(cx+w*.060f+bend,r.top+64);fw.cubicTo(cx+w*.15f+bend,r.top+hh*.38f,cx+w*.11f+bend,r.top+hh*.72f,cx+w*.075f,r.bottom-22);fw.close();p.setColor(Color.rgb(83,171,84));c.drawPath(fw,p);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3);p.setColor(Color.argb(65,255,255,255));for(int k=1;k<4;k++){float y=r.bottom-k*hh*.20f;c.drawLine(r.left+20,y,r.right-20,y,p);}p.setStyle(Paint.Style.FILL);
            p.setColor(DEEP);c.drawRoundRect(new RectF(cx-30,r.bottom-34,cx+30,r.bottom-20),7,7,p);text(c,"TEE",cx,r.bottom-42,6.5f,DEEP,true,Paint.Align.CENTER);
            if(selected==3){
                boolean second=hole>9;String active=(variant==0?(second?"Y":"R"):(second?"R":"Y"));
                p.setColor(Color.rgb(55,141,74));c.drawOval(new RectF(cx-82,r.top+34,cx-18,r.top+67),p);c.drawOval(new RectF(cx+18,r.top+34,cx+82,r.top+67),p);
                p.setColor(active.equals("R")?Color.rgb(215,48,55):Color.rgb(245,195,32));float gx=active.equals("R")?cx-50:cx+50;c.drawCircle(gx,r.top+49,7,p);
                pill(c,new RectF(r.left+16,r.top+14,r.left+w*.40f,r.top+47),Color.argb(235,255,255,255),"2D GUIDE · "+(active.equals("R")?"RED GREEN":"YELLOW GREEN"),DEEP,6.4f);
            }else{
                p.setColor(Color.rgb(48,135,70));c.drawOval(new RectF(cx-50+bend,r.top+34,cx+50+bend,r.top+68),p);p.setColor(CORAL);c.drawRect(cx+bend,r.top+20,cx+bend+3,r.top+50,p);Path fl=new Path();fl.moveTo(cx+bend+3,r.top+20);fl.lineTo(cx+bend+27,r.top+28);fl.lineTo(cx+bend+3,r.top+35);fl.close();c.drawPath(fl,p);
                pill(c,new RectF(r.left+16,r.top+14,r.left+w*.42f,r.top+47),Color.argb(238,255,255,255),"2D GUIDE · WHITE · PAR "+par,DEEP,6.2f);
            }
            Hazard[] hz=hazardsForHole();for(int i=0;i<hz.length;i++){Hazard z=hz[i];float x=r.left+z.x*r.width(),y=r.bottom-z.y*r.height();int cc=z.type.equals("WATER")?BLUE:YELLOW;p.setColor(Color.argb(235,255,255,255));c.drawCircle(x,y,17,p);p.setColor(cc);c.drawCircle(x,y,11,p);goldText(c,z.type.equals("WATER")?"W":"B",x,y,7.0f,z.type.equals("WATER")?Color.WHITE:DEEP);}
            c.restore();
        }

'''
s=s[:ks]+clean+s[ke:]

p.write_text(s)
print('applied v1.8.3 clean score input + uncluttered Korea yardage')
