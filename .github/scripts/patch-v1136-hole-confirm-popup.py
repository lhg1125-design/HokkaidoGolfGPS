from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.13.6 APPROVED UI HOTFIX' not in s:
    raise SystemExit('hole-confirm popup requires approved UI')
if 'private int approvedRemainingV1136(' not in s:
    raise SystemExit('hole-confirm popup requires TEE-first remaining distance')

MARK='V1.13.6 HOLE DETECT CONFIRM POPUP'
if MARK in s:
    print('hole-detect confirm popup already applied')
    raise SystemExit(0)

# -----------------------------------------------------------------------------
# State: auto detection only proposes a candidate. The actual active hole changes
# only after explicit user confirmation from the storybook popup.
# -----------------------------------------------------------------------------
field_anchor='        private long lastRoundLogElapsedV1136=0L;'
if field_anchor not in s:
    raise SystemExit('round-log field anchor missing')
s=s.replace(field_anchor,field_anchor+r'''
        // V1.13.6 HOLE DETECT CONFIRM POPUP
        private boolean holeDetectPopupV1136=false;
        private int holeDetectCandidateV1136=1;
        private long holeDetectSuppressUntilV1136=0L;
        private boolean holeExitArmedV1136=false;
        private int holeExitArmedHoleV1136=-1;
        private double holeExitLatV1136=999, holeExitLonV1136=999;
        private long holeExitAtV1136=0L;
        private final RectF holeDetectPrevV1136=new RectF(),holeDetectNextV1136=new RectF();
        private final RectF holeDetectAcceptV1136=new RectF(),holeDetectLaterV1136=new RectF(),holeDetectCloseV1136=new RectF();
''',1)


def replace_method(src, signature, body):
    start=src.find(signature)
    if start<0:
        raise SystemExit('missing method '+signature)
    brace=src.find('{',start)
    depth=0;end=None
    for i in range(brace,len(src)):
        if src[i]=='{': depth+=1
        elif src[i]=='}':
            depth-=1
            if depth==0:
                end=i+1;break
    if end is None:
        raise SystemExit('unbalanced method '+signature)
    return src[:start]+body+src[end:]

# Conservative first-visit auto detector. The golfer does not need learned future
# tee coordinates. After the current hole reaches its finish zone and the golfer
# leaves that zone, the app proposes H+1. It NEVER commits the change by itself.
auto_body=r'''        private void maybeAutoHole(){
            if(!autoHole || selected<0 || hole>=18 || location==null || !navGpsUsableV1133())return;
            long now=SystemClock.uptimeMillis();
            if(holeDetectPopupV1136 || now<holeDetectSuppressUntilV1136)return;
            GeoRef tee=getRef("t",hole);
            if(tee==null){holeExitArmedV1136=false;holeExitArmedHoleV1136=-1;return;}
            int total=verifiedMetersV190();if(total<=0)total=(int)Math.round(currentYards()*.9144);if(total<=0)return;
            int remain=approvedRemainingV1136(total,greenCenterRef(hole));if(remain<0)return;
            if(holeExitArmedHoleV1136!=hole){holeExitArmedV1136=false;holeExitArmedHoleV1136=hole;}
            float finishBand=Math.max(25f,Math.min(45f,total*.08f));
            if(!holeExitArmedV1136){
                if(remain<=finishBand){
                    holeExitArmedV1136=true;holeExitAtV1136=now;
                    holeExitLatV1136=location.getLatitude();holeExitLonV1136=location.getLongitude();
                }
                return;
            }
            if(now-holeExitAtV1136<12000L)return;
            float[] out=new float[1];
            Location.distanceBetween(holeExitLatV1136,holeExitLonV1136,location.getLatitude(),location.getLongitude(),out);
            if(out[0]<40f)return;
            holeExitArmedV1136=false;
            openHoleDetectPopupV1136(Math.min(18,hole+1));
        }'''
s=replace_method(s,'        private void maybeAutoHole(){',auto_body)

# Popup helpers are inserted just before the approved weather card renderer.
helper_anchor='        private void drawApprovedWeatherGpsV1136(Canvas c,float w,float h){'
idx=s.find(helper_anchor)
if idx<0:
    raise SystemExit('approved helper anchor missing')
