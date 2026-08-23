from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.13.6 HOLE DETECT CONFIRM POPUP' not in s:
    raise SystemExit('hole popup polish requires confirm popup')

MARK='V1.13.6 HOLE POPUP POLISH TTS'
if MARK in s:
    print('hole popup polish already applied')
    raise SystemExit(0)

# Add popup-only speaker/TTS state. Keep it local to the GolfView so it works
# without network access and uses the device's installed Android TTS engine.
field='''        private final RectF holeDetectAcceptV1136=new RectF(),holeDetectLaterV1136=new RectF(),holeDetectCloseV1136=new RectF();'''
if field not in s:
    raise SystemExit('popup field anchor missing')
s=s.replace(field,field+r'''
        // V1.13.6 HOLE POPUP POLISH TTS
        private final RectF holeDetectSpeakV1136=new RectF();
        private android.speech.tts.TextToSpeech holeDetectTtsV1136=null;
        private boolean holeDetectTtsReadyV1136=false;
''',1)

# Initialize Korean TTS after the view context has been assigned. Failure is
# non-fatal; the visual popup remains fully usable.
ctor='''            setKeepScreenOn(true);'''
if ctor not in s:
    raise SystemExit('GolfView constructor anchor missing')
s=s.replace(ctor,ctor+r'''
            holeDetectTtsV1136=new android.speech.tts.TextToSpeech(ctx,new android.speech.tts.TextToSpeech.OnInitListener(){
                @Override public void onInit(int status){
                    if(status==android.speech.tts.TextToSpeech.SUCCESS && holeDetectTtsV1136!=null){
                        int r=holeDetectTtsV1136.setLanguage(new java.util.Locale("ko","KR"));
                        holeDetectTtsReadyV1136=(r!=android.speech.tts.TextToSpeech.LANG_MISSING_DATA && r!=android.speech.tts.TextToSpeech.LANG_NOT_SUPPORTED);
                        if(holeDetectTtsReadyV1136){holeDetectTtsV1136.setSpeechRate(.92f);holeDetectTtsV1136.setPitch(1.03f);}
                    }
                }
            });
''',1)

# Stop the engine when the custom view is detached.
helper_anchor='''        private void openHoleDetectPopupV1136(int candidate){'''
idx=s.find(helper_anchor)
if idx<0:
    raise SystemExit('popup helper insertion anchor missing')
helpers=r'''        @Override protected void onDetachedFromWindow(){
            if(holeDetectTtsV1136!=null){try{holeDetectTtsV1136.stop();holeDetectTtsV1136.shutdown();}catch(Exception ignored){}}
            super.onDetachedFromWindow();
        }

        private void speakHoleDetectStrategyV1136(){
            if(!holeDetectTtsReadyV1136 || holeDetectTtsV1136==null){showToast("읽어주기 엔진을 확인해주세요");return;}
            int h=holeDetectCandidateV1136;
            String msg=h+"번 홀. 파 "+holeDetectParV1136(h)+". "+holeDetectTotalV1136(h)+"미터. 공략. "+holeDetectStrategyV1136(h);
            try{holeDetectTtsV1136.speak(msg,android.speech.tts.TextToSpeech.QUEUE_FLUSH,null,"hole_strategy_v1136");}
            catch(Exception e){showToast("읽어주기를 시작하지 못했습니다");}
        }

        private void drawHoleDetectSpeakerV1136(Canvas c,RectF r){
            box(c,r,Color.rgb(235,247,239),18);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2.6f);p.setStrokeCap(Paint.Cap.ROUND);p.setColor(Color.rgb(43,126,78));
            float cx=r.left+r.width()*.38f,cy=r.centerY();
            Path sp=new Path();sp.moveTo(r.left+r.width()*.17f,cy-r.height()*.11f);sp.lineTo(cx-r.width()*.04f,cy-r.height()*.11f);sp.lineTo(cx+r.width()*.13f,cy-r.height()*.27f);sp.lineTo(cx+r.width()*.13f,cy+r.height()*.27f);sp.lineTo(cx-r.width()*.04f,cy+r.height()*.11f);sp.lineTo(r.left+r.width()*.17f,cy+r.height()*.11f);sp.close();c.drawPath(sp,p);
            RectF a1=new RectF(cx+r.width()*.06f,cy-r.height()*.22f,cx+r.width()*.45f,cy+r.height()*.22f);c.drawArc(a1,-48,96,false,p);
            RectF a2=new RectF(cx-r.width()*.01f,cy-r.height()*.32f,cx+r.width()*.60f,cy+r.height()*.32f);c.drawArc(a2,-45,90,false,p);
            p.setStyle(Paint.Style.FILL);p.setStrokeCap(Paint.Cap.BUTT);
        }

        private void drawHoleDetectPopupButtonV1136(Canvas c,RectF r,String label,int bg,int fg){
            softShadow(c,r,20);box(c,r,bg,20);
            textFit(c,label,r.left+r.width()*.07f,r.centerY()+7,r.right-r.width()*.07f,20.7f,fg,true);
        }

'''
s=s[:idx]+helpers+s[idx:]

