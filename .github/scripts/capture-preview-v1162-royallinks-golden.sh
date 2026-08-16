#!/usr/bin/env bash
set -euo pipefail
APK="HokkaidoGolfGPS-v1.16.3-concept-reference-lock-debug.apk"
PKG="com.hokkaidogolf.trip"
ACTIVITY="com.hokkaidogolf.trip/.FieldGpsV09Activity"
OUT="preview-v1163-concept"
mkdir -p "$OUT"; rm -f "$OUT"/*.png "$OUT"/*.log
adb shell wm size 941x1672
adb shell wm density 420
sleep 4

clean_system_dialogs(){
  local tries=0
  while [ "$tries" -lt 8 ]; do
    tries=$((tries+1))
    adb shell uiautomator dump /sdcard/concept-ui.xml >/dev/null 2>&1 || true
    if adb shell cat /sdcard/concept-ui.xml 2>/dev/null | grep -Eq "Pixel Launcher isn't responding|isn't responding|Close app|Wait"; then
      # Prefer Wait so the emulator recovers cleanly, then stop the launcher process.
      adb shell input tap 365 965 || true
      adb shell am force-stop com.google.android.apps.nexuslauncher || true
      sleep 1.2
      continue
    fi
    return 0
  done
  return 1
}

# The launcher is irrelevant to direct activity capture. Stopping it prevents a
# late ANR dialog from racing with screencap on GitHub-hosted cold boots.
adb shell am force-stop com.google.android.apps.nexuslauncher || true
clean_system_dialogs || true
adb install -r "$APK"
adb shell pm grant "$PKG" android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant "$PKG" android.permission.ACCESS_COARSE_LOCATION || true
adb shell settings put secure immersive_mode_confirmations confirmed || true
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true

start_preview(){
  local variant="$1" hole="$2"
  adb shell am start -W -n "$ACTIVITY" --ez preview true --ei previewCourse 4 --ei previewVariant "$variant" --ei previewHole "$hole" --ei previewScreen 1 >/dev/null
}

image_is_clean(){
  local file="$1"
  python3 - "$file" <<'PY'
from PIL import Image
import numpy as np, sys
f=sys.argv[1]
a=np.asarray(Image.open(f).convert('RGB'))
assert a.shape[:2]==(1672,941),a.shape
# Android ANR/permission dialogs create a huge bright neutral card across the
# middle of the image. The approved Storybook UI never contains such a block.
roi=a[600:1100,60:880]
neutral=(roi.min(axis=2)>225)&((roi.max(axis=2)-roi.min(axis=2))<25)
fraction=float(neutral.mean())
if fraction>=0.30:
    print('CONTAMINATED_SCREENSHOT neutral_modal_fraction',fraction,file,file=sys.stderr)
    raise SystemExit(2)
print('CLEAN_SCREENSHOT neutral_modal_fraction',round(fraction,4),file)
PY
}

shot(){
  local variant="$1" hole="$2" file="$3"
  local attempt=0
  while [ "$attempt" -lt 5 ]; do
    attempt=$((attempt+1))
    rm -f "$OUT/$file"
    clean_system_dialogs || true
    adb shell am force-stop com.google.android.apps.nexuslauncher || true
    adb shell am force-stop "$PKG" || true
    start_preview "$variant" "$hole"
    sleep 1.5
    clean_system_dialogs || true
    start_preview "$variant" "$hole"
    sleep 1.4
    clean_system_dialogs || true
    if ! adb shell pidof "$PKG" >/dev/null 2>&1; then
      adb logcat -d -v threadtime | grep -E -A50 -B10 "AndroidRuntime|FATAL EXCEPTION|Process: ${PKG}|Caused by:" | tail -260 >&2 || true
      continue
    fi
    adb exec-out screencap -p > "$OUT/$file"
    test -s "$OUT/$file" || continue
    # Check both AFTER screencap: this closes the race where an ANR can appear
    # between the previous UI dump and the actual screenshot.
    adb shell uiautomator dump /sdcard/concept-ui-after.xml >/dev/null 2>&1 || true
    if adb shell cat /sdcard/concept-ui-after.xml 2>/dev/null | grep -Eq "isn't responding|Close app|Wait"; then
      echo "REJECT screenshot attempt=$attempt file=$file: system dialog appeared during capture" >&2
      rm -f "$OUT/$file"
      clean_system_dialogs || true
      continue
    fi
    if ! image_is_clean "$OUT/$file"; then
      echo "REJECT screenshot attempt=$attempt file=$file: pixel-level modal detector" >&2
      rm -f "$OUT/$file"
      clean_system_dialogs || true
      continue
    fi
    echo "ACCEPT screenshot attempt=$attempt file=$file"
    return 0
  done
  echo "FAILED to obtain uncontaminated screenshot: $file" >&2
  return 79
}

shot 0 1  "00-royallinks-queens-h1-concept.png"
shot 1 1  "01-royallinks-kings-h1-concept.png"
shot 0 18 "02-royallinks-queens-h18-concept.png"
shot 1 7  "03-royallinks-kings-h7-short-par3.png"

python3 - <<'PY'
from PIL import Image
from pathlib import Path
import numpy as np

out=Path('preview-v1163-concept')
fs=sorted(out.glob('*.png'))
assert len(fs)==4,fs
ref=np.asarray(Image.open('app/src/main/res/drawable-nodpi/master_golden_chrome_v1162.webp').convert('RGB'),dtype=np.int16)
assert ref.shape[:2]==(1672,941),ref.shape
ims=[]
for f in fs:
    im=Image.open(f).convert('RGB'); assert im.size==(941,1672),(f,im.size); ims.append(im)
    a=np.asarray(im,dtype=np.int16)
    mask=np.zeros((1672,941),bool)
    mask[8:148,18:82]=True
    mask[8:148,700:928]=True
    mask[156:205,18:923]=True
    mask[335:350,18:923]=True
    mask[477:1328,18:36]=True
    mask[477:1328,214:238]=True
    mask[397:450,714:918]=True
    mask[530:575,714:918]=True
    mask[1240:1408,620:925]=True
    mask[1458:1652,18:923]=True
    mask[370:1418,240:255]=True
    diff=np.abs(a-ref).mean(axis=2)
    mae=float(diff[mask].mean()); p95=float(np.percentile(diff[mask],95))
    assert mae<10.0,(f,'concept chrome MAE too high',mae,p95)
    assert p95<28.0,(f,'concept chrome p95 too high',mae,p95)

    slot=a[355:1435,250:690]
    nearwhite=np.all(slot>245,axis=2); white_fraction=float(nearwhite.mean())
    assert white_fraction<0.12,(f,'white rectangular course page remains',white_fraction)

    wood=a[180:300,330:600].mean(axis=(0,1))
    assert 45<wood[0]<120 and 25<wood[1]<85 and wood[2]<60,(f,'walnut board too pale',wood.tolist())
    panel=a[650:700,35:200].mean(axis=(0,1))
    assert panel[1]<90 and panel[1]>panel[0]*1.35 and panel[2]<45,(f,'score panel not deep green',panel.tolist())
    target=a[1275:1370,660:880].mean(axis=(0,1))
    assert target[0]>target[1]>target[2] and target[1]<190 and target[2]<145,(f,'target not amber-gold',target.tolist())
    nav=a[1470:1640,30:910].mean(axis=(0,1))
    assert nav[1]>nav[0]*1.25 and nav[1]<105,(f,'dark green nav missing',nav.tolist())

    rr,gg,bb=slot[:,:,0],slot[:,:,1],slot[:,:,2]
    green=(gg>rr*1.10)&(gg>bb*1.28)&(gg>55)
    green_fraction=float(green.mean())
    assert green_fraction>0.13,(f,'course still too washed / insufficient green density',green_fraction)
    if green.any():
        gm=slot[green].mean(axis=0)
        assert gm[0]<145 and gm[1]<190 and gm[2]<110,(f,'course green palette still washed',gm.tolist())
    print(f.name,'MAE',round(mae,2),'WHITE',round(white_fraction,4),'GREEN',round(green_fraction,4),'WOOD',wood.astype(int).tolist())

a0=np.asarray(ims[0],dtype=np.int16)[355:1435,250:690]
a1=np.asarray(ims[1],dtype=np.int16)[355:1435,250:690]
course_diff=float(np.abs(a0-a1).mean())
assert course_diff>6.0,('Queens/Kings course mapping did not change',course_diff)

short=np.asarray(ims[3],dtype=np.uint8)
roi=short[560:1180,640:790]
r,g,b=roi[:,:,0],roi[:,:,1],roi[:,:,2]
blue=((b>150)&(b>g*1.25)&(b>r*1.6))
assert float(blue.mean())<0.004,('short-hole invalid 200m marker still visible',float(blue.mean()))
print('V1.16.3 UPLOADED CONCEPT VISUAL QA PASS','course_diff',round(course_diff,2))
PY

adb shell wm size reset || true
adb shell wm density reset || true
ls -lh "$OUT"/*.png