helpers=r'''        private void openHoleDetectPopupV1136(int candidate){
            holeDetectCandidateV1136=Math.max(1,Math.min(18,candidate));
            holeDetectPopupV1136=true;
            showToast("다음 홀 후보 H"+holeDetectCandidateV1136+" · 확인해주세요");
            invalidate();
        }

        private void shiftHoleDetectCandidateV1136(int delta){
            holeDetectCandidateV1136=Math.max(1,Math.min(18,holeDetectCandidateV1136+delta));
            invalidate();
        }

        private void acceptHoleDetectV1136(){
            int old=hole;
            hole=Math.max(1,Math.min(18,holeDetectCandidateV1136));
            holeDirection=hole>=old?1:-1;lastHoleChange=SystemClock.uptimeMillis();lastAutoHoleAt=lastHoleChange;
            hasTarget=false;navSmoothXV1133=Float.NaN;navSmoothYV1133=Float.NaN;
            holeExitArmedV1136=false;holeExitArmedHoleV1136=hole;
            holeDetectPopupV1136=false;holeDetectSuppressUntilV1136=SystemClock.uptimeMillis()+30000L;
            saveState();showToast("H"+hole+" 확인 · 야디지 이동");invalidate();
        }

        private void dismissHoleDetectV1136(){
            holeDetectPopupV1136=false;
            holeDetectSuppressUntilV1136=SystemClock.uptimeMillis()+60000L;
            showToast("현재 H"+hole+" 유지");invalidate();
        }

        private Bitmap holeDetectBitmapV1136(int candidate){
            int old=hole;
            try{hole=candidate;return fullHoleBitmapV1102();}
            finally{hole=old;}
        }

        private String holeDetectStrategyV1136(int candidate){
            int old=hole;
            try{hole=candidate;return strategyNote();}
            finally{hole=old;}
        }

        private int holeDetectParV1136(int candidate){int old=hole;try{hole=candidate;return currentPar();}finally{hole=old;}}
        private int holeDetectTotalV1136(int candidate){int old=hole;try{hole=candidate;return (int)Math.round(currentYards()*.9144);}finally{hole=old;}}

        private void drawHoleDetectWrapV1136(Canvas c,String value,float x,float y,float right,float lineH,float z,int color,int maxLines){
            if(value==null)value="";String[] words=value.split(" ");String line="";int lines=0;
            p.setTextSize(z*getResources().getDisplayMetrics().scaledDensity);
            for(int i=0;i<words.length && lines<maxLines;i++){
                String test=line.length()==0?words[i]:line+" "+words[i];
                if(p.measureText(test)>right-x && line.length()>0){text(c,line,x,y+lines*lineH,z,color,true);lines++;line=words[i];}
                else line=test;
            }
            if(lines<maxLines && line.length()>0)text(c,line,x,y+lines*lineH,z,color,true);
        }

        private void drawHoleDetectPopupV1136(Canvas c){
            if(!holeDetectPopupV1136)return;
            float w=getWidth(),h=getHeight();
            p.setColor(Color.argb(112,16,42,31));c.drawRect(0,0,w,h,p);

            RectF card=new RectF(w*.055f,h*.205f,w*.945f,h*.790f);
            softShadow(c,card,32);box(c,card,Color.rgb(255,253,239),32);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(3f);p.setColor(Color.rgb(122,186,106));c.drawRoundRect(card,32,32,p);p.setStyle(Paint.Style.FILL);

            // Storybook sky header + mascot.
            RectF head=new RectF(card.left,card.top,card.right,card.top+h*.105f);box(c,head,Color.rgb(220,244,247),30);
            p.setColor(Color.rgb(255,255,255));c.drawCircle(head.left+w*.12f,head.top+h*.026f,18,p);c.drawCircle(head.left+w*.16f,head.top+h*.026f,13,p);
            text(c,"다음 홀을 찾았어요!",head.left+w*.055f,head.top+h*.046f,21f,DEEP,true);
            text(c,"코스 모양을 보고 맞는지 확인해주세요",head.left+w*.055f,head.top+h*.079f,10.5f,Color.rgb(76,105,82),true);
            mascot(c,head.right-w*.075f,head.centerY()+4,21,true);
            holeDetectCloseV1136.set(head.right-w*.060f,head.top+h*.008f,head.right-w*.018f,head.top+h*.043f);
            text(c,"×",holeDetectCloseV1136.centerX(),holeDetectCloseV1136.centerY()+6,18f,Color.rgb(96,121,101),true,Paint.Align.CENTER);

            float bodyTop=head.bottom+h*.018f,bodyBottom=card.bottom-h*.120f;
            RectF miniBox=new RectF(card.left+w*.035f,bodyTop,card.left+w*.405f,bodyBottom);
            box(c,miniBox,Color.rgb(238,248,219),22);
            p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.5f);p.setColor(Color.rgb(190,205,167));c.drawRoundRect(miniBox,22,22,p);p.setStyle(Paint.Style.FILL);

            Bitmap mb=holeDetectBitmapV1136(holeDetectCandidateV1136);
            RectF miniInner=new RectF(miniBox.left+w*.025f,miniBox.top+h*.018f,miniBox.right-w*.025f,miniBox.bottom-h*.020f);
            if(mb!=null){RectF dst=fitCenterV1102(mb,miniInner);Paint bp=new Paint(Paint.ANTI_ALIAS_FLAG|Paint.FILTER_BITMAP_FLAG);c.drawBitmap(mb,null,dst,bp);}
            else drawActualYardageV190(c,miniInner,holeDetectParV1136(holeDetectCandidateV1136),holeDetectTotalV1136(holeDetectCandidateV1136));

            // Only the number is overlaid on the actual mini yardage, as requested.
            text(c,""+holeDetectCandidateV1136,miniBox.left+w*.045f,miniBox.top+h*.070f,42f,Color.WHITE,true);
            text(c,""+holeDetectCandidateV1136,miniBox.left+w*.043f,miniBox.top+h*.068f,42f,DEEP,true);

            holeDetectPrevV1136.set(miniBox.left-w*.004f,miniBox.centerY()-h*.030f,miniBox.left+w*.075f,miniBox.centerY()+h*.030f);
            holeDetectNextV1136.set(miniBox.right-w*.075f,miniBox.centerY()-h*.030f,miniBox.right+w*.004f,miniBox.centerY()+h*.030f);
            drawApprovedArrowV1136(c,holeDetectPrevV1136,false);drawApprovedArrowV1136(c,holeDetectNextV1136,true);

            RectF info=new RectF(card.left+w*.445f,bodyTop,card.right-w*.030f,bodyBottom);
            box(c,info,Color.rgb(255,255,248),22);
            text(c,"PAR "+holeDetectParV1136(holeDetectCandidateV1136)+"   ·   "+holeDetectTotalV1136(holeDetectCandidateV1136)+"m",info.left+w*.025f,info.top+h*.040f,13.5f,Color.rgb(169,119,33),true);
            text(c,"공략 한 줄",info.left+w*.025f,info.top+h*.090f,14.5f,GREEN,true);
            drawHoleDetectWrapV1136(c,holeDetectStrategyV1136(holeDetectCandidateV1136),info.left+w*.025f,info.top+h*.126f,info.right-w*.020f,h*.031f,11.5f,INK,4);
            RectF tip=new RectF(info.left+w*.020f,info.bottom-h*.100f,info.right-w*.020f,info.bottom-h*.020f);
            box(c,tip,Color.rgb(236,248,224),16);
            text(c,"TIP",tip.left+w*.018f,tip.top+h*.030f,9.5f,GREEN,true);
            drawHoleDetectWrapV1136(c,"미니맵이 실제 홀과 다르면 좌우 버튼으로 바꾼 뒤 저장하세요.",tip.left+w*.018f,tip.top+h*.056f,tip.right-w*.012f,h*.025f,9.3f,Color.rgb(71,91,70),2);

            holeDetectLaterV1136.set(card.left+w*.040f,card.bottom-h*.088f,card.left+w*.355f,card.bottom-h*.028f);
            holeDetectAcceptV1136.set(card.left+w*.385f,card.bottom-h*.088f,card.right-w*.040f,card.bottom-h*.028f);
            drawApprovedActionV1136(c,holeDetectLaterV1136,"현재 홀 유지",Color.rgb(244,246,235),INK);
            drawApprovedActionV1136(c,holeDetectAcceptV1136,"이 홀로 이동",Color.rgb(64,151,89),Color.WHITE);
        }

'''
s=s[:idx]+helpers+s[idx:]