# Candidate changes stop current speech so the spoken information never refers
# to a previous mini-map.
shift='''        private void shiftHoleDetectCandidateV1136(int delta){\n            holeDetectCandidateV1136=Math.max(1,Math.min(18,holeDetectCandidateV1136+delta));\n            invalidate();\n        }'''
shift_new='''        private void shiftHoleDetectCandidateV1136(int delta){\n            if(holeDetectTtsV1136!=null){try{holeDetectTtsV1136.stop();}catch(Exception ignored){}}\n            holeDetectCandidateV1136=Math.max(1,Math.min(18,holeDetectCandidateV1136+delta));\n            invalidate();\n        }'''
if shift in s:s=s.replace(shift,shift_new,1)

# Make PAR and official distance approximately 2x the previous 13.5sp size,
# separated into two large chips so the text stays readable without squeezing.
old='''            text(c,"PAR "+holeDetectParV1136(holeDetectCandidateV1136)+"   ·   "+holeDetectTotalV1136(holeDetectCandidateV1136)+"m",info.left+w*.025f,info.top+h*.040f,13.5f,Color.rgb(169,119,33),true);\n            text(c,"공략 한 줄",info.left+w*.025f,info.top+h*.090f,14.5f,GREEN,true);\n            drawHoleDetectWrapV1136(c,holeDetectStrategyV1136(holeDetectCandidateV1136),info.left+w*.025f,info.top+h*.126f,info.right-w*.020f,h*.031f,11.5f,INK,4);'''
new='''            RectF parBig=new RectF(info.left+w*.020f,info.top+h*.014f,info.left+w*.205f,info.top+h*.078f);\n            RectF distBig=new RectF(info.left+w*.220f,info.top+h*.014f,info.right-w*.020f,info.top+h*.078f);\n            box(c,parBig,Color.rgb(255,247,218),18);box(c,distBig,Color.rgb(239,248,220),18);\n            text(c,"PAR "+holeDetectParV1136(holeDetectCandidateV1136),parBig.centerX(),parBig.centerY()+9,27.0f,Color.rgb(157,105,24),true,Paint.Align.CENTER);\n            text(c,holeDetectTotalV1136(holeDetectCandidateV1136)+"m",distBig.centerX(),distBig.centerY()+9,27.0f,DEEP,true,Paint.Align.CENTER);\n            text(c,"공략법",info.left+w*.025f,info.top+h*.118f,18.5f,GREEN,true);\n            holeDetectSpeakV1136.set(info.right-w*.105f,info.top+h*.087f,info.right-w*.020f,info.top+h*.143f);\n            drawHoleDetectSpeakerV1136(c,holeDetectSpeakV1136);\n            drawHoleDetectWrapV1136(c,holeDetectStrategyV1136(holeDetectCandidateV1136),info.left+w*.025f,info.top+h*.166f,info.right-w*.020f,h*.040f,15.5f,INK,4);'''
if old not in s:
    raise SystemExit('popup info typography anchor missing')
s=s.replace(old,new,1)

# Popup buttons are 50% larger than the former 13.8sp approved-action label.
s=s.replace('''            drawApprovedActionV1136(c,holeDetectLaterV1136,"현재 홀 유지",Color.rgb(244,246,235),INK);\n            drawApprovedActionV1136(c,holeDetectAcceptV1136,"이 홀로 이동",Color.rgb(64,151,89),Color.WHITE);''',
'''            drawHoleDetectPopupButtonV1136(c,holeDetectLaterV1136,"현재 홀 유지",Color.rgb(244,246,235),INK);\n            drawHoleDetectPopupButtonV1136(c,holeDetectAcceptV1136,"이 홀로 이동",Color.rgb(64,151,89),Color.WHITE);''',1)

# Speaker owns its own touch target while the popup is open.
touch='''                if(holeDetectNextV1136.contains(x,y)){shiftHoleDetectCandidateV1136(1);return true;}'''
if touch not in s:
    raise SystemExit('popup speaker touch anchor missing')
s=s.replace(touch,touch+'\n                if(holeDetectSpeakV1136.contains(x,y)){speakHoleDetectStrategyV1136();return true;}',1)

p.write_text(s)
print('applied V1.13.6 HOLE POPUP POLISH TTS: real mini-yardage, 2x PAR/distance, bold strategy, 1.5x buttons, offline Android TTS')
