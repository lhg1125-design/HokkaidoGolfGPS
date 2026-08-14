from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import random, math, hashlib

ROOT=Path('app/src/main/res/drawable-nodpi')
TMP=Path('.github/tmp/v1130')
TMP.mkdir(parents=True,exist_ok=True)
FILES=sorted(ROOT.glob('yardage_*.jpg'))
if len(FILES)!=135:
    raise SystemExit(f'V1.14.6 expects 135 full-hole JPGs including Naepo 9, got {len(FILES)}')

# Approved illustration palette: warm, cheerful, high-contrast, storybook-like.
FOREST_TOP=(44,116,55); FOREST_BOTTOM=(26,83,48)
COURSE=(66,143,65); COURSE_EDGE=(26,85,43)
ROUGH=(92,174,72); ROUGH_EDGE=(44,116,48)
FAIR=(143,211,79); FAIR_ALT=(156,221,86); FAIR_EDGE=(72,151,51)
GREEN=(164,224,92); GREEN_EDGE=(67,148,50)
WATER=(59,165,218); WATER_LIGHT=(104,207,238); WATER_EDGE=(35,116,168)
SAND=(250,224,157); SAND_LIGHT=(255,239,190); SAND_EDGE=(194,151,82)
TRUNK=(105,67,37); TRUNK_LIGHT=(144,95,51)
TREE_DARK=(34,103,49); TREE_A=(48,132,56); TREE_B=(65,153,61); TREE_C=(91,174,66); TREE_HI=(137,202,83)
FLOWER_Y=(252,193,54); FLOWER_P=(243,112,126); FLOWER_W=(255,248,216); FLOWER_B=(95,173,225)
ROCK=(147,137,105); ROCK_HI=(197,187,144)
INK=(48,70,42)

WORK_W=600; WORK_H=900; OUT_W=1200; OUT_H=1800


def runs(xs):
    if len(xs)==0:return []
    out=[];start=int(xs[0]);prev=int(xs[0])
    for v in xs[1:]:
        v=int(v)
        if v-prev>7: out.append((start,prev));start=v
        prev=v
    out.append((start,prev));return out


def interpolate_nan(a):
    a=np.asarray(a,dtype=np.float32);good=np.isfinite(a)
    if not good.any():return np.full_like(a,a.shape[0]*.5)
    x=np.arange(a.size);a[~good]=np.interp(x[~good],x[good],a[good]);return a


def smooth1d(a,win=31):
    k=np.ones(win,dtype=np.float32)/win;pad=win//2
    return np.convolve(np.pad(a,(pad,pad),mode='edge'),k,mode='valid')[:a.size]


def choose_fairway_corridor(arr):
    r=arr[:,:,0].astype(np.int16);g=arr[:,:,1].astype(np.int16);b=arr[:,:,2].astype(np.int16)
    hi=np.max(arr,axis=2).astype(np.int16);lo=np.min(arr,axis=2).astype(np.int16);sat=hi-lo
    cand=(g>126)&((g-r)>20)&((g-b)>30)&(sat>45)
    cand[:,:10]=False;cand[:,-10:]=False
    left=np.full(WORK_H,np.nan,dtype=np.float32);right=left.copy();prev=WORK_W*.5
    for y in range(WORK_H):
        valid=[q for q in runs(np.flatnonzero(cand[y])) if q[1]-q[0]>=12]
        if not valid:continue
        def score(q):
            c=(q[0]+q[1])*.5;ln=q[1]-q[0]+1
            return ln*1.8-abs(c-prev)*.30-(70 if q[0]<7 or q[1]>WORK_W-8 else 0)
        q=max(valid,key=score);left[y]=q[0];right[y]=q[1];prev=(q[0]+q[1])*.5
    left=smooth1d(interpolate_nan(left),41);right=smooth1d(interpolate_nan(right),41)
    center=smooth1d((left+right)*.5,35)
    # Preserve dogleg trajectory but center the overall composition and make the playable area visually generous.
    median=float(np.median(center));center=WORK_W*.5+(center-median)*1.16
    raw=np.maximum(118,(right-left)*1.08);width=smooth1d(raw,37)
    width=np.clip(width,118,245)
    left=np.clip(center-width*.5,54,WORK_W-175);right=np.clip(center+width*.5,175,WORK_W-54)
    center=(left+right)*.5
    return left,right,center


