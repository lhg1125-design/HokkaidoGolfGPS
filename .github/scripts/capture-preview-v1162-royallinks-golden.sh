#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.16.2-golden-master-restore-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1162-royallinks-golden"
mkdir -p "$OUT"; rm -f "$OUT"/*.png "$OUT"/*.log
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put secure immersive_mode_confirmations confirmed || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
adb shell wm size 941x1672
adb shell wm density 420

shot(){
  local variant="$1" hole="$2" file="$3"
  adb shell am force-stop "$PKG" || true
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse 4 --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen 1
  sleep 2.0
  if ! adb shell pidof "$PKG" >/dev/null 2>&1; then
    echo "APP PROCESS EXITED variant=$variant hole=$hole" >&2
    adb logcat -d -v threadtime | grep -E -A50 -B10 "AndroidRuntime|FATAL EXCEPTION|Process: ${PKG}|Caused by:" | tail -260 >&2 || true
    return 77
  fi
  adb exec-out screencap -p > "$OUT/$file"
  test -s "$OUT/$file"
}

shot 0 1  "00-royallinks-queens-h1-golden.png"
shot 1 1  "01-royallinks-kings-h1-golden.png"
shot 0 18 "02-royallinks-queens-h18-golden.png"

python3 - <<'PY'
from PIL import Image, ImageChops
from pathlib import Path
import numpy as np

out=Path('preview-v1162-royallinks-golden')
fs=sorted(out.glob('*.png'))
assert len(fs)==3,fs
ref=np.asarray(Image.open('app/src/main/res/drawable-nodpi/master_golden_chrome_v1162.webp').convert('RGB'),dtype=np.int16)
assert ref.shape[:2]==(1672,941),ref.shape
ims=[]
for f in fs:
    im=Image.open(f).convert('RGB'); assert im.size==(941,1672),(f,im.size); ims.append(im)
    a=np.asarray(im,dtype=np.int16)
    mask=np.zeros((1672,941),bool)
    # Approved fixed chrome only. Dynamic title/metrics/players/course/ruler are excluded.
    mask[8:148,18:82]=True                 # back + lower-left course icon edge
    mask[8:148,700:928]=True               # approved weather chrome
    mask[156:205,18:923]=True              # wood top/grain/leaves
    mask[335:350,18:923]=True              # wood lower edge
    mask[477:1328,18:36]=True              # score panel left edge
    mask[477:1328,214:238]=True             # score panel right/shadow edge
    mask[397:450,714:918]=True              # bubble top chrome
    mask[530:575,714:918]=True              # bubble bottom chrome
    mask[1240:1408,620:925]=True            # approved beige target control
    mask[1458:1652,18:923]=True             # approved bottom navigation
    mask[370:1418,240:255]=True             # warm paper strip beside course
    diff=np.abs(a-ref).mean(axis=2)
    mae=float(diff[mask].mean())
    p95=float(np.percentile(diff[mask],95))
    assert mae<10.0,(f,'golden chrome MAE too high',mae,p95)
    assert p95<28.0,(f,'golden chrome p95 too high',mae,p95)
    slot=a[365:1422,260:680]
    nearwhite=np.all(slot>245,axis=2)
    white_fraction=float(nearwhite.mean())
    assert white_fraction<0.16,(f,'white rectangular course page remains',white_fraction)
    # Golden target is warm beige, not V1.16.1 saturated orange.
    target=a[1275:1370,660:880].mean(axis=(0,1))
    assert target[0]>target[1]>target[2] and target[1]>150,(f,'golden target tone missing',target.tolist())
    # Golden nav is very dark green, not the brighter teal V1.16.1 substitute.
    nav=a[1470:1640,30:910].mean(axis=(0,1))
    assert nav[1]>nav[0]*1.25 and nav[1]<105,(f,'golden dark nav missing',nav.tolist())
    print(f.name,'GOLDEN_MAE',round(mae,2),'P95',round(p95,2),'WHITE_PAGE',round(white_fraction,4))

# Raw maps must actually differ while the chrome stays locked.
a0=np.asarray(ims[0],dtype=np.int16)[365:1422,260:680]
a1=np.asarray(ims[1],dtype=np.int16)[365:1422,260:680]
course_diff=float(np.abs(a0-a1).mean())
assert course_diff>6.0,('Queens/Kings course mapping did not change',course_diff)
print('V1.16.2 USER GOLDEN MASTER VISUAL QA PASS','course_diff',round(course_diff,2))
PY

adb shell wm size reset || true
adb shell wm density reset || true
ls -lh "$OUT"/*.png
