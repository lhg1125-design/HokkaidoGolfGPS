from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.13.6 HOLE DETECT CONFIRM POPUP' not in s:
    raise SystemExit('cute popup polish requires hole-confirm popup')
MARK='V1.13.6 HOLE POPUP CUTE CHARACTER WALLPAPER + TTS'
if MARK in s:
    print('cute hole popup already applied')
    raise SystemExit(0)

# Extra state: speaker hit target + lazy Android TTS engine.
field='        private final RectF holeDetectAcceptV1136=new RectF(),holeDetectLaterV1136=new RectF(),holeDetectCloseV1136=new RectF();'
if field not in s:
    raise SystemExit('popup rect field anchor missing')
s=s.replace(field,field+r'''
        // V1.13.6 HOLE POPUP CUTE CHARACTER WALLPAPER + TTS
        private final RectF holeDetectSpeakV1136=new RectF();
        private android.speech.tts.TextToSpeech holeDetectTtsV1136=null;
''',1)

helper_anchor='        private void drawHoleDetectPopupV1136(Canvas c){'
idx=s.find(helper_anchor)
if idx<0:
    raise SystemExit('popup draw helper anchor missing')
helpers=r'''        private void drawHoleDetectCuteWallpaperV1136(Canvas c,RectF card,RectF head){
            // Reuse the same mascot renderer used by the approved storybook/home visual family.
            // Many low-alpha characters decorate the background, while the actual mini-map
            // and strategy panes remain opaque for field readability.
            int save=c.saveLayerAlpha(card.left,card.top,card.right,card.bottom,68);
            mascot(c,card.left+getWidth()*.075f,head.bottom+getHeight()*.045f,19,false);
            mascot(c,card.left+getWidth()*.165f,head.bottom+getHeight()*.028f,14,true);
            mascot(c,card.right-getWidth()*.095f,head.bottom+getHeight()*.050f,18,true);
            mascot(c,card.right-getWidth()*.180f,head.bottom+getHeight()*.032f,13,false);
            mascot(c,card.left+getWidth()*.070f,card.centerY()+getHeight()*.115f,16,true);
            mascot(c,card.right-getWidth()*.070f,card.centerY()+getHeight()*.120f,17,false);
            mascot(c,card.left+getWidth()*.150f,card.bottom-getHeight()*.105f,13,false);
            mascot(c,card.right-getWidth()*.150f,card.bottom-getHeight()*.105f,13,true);
            mascot(c,head.right-getWidth()*.070f,head.centerY()+2,20,true);
            mascot(c,head.right-getWidth()*.155f,head.centerY()+8,11,false);
            mascot(c,head.left+getWidth()*.410f,head.top+getHeight()*.028f,10,true);
            mascot(c,head.left+getWidth()*.480f,head.top+getHeight()*.071f,9,false);
            c.restoreToCount(save);

            // Tiny golf/storybook decorations: flags, balls, clouds and stars.
            p.setStyle(Paint.Style.FILL);
            p.setColor(Color.argb(78,87,159,98));
            float[][] balls={{.105f,.360f},{.880f,.365f},{.120f,.685f},{.855f,.695f},{.500f,.745f}};
            for(float[] b:balls)c.drawCircle(card.left+card.width()*b[0],card.top+card.height()*b[1],5.5f,p);
            p.setColor(Color.argb(88,247,126,86));
            float[][] flags={{.075f,.255f},{.915f,.250f},{.095f,.585f},{.900f,.590f}};
            for(float[] f:flags){
                float x=card.left+card.width()*f[0],y=card.top+card.height()*f[1];
                c.drawRect(x,y-15,x+2,y+11,p);Path fp=new Path();fp.moveTo(x+2,y-15);fp.lineTo(x+18,y-9);fp.lineTo(x+2,y-3);fp.close();c.drawPath(fp,p);
            }
            p.setColor(Color.argb(90,252,203,62));
            float[][] stars={{.275f,.055f},{.345f,.082f},{.675f,.060f},{.735f,.090f},{.510f,.030f}};
            for(float[] st:stars){float x=card.left+card.width()*st[0],y=card.top+card.height()*st[1];c.drawCircle(x,y,4,p);c.drawRect(x-1,y-8,x+1,y+8,p);c.drawRect(x-8,y-1,x+8,y+1,p);}
        }

        private void drawHoleDetectSpeakerV1136(Canvas c,RectF r){
            box(c,r,Color.rgb(235,247,239),16);
            p.setStyle(Paint.Style.STROKE);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeJoin(Paint.Join.ROUND);
            p.setStrokeWidth(3.2f);p.setColor(DEEP);
            float cx=r.centerX(),cy=r.centerY();
            Path sp=new Path();sp.moveTo(cx-15,cy-7);sp.lineTo(cx-7,cy-7);sp.lineTo(cx+3,cy-17);sp.lineTo(cx+3,cy+17);sp.lineTo(cx-7,cy+7);sp.lineTo(cx-15,cy+7);sp.close();c.drawPath(sp,p);
            c.drawArc(new RectF(cx-1,cy-13,cx+19,cy+13),-55,110,false,p);
            c.drawArc(new RectF(cx-4,cy-20,cx+29,cy+20),-50,100,false,p);
            p.setStrokeCap(Paint.Cap.BUTT);p.setStrokeJoin(Paint.Join.MITER);p.setStyle(Paint.Style.FILL);
        }

        private String holeDetectSpeechV1136(){
            return holeDetectCandidateV1136+"번 홀. 파 "+holeDetectParV1136(holeDetectCandidateV1136)+". "+holeDetectTotalV1136(holeDetectCandidateV1136)+"미터. 공략. "+holeDetectStrategyV1136(holeDetectCandidateV1136);
        }

        private void stopHoleDetectSpeechV1136(){
            try{if(holeDetectTtsV1136!=null)holeDetectTtsV1136.stop();}catch(Exception ignored){}
        }

        private void speakHoleDetectV1136(){
            final String spoken=holeDetectSpeechV1136();
            stopHoleDetectSpeechV1136();
            if(holeDetectTtsV1136==null){
                try{
                    holeDetectTtsV1136=new android.speech.tts.TextToSpeech(ctx,status->{
                        if(status==android.speech.tts.TextToSpeech.SUCCESS){
                            holeDetectTtsV1136.setLanguage(java.util.Locale.KOREAN);
                            holeDetectTtsV1136.setSpeechRate(.94f);
                            holeDetectTtsV1136.speak(spoken,android.speech.tts.TextToSpeech.QUEUE_FLUSH,null,"hole-v1136");
                        }
                    });
                }catch(Exception e){showToast("음성 읽기를 사용할 수 없어요");}
            }else{
                try{
                    holeDetectTtsV1136.setLanguage(java.util.Locale.KOREAN);
                    holeDetectTtsV1136.setSpeechRate(.94f);
                    holeDetectTtsV1136.speak(spoken,android.speech.tts.TextToSpeech.QUEUE_FLUSH,null,"hole-v1136");
                }catch(Exception e){showToast("음성 읽기를 사용할 수 없어요");}
            }
        }

        private void drawHoleDetectBigActionV1136(Canvas c,RectF r,String label,int bg,int fg,float size){
            softShadow(c,r,24);box(c,r,bg,24);
            text(c,label,r.centerX(),r.centerY()+getHeight()*.009f,size,fg,true,Paint.Align.CENTER);
        }

'''
s=s[:idx]+helpers+s[idx:]

