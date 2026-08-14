from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import random

ROOT=Path('app/src/main/res/drawable-nodpi')
TMP=Path('.github/tmp/v1130')
TMP.mkdir(parents=True,exist_ok=True)
FILES=sorted(ROOT.glob('yardage_*.jpg'))
if len(FILES)!=135:
    raise SystemExit(f'V1.14.2 expects 135 full-hole JPGs including Naepo 9, got {len(FILES)}')

CREAM=(250,226,158)
FOREST=(31,103,56)
COURSE=(55,136,63)
ROUGH=(80,164,70)
FAIR=(127,205,75)
FAIR_ALT=(132,213,76)
FAIR_EDGE=(72,157,54)
ROUGH_EDGE=(48,121,52)
COURSE_EDGE=(27,87,45)
WATER=(65,169,219)
WATER_EDGE=(43,126,176)
BUNKER_EDGE=(203,166,96)
TRUNK=(102,70,39)
TREE_A=(48,128,57)
TREE_B=(58,147,62)
TREE_C=(75,160,64)
FLOWER=(247,184,66)
INK=(49,72,44)

WORK_W=600
WORK_H=900
OUT_W=1200
OUT_H=1800


def runs(xs):
    if len(xs)==0:return []
    out=[];start=int(xs[0]);prev=int(xs[0])
    for v in xs[1:]:
        v=int(v)
        if v-prev>7:
            out.append((start,prev));start=v
        prev=v
    out.append((start,prev));return out


def interpolate_nan(a):
    a=np.asarray(a,dtype=np.float32);good=np.isfinite(a)
    if not good.any():return np.full_like(a,a.shape[0]*0.5)
    x=np.arange(a.size);a[~good]=np.interp(x[~good],x[good],a[good]);return a


def smooth1d(a,win=31):
    if win<3:return a
    k=np.ones(win,dtype=np.float32)/win
    pad=win//2;ap=np.pad(a,(pad,pad),mode='edge')
    return np.convolve(ap,k,mode='valid')[:a.size]


def choose_fairway_corridor(arr):
    r=arr[:,:,0].astype(np.int16);g=arr[:,:,1].astype(np.int16);b=arr[:,:,2].astype(np.int16)
    hi=np.max(arr,axis=2).astype(np.int16);lo=np.min(arr,axis=2).astype(np.int16);sat=hi-lo
    cand=(g>132)&((g-r)>25)&((g-b)>38)&(sat>55)
    # Ignore the outer 2% to avoid source-page borders.
    cand[:,:12]=False;cand[:,-12:]=False
    left=np.full(WORK_H,np.nan,dtype=np.float32);right=left.copy();prev=WORK_W*.5
    for y in range(WORK_H):
        rs=runs(np.flatnonzero(cand[y]))
        valid=[q for q in rs if q[1]-q[0]>=14]
        if not valid:continue
        def score(q):
            c=(q[0]+q[1])*.5;ln=q[1]-q[0]+1
            center_pen=abs(c-prev)*.34
            edge_pen=70 if q[0]<8 or q[1]>WORK_W-9 else 0
            return ln*1.7-center_pen-edge_pen
        q=max(valid,key=score);left[y]=q[0];right[y]=q[1];prev=(q[0]+q[1])*.5
    left=interpolate_nan(left);right=interpolate_nan(right)
    left=smooth1d(left,39);right=smooth1d(right,39)
    # Give every hole a friendly broad illustrated fairway while preserving its centerline/dogleg.
    center=(left+right)*.5;width=np.maximum(86,(right-left)*.86)
    width=smooth1d(width,35)
    left=np.clip(center-width*.5,28,WORK_W-110);right=np.clip(center+width*.5,110,WORK_W-28)
    return left,right,center


def polygon_from_lr(left,right,pad=0):
    pts=[]
    for y in range(0,WORK_H,6):pts.append((float(max(0,left[y]-pad)),float(y)))
    for y in range(WORK_H-1,-1,-6):pts.append((float(min(WORK_W-1,right[y]+pad)),float(y)))
    return pts


def contour(draw,pts,fill,outline,width):
    draw.polygon(pts,fill=fill)
    draw.line(pts+[pts[0]],fill=outline,width=width,joint='curve')


