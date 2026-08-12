from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('v1.2.2 missing '+label)
    s=s.replace(old,new,1)

# Course selector buttons: cover the small baked text and use the same 2x control typography.
rep('''            if(selected>=0){
                box(c,varA,variant==0?GREEN:SOFT,34);box(c,varB,variant==1?GREEN:SOFT,34);
                text(c,variants[selected][0],varA.centerX(),varA.centerY()+7,10,variant==0?Color.WHITE:INK,true,Paint.Align.CENTER);
                text(c,variants[selected][1],varB.centerX(),varB.centerY()+7,10,variant==1?Color.WHITE:INK,true,Paint.Align.CENTER);
            }''','''            if(selected>=0){
                goldButton(c,varA,variant==0?GREEN:SOFT,variants[selected][0],variant==0?Color.WHITE:INK,19.6f);
                goldButton(c,varB,variant==1?GREEN:SOFT,variants[selected][1],variant==1?Color.WHITE:INK,19.6f);
            }''','home selector typography')

# Main round controls: increase the control height ~22%, double text size, and use optical vertical centering.
rep('''            greenSave.set(w*.055f,h*.752f,w*.38f,h*.794f);teeSave.set(w*.403f,h*.752f,w*.65f,h*.794f);mapLaunch.set(w*.67f,h*.752f,w*.945f,h*.794f);
            box(c,greenSave,green==null?CORAL:DEEP,28);box(c,teeSave,getRef("t",hole)==null?Color.rgb(53,139,94):DEEP,28);
            text(c,greenSaveLabel(),greenSave.centerX(),greenSave.centerY()+6,8.2f,Color.WHITE,true,Paint.Align.CENTER);
            text(c,getRef("t",hole)==null?"TEE 저장":"TEE OK",teeSave.centerX(),teeSave.centerY()+6,8.2f,Color.WHITE,true,Paint.Align.CENTER);
            drawPlayerTabs(c,h*.815f);''','''            greenSave.set(w*.055f,h*.744f,w*.38f,h*.806f);teeSave.set(w*.403f,h*.744f,w*.65f,h*.806f);mapLaunch.set(w*.67f,h*.744f,w*.945f,h*.806f);
            goldButton(c,greenSave,green==null?CORAL:DEEP,greenSaveLabel(),Color.WHITE,19.6f);
            goldButton(c,teeSave,getRef("t",hole)==null?Color.rgb(53,139,94):DEEP,getRef("t",hole)==null?"TEE 저장":"TEE OK",Color.WHITE,19.6f);
            goldButton(c,mapLaunch,CARD,"외부 지도",INK,19.6f);
            drawPlayerTabs(c,h*.815f);''','round action buttons')

# The V1.2 artwork contains a baked small nav. Cover it with one clean rounded navigation bar and larger labels.
rep('''            prev.set(w*.055f,h*.933f,w*.27f,h*.979f);mapTab.set(w*.28f,h*.933f,w*.49f,h*.979f);scoreTab.set(w*.51f,h*.933f,w*.73f,h*.979f);next.set(w*.74f,h*.933f,w*.945f,h*.979f);
            autoBtn.set(w*.75f,h*.215f,w*.94f,h*.25f);''','''            prev.set(w*.055f,h*.925f,w*.27f,h*.981f);mapTab.set(w*.28f,h*.925f,w*.49f,h*.981f);scoreTab.set(w*.51f,h*.925f,w*.73f,h*.981f);next.set(w*.74f,h*.925f,w*.945f,h*.981f);
            drawGoldenNav(c);
            autoBtn.set(w*.75f,h*.215f,w*.94f,h*.25f);''','round nav')

rep('''            prev.set(w*.055f,h*.933f,w*.27f,h*.979f);mapTab.set(w*.28f,h*.933f,w*.49f,h*.979f);scoreTab.set(w*.51f,h*.933f,w*.73f,h*.979f);next.set(w*.74f,h*.933f,w*.945f,h*.979f);
        }''','''            prev.set(w*.055f,h*.925f,w*.27f,h*.981f);mapTab.set(w*.28f,h*.925f,w*.49f,h*.981f);scoreTab.set(w*.51f,h*.925f,w*.73f,h*.981f);next.set(w*.74f,h*.925f,w*.945f,h*.981f);
            drawGoldenNav(c);
        }''','score nav')