# Put the character wallpaper behind all readable popup panes.
anchor='            RectF head=new RectF(card.left,card.top,card.right,card.top+h*.105f);box(c,head,Color.rgb(220,244,247),30);'
if anchor not in s:
    raise SystemExit('header wallpaper anchor missing')
s=s.replace(anchor,anchor+'\n            drawHoleDetectCuteWallpaperV1136(c,card,head);',1)

# The header already has one mascot. Keep it, but now it belongs to a larger family scene.

# Make PAR and distance approximately 2x larger and bold, as separate high-contrast values.
old='            text(c,"PAR "+holeDetectParV1136(holeDetectCandidateV1136)+"   ·   "+holeDetectTotalV1136(holeDetectCandidateV1136)+"m",info.left+w*.025f,info.top+h*.040f,13.5f,Color.rgb(169,119,33),true);\n            text(c,"공략 한 줄",info.left+w*.025f,info.top+h*.090f,14.5f,GREEN,true);\n            drawHoleDetectWrapV1136(c,holeDetectStrategyV1136(holeDetectCandidateV1136),info.left+w*.025f,info.top+h*.126f,info.right-w*.020f,h*.031f,11.5f,INK,4);'
new='            text(c,"PAR "+holeDetectParV1136(holeDetectCandidateV1136),info.left+w*.025f,info.top+h*.055f,25.5f,Color.rgb(169,119,33),true);\n            text(c,holeDetectTotalV1136(holeDetectCandidateV1136)+"m",info.left+w*.245f,info.top+h*.055f,26.5f,DEEP,true);\n            text(c,"공략법",info.left+w*.025f,info.top+h*.112f,18.5f,GREEN,true);\n            holeDetectSpeakV1136.set(info.right-w*.105f,info.top+h*.075f,info.right-w*.025f,info.top+h*.125f);\n            drawHoleDetectSpeakerV1136(c,holeDetectSpeakV1136);\n            drawHoleDetectWrapV1136(c,holeDetectStrategyV1136(holeDetectCandidateV1136),info.left+w*.025f,info.top+h*.155f,info.right-w*.020f,h*.037f,13.2f,INK,4);'
if old not in s:
    raise SystemExit('PAR/strategy typography anchor missing')
