from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

start=s.find('        private void score(Canvas c){')
end=s.find('        private void saveRef(', start)
if start < 0 or end < 0:
    raise SystemExit('v1.3 score block not found')

score=r'''        private void score(Canvas c){
            float w=getWidth(),h=getHeight(),m=w*.045f;
            c.drawBitmap(v12Score,null,new RectF(0,0,w,h),p);

            // Cover the baked small table and rebuild it as two 9-hole cards.
            RectF clean=new RectF(w*.025f,h*.118f,w*.975f,h*.905f);
            box(c,clean,Color.rgb(249,250,240),34);
            text(c,"스코어카드",m,h*.083f,29,Color.WHITE,true);
            text(c,ko[selected]+" / "+variants[selected][variant],m,h*.112f,14,Color.rgb(218,242,222),true);

            float leftL=w*.045f,leftR=w*.495f,rightL=w*.505f,rightR=w*.955f;
            float top=h*.145f,bottom=h*.705f;
            RectF outCard=new RectF(leftL,top,leftR,bottom);
            RectF inCard=new RectF(rightL,top,rightR,bottom);
            softShadow(c,outCard,30); box(c,outCard,CARD,30);
            softShadow(c,inCard,30); box(c,inCard,CARD,30);

            RectF outHead=new RectF(leftL+8,top+8,leftR-8,top+h*.052f);
            RectF inHead=new RectF(rightL+8,top+8,rightR-8,top+h*.052f);
            box(c,outHead,DEEP,22); box(c,inHead,GREEN,22);
            goldText(c,"OUT · 1–9",outHead.centerX(),outHead.centerY(),18.5f,Color.WHITE);
            goldText(c,"IN · 10–18",inHead.centerX(),inHead.centerY(),18.5f,Color.WHITE);

            float headerY=top+h*.078f;
            drawScoreHeader(c,leftL,leftR,headerY);
            drawScoreHeader(c,rightL,rightR,headerY);

            int[] totals={0,0,0,0},puts={0,0,0,0};
            int parTotal=0;
            float firstY=top+h*.122f,rowStep=h*.0552f;
            for(int i=1;i<=18;i++){
                int pa=parForHole(i); parTotal+=pa;
                int row=(i-1)%9;
                float l=i<=9?leftL:rightL, r=i<=9?leftR:rightR;
                float y=firstY+row*rowStep;
                if(row%2==1){
                    RectF stripe=new RectF(l+10,y-h*.020f,r-10,y+h*.026f);
                    box(c,stripe,Color.rgb(247,249,242),14);
                }
                float[] xs=scoreColumns(l,r);
                goldText(c,""+i,xs[0],y,16.8f,INK);
                goldText(c,""+pa,xs[1],y,16.8f,Color.GRAY);
                for(int pl=0;pl<4;pl++){
                    int sv=getStroke(pl,i,pa); totals[pl]+=sv; puts[pl]+=getPutt(pl,i);
                    int col=sv>pa?CORAL:(sv<pa?GREEN:INK);
                    goldText(c,""+sv,xs[2+pl],y,18.4f,col);
                }
                if(i==hole){
                    p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(4);p.setColor(YELLOW);
                    c.drawRoundRect(new RectF(l+8,y-h*.025f,r-8,y+h*.029f),18,18,p);
                    p.setStyle(Paint.Style.FILL);
                }
            }

            RectF summary=new RectF(w*.045f,h*.730f,w*.955f,h*.895f);
            gradient(c,summary,DEEP,GREEN,34); sheen(c,summary,34);
            goldText(c,"ROUND SUMMARY",summary.centerX(),h*.758f,17.5f,Color.rgb(218,242,222));
            float cardGap=w*.012f,cardW=(summary.width()-w*.05f-cardGap*3)/4f;
            for(int pl=0;pl<4;pl++){
                float l=summary.left+w*.025f+pl*(cardW+cardGap);
                RectF pc=new RectF(l,h*.775f,l+cardW,h*.875f);
                box(c,pc,Color.argb(42,255,255,255),22);
                goldText(c,"P"+(pl+1),pc.centerX(),h*.798f,16.0f,Color.rgb(218,242,222));
                int delta=totals[pl]-parTotal;
                String rel=delta==0?"E":(delta>0?"+"+delta:""+delta);
                goldText(c,""+totals[pl],pc.centerX(),h*.833f,32.0f,Color.WHITE);
                goldText(c,rel+"  ·  퍼트 "+puts[pl],pc.centerX(),h*.862f,14.5f,Color.WHITE);
            }

            prev.set(w*.055f,h*.925f,w*.27f,h*.981f);
            mapTab.set(w*.28f,h*.925f,w*.49f,h*.981f);
            scoreTab.set(w*.51f,h*.925f,w*.73f,h*.981f);
            next.set(w*.74f,h*.925f,w*.945f,h*.981f);
            drawGoldenNav(c);
        }

        private float[] scoreColumns(float l,float r){
            float ww=r-l;
            return new float[]{l+ww*.075f,l+ww*.205f,l+ww*.385f,l+ww*.555f,l+ww*.725f,l+ww*.895f};
        }

        private void drawScoreHeader(Canvas c,float l,float r,float y){
            float[] xs=scoreColumns(l,r);
            String[] labs={"H","PAR","P1","P2","P3","P4"};
            for(int i=0;i<labs.length;i++) goldText(c,labs[i],xs[i],y,15.5f,i<2?Color.GRAY:GREEN);
        }
'''

s=s[:start]+score+'\n'+s[end:]
s=s.replace('V1.2.2 · ARTWORK FIDELITY','V1.3 · SCORECARD XL')
p.write_text(s)
print('applied v1.3 scorecard XL: 2x table fonts + OUT/IN split + round summary')
