from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.13.6 APPROVED UI HOTFIX' not in s:
    raise SystemExit('one-shot field patch requires approved UI')
if 'private int approvedRemainingV1136(' not in s:
    raise SystemExit('one-shot field patch requires TEE-first DIST compatibility')

MARK='V1.13.6 ONE-SHOT FIELD MODE'
if MARK in s:
    print('one-shot field mode already applied')
else:
    # State for conservative same-round sequential hole advance. This deliberately
    # does not depend on future-hole learned TEE coordinates because each course is
    # played only once on this trip.
    anchor='        private long lastRoundLogElapsedV1136=0L;'
    if anchor not in s:
        raise SystemExit('round-log field anchor missing')
    s=s.replace(anchor,anchor+r'''
        // V1.13.6 ONE-SHOT FIELD MODE
        private boolean oneShotExitArmedV1136=false;
        private int oneShotExitHoleV1136=-1;
        private double oneShotExitLatV1136=999,oneShotExitLonV1136=999;
        private long oneShotExitAtV1136=0L;
''',1)

    def replace_method(src, signature, body):
        start=src.find(signature)
        if start<0: raise SystemExit('missing method '+signature)
        brace=src.find('{',start); depth=0; end=None
        for i in range(brace,len(src)):
            if src[i]=='{': depth+=1
            elif src[i]=='}':
                depth-=1
                if depth==0:
                    end=i+1; break
        if end is None: raise SystemExit('unbalanced method '+signature)
        return src[:start]+body+src[end:]

    # First-visit / one-round auto-hole assist. This base implementation is then
    # upgraded by patch-v1136-hole-confirm-popup.py so detection proposes H+1 but
    # never changes the active hole until the golfer confirms it.
    body=r'''        private void maybeAutoHole(){
            if(!autoHole || selected<0 || hole>=18 || location==null || !navGpsUsableV1133())return;
            GeoRef tee=getRef("t",hole);if(tee==null){oneShotExitArmedV1136=false;oneShotExitHoleV1136=-1;return;}
            int total=verifiedMetersV190();if(total<=0)total=(int)Math.round(currentYards()*.9144);if(total<=0)return;
            int remain=approvedRemainingV1136(total,greenCenterRef(hole));if(remain<0)return;
            long now=SystemClock.uptimeMillis();
            if(oneShotExitHoleV1136!=hole){oneShotExitArmedV1136=false;oneShotExitHoleV1136=hole;}
            float finishBand=Math.max(25f,Math.min(45f,total*.08f));
            if(!oneShotExitArmedV1136){
                if(remain<=finishBand){
                    oneShotExitArmedV1136=true;oneShotExitAtV1136=now;
                    oneShotExitLatV1136=location.getLatitude();oneShotExitLonV1136=location.getLongitude();
                }
                return;
            }
            if(now-oneShotExitAtV1136<12000L)return;
            float[] out=new float[1];Location.distanceBetween(oneShotExitLatV1136,oneShotExitLonV1136,location.getLatitude(),location.getLongitude(),out);
            if(out[0]<40f)return;
            int old=hole;hole=Math.min(18,hole+1);holeDirection=1;lastHoleChange=now;lastAutoHoleAt=now;hasTarget=false;
            navSmoothXV1133=Float.NaN;navSmoothYV1133=Float.NaN;
            oneShotExitArmedV1136=false;oneShotExitHoleV1136=hole;saveState();
            showToast("H"+old+" 종료 감지 · H"+hole+" 준비 · TEE 저장");
        }'''
    s=replace_method(s,'        private void maybeAutoHole(){',body)
    p.write_text(s)
    print('applied V1.13.6 ONE-SHOT FIELD MODE: per-hole TEE-first use, optional GREEN, sequential auto-hole assist')

# Popup confirmation and the single final Cute/TTS layer are intentionally owned
# by patch-v1136-approved-compat.py. Do not execute either here; otherwise an
# idempotent SystemExit from the popup patch can terminate the parent compat
# script before the final visual/TTS layer is applied.
print('one-shot field mode complete; popup finalization deferred to approved compat')