# Draw popup above the PASS UI and all field overlays.
draw_anchor='            drawToast(c); postInvalidateDelayed(screen==1?50:120);'
if draw_anchor not in s:
    raise SystemExit('onDraw popup anchor missing')
s=s.replace(draw_anchor,'            if(screen==1 && holeDetectPopupV1136)drawHoleDetectPopupV1136(c);\n'+draw_anchor,1)

# Popup owns touch while visible. Candidate arrows do not alter the current hole;
# only the explicit green confirmation button commits and opens that yardage.
touch_anchor='            if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();'
if touch_anchor not in s:
    raise SystemExit('touch popup anchor missing')
popup_touch=r'''            if(holeDetectPopupV1136){
                if(holeDetectPrevV1136.contains(x,y)){shiftHoleDetectCandidateV1136(-1);return true;}
                if(holeDetectNextV1136.contains(x,y)){shiftHoleDetectCandidateV1136(1);return true;}
                if(holeDetectAcceptV1136.contains(x,y)){acceptHoleDetectV1136();return true;}
                if(holeDetectLaterV1136.contains(x,y)||holeDetectCloseV1136.contains(x,y)){dismissHoleDetectV1136();return true;}
                return true;
            }
'''
s=s.replace(touch_anchor,touch_anchor+'\n'+popup_touch,1)

p.write_text(s)
print('applied V1.13.6 HOLE DETECT CONFIRM POPUP: detect -> review actual mini yardage -> adjust -> explicit commit')