def component_blobs(mask,min_area=12,max_area=12000):
    # Fast row-run grouping is enough for bunker/water illustration; merge nearby runs vertically.
    h,w=mask.shape;boxes=[];active=[]
    for y in range(h):
        row=np.flatnonzero(mask[y]);rr=runs(row);next_active=[]
        for l,r in rr:
            if r-l<2:continue
            match=None
            for idx,b in enumerate(active):
                if l<=b[2]+5 and r>=b[0]-5:
                    match=idx;break
            if match is None:next_active.append([l,y,r,y,(r-l+1)])
            else:
                b=active.pop(match);b[0]=min(b[0],l);b[2]=max(b[2],r);b[3]=y;b[4]+=r-l+1;next_active.append(b)
        for b in active:
            if min_area<=b[4]<=max_area:boxes.append(tuple(b))
        active=next_active
    for b in active:
        if min_area<=b[4]<=max_area:boxes.append(tuple(b))
    return boxes


def rounded_blob(draw,box,fill,outline,width=3):
    l,t,r,b,_=box
    if r-l<5 or b-t<4:return
    pad=2
    draw.rounded_rectangle((l-pad,t-pad,r+pad,b+pad),radius=max(3,min((r-l)//3,(b-t)//3,14)),fill=fill,outline=outline,width=width)


def tree(draw,x,y,rad,rnd):
    draw.rounded_rectangle((x-3,y+rad*.38,x+3,y+rad+9),radius=2,fill=TRUNK+(235,))
    cols=[TREE_A,TREE_B,TREE_C]
    blobs=[(-rad*.48,1,rad*.67),(rad*.36,-2,rad*.70),(0,-rad*.38,rad*.78)]
    for i,(dx,dy,rr) in enumerate(blobs):
        c=cols[(i+rnd.randint(0,2))%3];draw.ellipse((x+dx-rr,y+dy-rr,x+dx+rr,y+dy+rr),fill=c+(255,))
    draw.ellipse((x-rad*.18,y-rad*.70,x+rad*.22,y-rad*.30),fill=(117,188,73,180))


def reillustrate(im,name):
    # Fixed canvas keeps normalized x/y mapping stable but makes every hole fill the phone like the reference.
    src=im.convert('RGB').resize((WORK_W,WORK_H),Image.Resampling.LANCZOS)
    arr=np.asarray(src)
    left,right,center=choose_fairway_corridor(arr)
    out=Image.new('RGB',(WORK_W,WORK_H),FOREST);d=ImageDraw.Draw(out,'RGBA')

    course_pts=polygon_from_lr(left,right,72);rough_pts=polygon_from_lr(left,right,38);fair_pts=polygon_from_lr(left,right,0)
    contour(d,course_pts,COURSE+(255,),COURSE_EDGE+(255,),5)
    contour(d,rough_pts,ROUGH+(255,),ROUGH_EDGE+(255,),4)
    contour(d,fair_pts,FAIR+(255,),FAIR_EDGE+(255,),4)

    # Broad alternating mowing bands, clipped approximately to the fairway row span.
    for y0 in range(18,WORK_H,58):
        y1=min(WORK_H-1,y0+29)
        poly=[]
        for y in range(y0,y1+1,5):poly.append((left[y]+4,y))
        for y in range(y1,y0-1,-5):poly.append((right[y]-4,y))
        if len(poly)>3:d.polygon(poly,fill=FAIR_ALT+(92,))

    r=arr[:,:,0].astype(np.int16);g=arr[:,:,1].astype(np.int16);b=arr[:,:,2].astype(np.int16)
    hi=np.max(arr,axis=2).astype(np.int16);lo=np.min(arr,axis=2).astype(np.int16);sat=hi-lo
    yy,xx=np.indices((WORK_H,WORK_W));inside=(xx>=left[:,None]-72)&(xx<=right[:,None]+72)
    bunker=(hi>184)&(sat<92)&inside
    water=(b>105)&((b-g)>4)&((b-r)>18)&(sat>55)&inside
    for box in component_blobs(bunker,18,5200):rounded_blob(d,box,CREAM+(255,),BUNKER_EDGE+(255,),3)
    for box in component_blobs(water,20,16000):rounded_blob(d,box,WATER+(255,),WATER_EDGE+(255,),3)

    rnd=random.Random(sum(ord(c) for c in name)*7919)
    # Tree rows closely hug the fairway like the approved animation reference.
    for y in range(42,WORK_H-42,47):
        for side in (-1,1):
            x=(left[y]-rnd.randint(27,54)) if side<0 else (right[y]+rnd.randint(27,54))
            x=max(14,min(WORK_W-14,x));tree(d,x,y,rnd.randint(11,18),rnd)
    # Small flowers and bushes break up empty margins.
    for i in range(28):
        y=rnd.randint(55,WORK_H-65);side=-1 if i%2==0 else 1
        x=(left[y]-rnd.randint(42,68)) if side<0 else (right[y]+rnd.randint(42,68));x=max(8,min(WORK_W-8,x))
        rr=rnd.randint(2,4);col=FLOWER if i%3 else (235,107,104)
        d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col+(240,))

    # Green target zone, pin and tee marker.
    gy=54;gx=center[gy];gw=max(62,(right[gy]-left[gy])*.58)
    d.ellipse((gx-gw*.48,gy-31,gx+gw*.48,gy+32),fill=(145,216,82,185),outline=(74,158,55,230),width=3)
    d.line((gx,gy+22,gx,gy-24),fill=(103,65,38,255),width=5)
    d.polygon([(gx,gy-24),(gx+25,gy-15),(gx,gy-5)],fill=(240,77,49,255))
    ty=WORK_H-48;tx=center[ty]
    d.ellipse((tx-15,ty-15,tx+15,ty+15),fill=(255,255,250,255),outline=(61,92,54,255),width=4)

    # Friendly dotted strategy route. The live orange GPS marker remains the authoritative player position.
    route=[]
    for y in range(WORK_H-85,95,-28):route.append((center[y],y))
    for i,(x,y) in enumerate(route):
        if i%2==0:d.ellipse((x-3,y-3,x+3,y+3),fill=(255,255,244,225))

    # Slight paper-softening keeps it illustrative rather than vector-flat.
    out=out.filter(ImageFilter.GaussianBlur(.35)).resize((OUT_W,OUT_H),Image.Resampling.LANCZOS)
    return out

manifest=[];samples=[]
SAMPLE={'yardage_kamishihoro_c01.jpg','yardage_furano_palmer15.jpg','yardage_sahoro_07.jpg','yardage_royallinks_queens07.jpg','yardage_naepo_01.jpg'}
for p in FILES:
    with Image.open(p) as src:
        before=src.size;out=reillustrate(src,p.name)
    out.save(p,'JPEG',quality=95,subsampling=0,optimize=True,progressive=True)
    manifest.append(f'{p.name}\t{before[0]}x{before[1]} -> {OUT_W}x{OUT_H}')
    if p.name in SAMPLE:samples.append((p.name,out.copy()))

(TMP/'manifest.txt').write_text('\n'.join(manifest)+'\n')
if samples:
    samples.sort();tile_w=300;tile_h=500;W=len(samples)*315+30;H=590
    sheet=Image.new('RGB',(W,H),(249,249,231));d=ImageDraw.Draw(sheet)
    try:f=ImageFont.truetype('/tmp/Jua-Regular.ttf',26);sf=ImageFont.truetype('/tmp/Jua-Regular.ttf',17)
    except Exception:f=sf=None
    d.text((26,18),'V1.14.2 · REAL HOLE → STORYBOOK REDRAW',fill=INK,font=f)
    for idx,(nm,im) in enumerate(samples):
        x=20+idx*315;y=58;thumb=im.copy();thumb.thumbnail((tile_w,tile_h),Image.Resampling.LANCZOS);bx=x+(tile_w-thumb.width)//2;by=y+(tile_h-thumb.height)//2
        sheet.paste(thumb,(bx,by));d.rounded_rectangle((x,y,x+tile_w,y+tile_h),radius=24,outline=(76,157,91),width=4);d.text((x+6,y+510),nm.replace('yardage_','').replace('.jpg',''),fill=INK,font=sf)
    sheet.save(TMP/'yardage-concept-samples.jpg','JPEG',quality=94,subsampling=0)

print('V1.14.2: 135 real holes re-illustrated into fixed 1200x1800 storybook maps')
print('Preserved: normalized hole centerline/dogleg, bunker/water extraction, TEE→GREEN direction')
print('sample sheet:',TMP/'yardage-concept-samples.jpg')