def polygon_from_lr(left,right,pad=0,step=5):
    pts=[(float(max(0,left[y]-pad)),float(y)) for y in range(0,WORK_H,step)]
    pts += [(float(min(WORK_W-1,right[y]+pad)),float(y)) for y in range(WORK_H-1,-1,-step)]
    return pts


def contour(draw,pts,fill,outline,width,shadow=False):
    if shadow:
        sh=[(x+4,y+6) for x,y in pts];draw.polygon(sh,fill=(15,58,37,90))
    draw.polygon(pts,fill=fill);draw.line(pts+[pts[0]],fill=outline,width=width,joint='curve')


def component_blobs(mask,min_area=12,max_area=16000):
    h,w=mask.shape;boxes=[];active=[]
    for y in range(h):
        rr=runs(np.flatnonzero(mask[y]));next_active=[]
        for l,r in rr:
            if r-l<2:continue
            match=None
            for idx,b in enumerate(active):
                if l<=b[2]+5 and r>=b[0]-5:match=idx;break
            if match is None:next_active.append([l,y,r,y,r-l+1])
            else:
                q=active.pop(match);q[0]=min(q[0],l);q[2]=max(q[2],r);q[3]=y;q[4]+=r-l+1;next_active.append(q)
        for q in active:
            if min_area<=q[4]<=max_area:boxes.append(tuple(q))
        active=next_active
    for q in active:
        if min_area<=q[4]<=max_area:boxes.append(tuple(q))
    return boxes


def organic_polygon(box,rnd,water=False):
    l,t,r,b,_=box;cx=(l+r)/2;cy=(t+b)/2;rx=max(6,(r-l)/2+4);ry=max(5,(b-t)/2+4)
    if not water and (r-l>82 or b-t>68 or ((r-l)>48 and (b-t)>48)):return None
    pts=[];n=24
    for i in range(n):
        a=2*math.pi*i/n
        wob=.86+.14*math.sin(a*3+rnd.random()*1.6)+rnd.uniform(-.08,.08)
        pts.append((cx+math.cos(a)*rx*wob,cy+math.sin(a)*ry*wob))
    return pts


def bunker(draw,box,rnd):
    pts=organic_polygon(box,rnd,False)
    if not pts:return
    sh=[(x+3,y+4) for x,y in pts];draw.polygon(sh,fill=(91,95,48,65));draw.polygon(pts,fill=SAND+(255,));draw.line(pts+[pts[0]],fill=SAND_EDGE+(255,),width=3,joint='curve')
    cx=sum(x for x,_ in pts)/len(pts);cy=sum(y for _,y in pts)/len(pts)
    draw.ellipse((cx-8,cy-6,cx+5,cy+3),fill=SAND_LIGHT+(140,))


def water(draw,box,rnd):
    pts=organic_polygon(box,rnd,True)
    if not pts:return
    draw.polygon([(x+3,y+4) for x,y in pts],fill=(23,79,117,70));draw.polygon(pts,fill=WATER+(255,));draw.line(pts+[pts[0]],fill=WATER_EDGE+(255,),width=4,joint='curve')
    l,t,r,b,_=box
    for yy in np.linspace(t+7,b-6,4):
        x1=l+5+rnd.uniform(0,8);x2=r-5-rnd.uniform(0,8)
        if x2>x1+8:draw.arc((x1,yy-3,x2,yy+4),200,340,fill=WATER_LIGHT+(210,),width=2)