s=s.replace(old,new,1)

# Make bottom button labels about 50% larger and bold.
oldbtn='            drawApprovedActionV1136(c,holeDetectLaterV1136,"현재 홀 유지",Color.rgb(244,246,235),INK);\n            drawApprovedActionV1136(c,holeDetectAcceptV1136,"이 홀로 이동",Color.rgb(64,151,89),Color.WHITE);'
newbtn='            drawHoleDetectBigActionV1136(c,holeDetectLaterV1136,"현재 홀 유지",Color.rgb(244,246,235),INK,16.5f);\n            drawHoleDetectBigActionV1136(c,holeDetectAcceptV1136,"이 홀로 이동",Color.rgb(64,151,89),Color.WHITE,18.0f);'
if oldbtn not in s:
    raise SystemExit('bottom action anchor missing')
s=s.replace(oldbtn,newbtn,1)

# Candidate change / accept / dismiss should stop any old speech.
s=s.replace('        private void shiftHoleDetectCandidateV1136(int delta){\n            holeDetectCandidateV1136=',
            '        private void shiftHoleDetectCandidateV1136(int delta){\n            stopHoleDetectSpeechV1136();\n            holeDetectCandidateV1136=',1)
s=s.replace('        private void acceptHoleDetectV1136(){\n            int old=hole;',
            '        private void acceptHoleDetectV1136(){\n            stopHoleDetectSpeechV1136();\n            int old=hole;',1)
s=s.replace('        private void dismissHoleDetectV1136(){\n            holeDetectPopupV1136=false;',
            '        private void dismissHoleDetectV1136(){\n            stopHoleDetectSpeechV1136();\n            holeDetectPopupV1136=false;',1)

# Speaker touch owns the popup and reads candidate hole + PAR + total + strategy.
touch='            if(holeDetectPopupV1136){\n                if(holeDetectPrevV1136.contains(x,y)){shiftHoleDetectCandidateV1136(-1);return true;}'
if touch not in s:
    raise SystemExit('popup touch anchor missing')
s=s.replace(touch,'            if(holeDetectPopupV1136){\n                if(holeDetectSpeakV1136.contains(x,y)){speakHoleDetectV1136();return true;}\n                if(holeDetectPrevV1136.contains(x,y)){shiftHoleDetectCandidateV1136(-1);return true;}',1)

p.write_text(s)
print('applied V1.13.6 HOLE POPUP CUTE CHARACTER WALLPAPER + TTS: dense mascots, 2x PAR/distance, bold strategy, 1.5x buttons, speaker readout')