old_tabs='''        private void drawPlayerTabs(Canvas c,float y){
            float w=getWidth(),m=w*.045f,gap=6,avail=w-2*m,ww=(avail-gap*3)/4;int[] dots={GREEN,SKY,CORAL,YELLOW};
            for(int i=0;i<4;i++){float l=m+i*(ww+gap);playerTabs[i].set(l,y,l+ww,y+34);box(c,playerTabs[i],player==i?GREEN:CARD,18);p.setColor(dots[i]);c.drawCircle(l+13,y+17,4,p);text(c,"P"+(i+1),l+ww/2+6,y+22,10,player==i?Color.WHITE:INK,true,Paint.Align.CENTER);}
        }'''
new_tabs='''        private void drawPlayerTabs(Canvas c,float y){
            float w=getWidth(),h=getHeight(),m=w*.055f,gap=w*.012f,avail=w-2*m,ww=(avail-gap*3)/4,tabH=h*.034f;int[] dots={GREEN,SKY,CORAL,YELLOW};
            for(int i=0;i<4;i++){
                float l=m+i*(ww+gap);playerTabs[i].set(l,y,l+ww,y+tabH);
                int bg=player==i?GREEN:CARD,fg=player==i?Color.WHITE:INK;
                softShadow(c,playerTabs[i],tabH*.382f);box(c,playerTabs[i],bg,tabH*.382f);
                p.setColor(dots[i]);c.drawCircle(l+ww*.17f,y+tabH*.50f,Math.max(5f,tabH*.065f),p);
                goldText(c,"P"+(i+1),l+ww*.57f,y+tabH*.50f,20.0f,fg);
            }
        }'''
rep(old_tabs,new_tabs,'player tabs')

# New control typography helpers. 19.6sp is exactly 2x the former 9.8sp pillButton size.
marker='''        private void metric(Canvas c,String lab,String val,float x,float y){text(c,lab,x,y,9,Color.rgb(212,237,219),true,Paint.Align.CENTER);text(c,val,x,y+getHeight()*.040f,19,Color.WHITE,true,Paint.Align.CENTER);}
'''
helpers='''        private void goldText(Canvas c,String s,float x,float cy,float sp,int fg){
            p.setShader(null);p.setStyle(Paint.Style.FILL);p.setColor(fg);p.setTextAlign(Paint.Align.CENTER);
            p.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));
            p.setTextSize(sp*getResources().getDisplayMetrics().scaledDensity);
            Paint.FontMetrics fm=p.getFontMetrics();float baseline=cy-(fm.ascent+fm.descent)/2f;
            c.drawText(s,x,baseline,p);
        }
        private void goldButton(Canvas c,RectF r,int bg,String s,int fg,float sp){
            float rad=r.height()*.382f;
            softShadow(c,r,rad);box(c,r,bg,rad);goldText(c,s,r.centerX(),r.centerY(),sp,fg);
        }
        private void drawGoldenNav(Canvas c){
            float w=getWidth(),h=getHeight();RectF bar=new RectF(w*.045f,h*.918f,w*.955f,h*.985f);
            softShadow(c,bar,bar.height()*.382f);box(c,bar,CARD,bar.height()*.382f);
            goldText(c,"‹ 이전",prev.centerX(),bar.centerY(),18.5f,INK);
            goldText(c,"코스",mapTab.centerX(),bar.centerY(),18.5f,screen==1?GREEN:INK);
            goldText(c,"스코어",scoreTab.centerX(),bar.centerY(),18.5f,screen==2?GREEN:INK);
            goldText(c,"다음 ›",next.centerX(),bar.centerY(),18.5f,INK);
        }
'''
rep(marker,marker+helpers,'golden control helpers')

s=s.replace('V1.2.1 · ARTWORK FIDELITY','V1.2.2 · ARTWORK FIDELITY')
p.write_text(s)
print('applied v1.2.2 2x control typography + golden-ratio spacing')