def tree(draw,x,y,rad,rnd,variant=0):
    # shadow + trunk
    draw.ellipse((x-rad*.85,y+rad*.55,x+rad*.9,y+rad*1.15),fill=(15,55,32,65))
    draw.rounded_rectangle((x-rad*.12,y+rad*.18,x+rad*.13,y+rad*1.08),radius=2,fill=TRUNK+(255,))
    draw.rounded_rectangle((x-rad*.02,y+rad*.26,x+rad*.10,y+rad*.94),radius=2,fill=TRUNK_LIGHT+(150,))
    centers=[(-.52,.06,.66),(.48,.08,.68),(-.20,-.46,.73),(.22,-.42,.70),(0,-.08,.78)]
    cols=[TREE_DARK,TREE_A,TREE_B,TREE_C]
    for i,(dx,dy,rr) in enumerate(centers):
        c=cols[(i+variant+rnd.randint(0,2))%len(cols)];r2=rad*rr
        draw.ellipse((x+dx*rad-r2,y+dy*rad-r2,x+dx*rad+r2,y+dy*rad+r2),fill=c+(255,))
    draw.ellipse((x-rad*.42,y-rad*.75,x+rad*.10,y-rad*.24),fill=TREE_HI+(160,))
    draw.arc((x-rad*.72,y-rad*.42,x+rad*.55,y+rad*.55),20,150,fill=(205,237,116,120),width=max(1,int(rad*.10)))


def bush(draw,x,y,r,rnd):
    cols=[TREE_DARK,TREE_A,TREE_B,TREE_C]
    draw.ellipse((x-r*1.1,y+r*.25,x+r*1.2,y+r*.9),fill=(17,65,34,45))
    for i,(dx,dy) in enumerate([(-.48,.05),(.45,.08),(0,-.36)]):
        rr=r*(.72+rnd.random()*.16);draw.ellipse((x+dx*r-rr,y+dy*r-rr,x+dx*r+rr,y+dy*r+rr),fill=cols[(i+rnd.randint(0,3))%4]+(240,))
    draw.ellipse((x-r*.35,y-r*.55,x+r*.06,y-r*.18),fill=TREE_HI+(120,))


def flower(draw,x,y,r,col):
    for a in (0,math.pi/2,math.pi,3*math.pi/2):
        dx=math.cos(a)*r;dy=math.sin(a)*r;draw.ellipse((x+dx-r*.55,y+dy-r*.55,x+dx+r*.55,y+dy+r*.55),fill=col+(245,))
    draw.ellipse((x-r*.45,y-r*.45,x+r*.45,y+r*.45),fill=FLOWER_Y+(255,))


def rock(draw,x,y,r):
    pts=[(x-r,y+r*.35),(x-r*.55,y-r*.55),(x+r*.15,y-r*.8),(x+r,y-r*.05),(x+r*.65,y+r*.65),(x-r*.2,y+r*.8)]
    draw.polygon([(a+2,b+3) for a,b in pts],fill=(25,57,36,50));draw.polygon(pts,fill=ROCK+(230,));draw.line(pts+[pts[0]],fill=(104,100,78,220),width=2);draw.ellipse((x-r*.45,y-r*.48,x+r*.1,y-r*.15),fill=ROCK_HI+(140,))


def base_background(rnd):
    arr=np.zeros((WORK_H,WORK_W,3),dtype=np.uint8)
    for y in range(WORK_H):
        t=y/(WORK_H-1);col=np.array(FOREST_TOP)*(1-t)+np.array(FOREST_BOTTOM)*t;arr[y,:,:]=col.astype(np.uint8)
    noise=np.random.default_rng(rnd.randint(0,2**32-1)).normal(0,4,(WORK_H,WORK_W,1))
    arr=np.clip(arr.astype(np.float32)+noise,0,255).astype(np.uint8)
    return Image.fromarray(arr,'RGB').filter(ImageFilter.GaussianBlur(.45))


def reillustrate(im,name):
    seed=int(hashlib.sha1(name.encode()).hexdigest()[:8],16);rnd=random.Random(seed)
    src=im.convert('RGB').resize((WORK_W,WORK_H),Image.Resampling.LANCZOS);arr=np.asarray(src)
    left,right,center=choose_fairway_corridor(arr)
    out=base_background(rnd);d=ImageDraw.Draw(out,'RGBA')

    # Layered playable corridor with soft depth/shadow.
    contour(d,polygon_from_lr(left,right,80),COURSE+(255,),COURSE_EDGE+(255,),5,True)
    contour(d,polygon_from_lr(left,right,43),ROUGH+(255,),ROUGH_EDGE+(255,),4,True)
    contour(d,polygon_from_lr(left,right,0),FAIR+(255,),FAIR_EDGE+(255,),4,True)
    # subtle mowing stripes
    for y0 in range(24,WORK_H-40,54):
        y1=min(WORK_H-1,y0+26);poly=[]
        for y in range(y0,y1+1,4):poly.append((left[y]+4,y))
        for y in range(y1,y0-1,-4):poly.append((right[y]-4,y))
        if len(poly)>3:d.polygon(poly,fill=FAIR_ALT+(80,))

    r=arr[:,:,0].astype(np.int16);g=arr[:,:,1].astype(np.int16);b=arr[:,:,2].astype(np.int16);hi=np.max(arr,axis=2).astype(np.int16);lo=np.min(arr,axis=2).astype(np.int16);sat=hi-lo;yy,xx=np.indices((WORK_H,WORK_W))
    bunker_band=(xx>=left[:,None]-36)&(xx<=right[:,None]+36)
    water_band=(xx>=left[:,None]-92)&(xx<=right[:,None]+92)
    bunker_mask=(hi>180)&(sat<88)&bunker_band
    water_mask=(b>100)&((b-g)>2)&((b-r)>14)&(sat>45)&water_band
    for box in component_blobs(bunker_mask,18,3500):bunker(d,box,rnd)
    for box in component_blobs(water_mask,22,17000):water(d,box,rnd)

    # Dense but controlled storybook vegetation along both sides.
    for y in range(32,WORK_H-28,38):
        for side in (-1,1):
            edge=left[y] if side<0 else right[y]
            for layer in range(2):
                off=rnd.randint(27+layer*21,48+layer*31);x=edge-off if side<0 else edge+off;x=max(18,min(WORK_W-18,x))
                if rnd.random()<.67:tree(d,x,y+rnd.randint(-8,8),rnd.randint(12,20),rnd,(y//38+layer)%3)
                else:bush(d,x,y+rnd.randint(-7,7),rnd.randint(9,15),rnd)
    # Small flowers, bushes, rocks create the hand-painted richness missing from vector versions.
    flower_cols=[FLOWER_Y,FLOWER_P,FLOWER_W,FLOWER_B]
    for i in range(70):
        y=rnd.randint(48,WORK_H-48);side=-1 if rnd.random()<.5 else 1;edge=left[y] if side<0 else right[y];x=edge-rnd.randint(42,88) if side<0 else edge+rnd.randint(42,88);x=max(10,min(WORK_W-10,x))
        q=rnd.random()
        if q<.55:flower(d,x,y,rnd.randint(2,4),flower_cols[i%4])
        elif q<.82:bush(d,x,y,rnd.randint(5,9),rnd)
        else:rock(d,x,y,rnd.randint(4,8))

    # Green / flag / cup: concentric soft shapes, no flat vector disc.
    gy=58;gx=center[gy];gw=max(74,(right[gy]-left[gy])*.72)
    d.ellipse((gx-gw*.58+3,gy-39+5,gx+gw*.58+3,gy+40+5),fill=(25,83,39,65))
    d.ellipse((gx-gw*.58,gy-39,gx+gw*.58,gy+40),fill=GREEN+(255,),outline=GREEN_EDGE+(255,),width=4)
    d.ellipse((gx-gw*.36,gy-24,gx+gw*.20,gy+12),fill=(188,235,107,150))
    d.ellipse((gx-5,gy-2,gx+5,gy+8),fill=(73,75,40,160))
    d.line((gx,gy+22,gx,gy-30),fill=(103,65,38,255),width=5);d.polygon([(gx,gy-30),(gx+28,gy-20),(gx,gy-9)],fill=(242,75,47,255))

    # Storybook route: white dashed strategy line with soft dark offset.
    route=list(range(WORK_H-62,98,-24))
    for i,y in enumerate(route):
        if i%2==0:
            x=float(center[y]);y2=max(96,y-14);x2=float(center[y2])
            d.line((x+2,y+3,x2+2,y2+3),fill=(20,76,41,95),width=7);d.line((x,y,x2,y2),fill=(255,255,242,235),width=4)

    # Tee platform + player ball.
    ty=WORK_H-46;tx=center[ty];d.ellipse((tx-32,ty-19,tx+32,ty+20),fill=(126,191,73,220),outline=(59,132,50,235),width=3);d.ellipse((tx-15,ty-16,tx+15,ty+14),fill=(255,255,251,255),outline=(60,88,54,255),width=4);d.ellipse((tx-8,ty-11,tx+1,ty-4),fill=(255,255,255,180))

    # Gentle painted finish, richer saturation without destroying contours.
    out=out.filter(ImageFilter.GaussianBlur(.22));out=ImageEnhance.Color(out).enhance(1.07);out=ImageEnhance.Contrast(out).enhance(1.03)
    return out.resize((OUT_W,OUT_H),Image.Resampling.LANCZOS)

manifest=[];samples=[]
SAMPLE={'yardage_kamishihoro_c01.jpg','yardage_furano_palmer15.jpg','yardage_sahoro_07.jpg','yardage_royallinks_queens07.jpg','yardage_naepo_01.jpg'}
for fp in FILES:
    with Image.open(fp) as src:before=src.size;out=reillustrate(src,fp.name)
    out.save(fp,'JPEG',quality=95,subsampling=0,optimize=True,progressive=True);manifest.append(f'{fp.name}\t{before[0]}x{before[1]} -> {OUT_W}x{OUT_H}')
    if fp.name in SAMPLE:samples.append((fp.name,out.copy()))

(TMP/'manifest.txt').write_text('\n'.join(manifest)+'\n')
if samples:
    samples.sort();tile_w=300;tile_h=500;W=len(samples)*315+30;H=590;sheet=Image.new('RGB',(W,H),(249,249,231));sd=ImageDraw.Draw(sheet)
    try:f=ImageFont.truetype('/tmp/Jua-Regular.ttf',26);sf=ImageFont.truetype('/tmp/Jua-Regular.ttf',17)
    except Exception:f=sf=None
    sd.text((26,18),'V1.14.6 · REAL HOLE → ILLUSTRATED STORYBOOK',fill=INK,font=f)
    for idx,(nm,im) in enumerate(samples):
        x=20+idx*315;y=58;thumb=im.copy();thumb.thumbnail((tile_w,tile_h),Image.Resampling.LANCZOS);bx=x+(tile_w-thumb.width)//2;by=y+(tile_h-thumb.height)//2;sheet.paste(thumb,(bx,by));sd.rounded_rectangle((x,y,x+tile_w,y+tile_h),radius=24,outline=(76,157,91),width=4);sd.text((x+6,y+510),nm.replace('yardage_','').replace('.jpg',''),fill=INK,font=sf)
    sheet.save(TMP/'yardage-concept-samples.jpg','JPEG',quality=94,subsampling=0)

print('V1.14.6: 135 real holes professionally re-illustrated in layered storybook style')
print('Preserved: TEE→GREEN centerline/dogleg, obstacle extraction and live GPS mapping; upgraded: vegetation, shadows, texture, water, bunkers, route')
