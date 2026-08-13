from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

build='        private static final String BUILD_V1131="V1.13.1 · NAEPO FIELD TEST";'
if build in s:
    s=s.replace(build,'        private static final String BUILD_V1132="V1.13.2 · NAEPO REAL YARDAGE";',1)
elif 'naepoActiveGreenV1131()' not in s:
    raise SystemExit('v1.13.2 requires the Naepo field-test base')

# -----------------------------------------------------------------------------
# 1) Real physical-hole resource mapping. Logical H10..H18 intentionally reuse
#    physical H1..H9 because Naepo is a 9-hole / two-green course.
# -----------------------------------------------------------------------------
old='''            if(selected==2)return "yardage_sahoro_"+hh;\n            if(selected==4)return variant==0?("yardage_royallinks_queens"+hh):("yardage_royallinks_kings"+hh);'''
new='''            if(selected==2)return "yardage_sahoro_"+hh;\n            if(selected==3){int ph=((hole-1)%9)+1;String pp=ph<10?("0"+ph):(""+ph);return "yardage_naepo_"+pp;}\n            if(selected==4)return variant==0?("yardage_royallinks_queens"+hh):("yardage_royallinks_kings"+hh);'''
if old not in s: raise SystemExit('v1.13.2 full-hole resource anchor missing')
s=s.replace(old,new,1)

# -----------------------------------------------------------------------------
# 2) Published Naepo WHITE-tee meter / par packs. The same physical hole has a
#    Red-flag and Yellow-flag setup; the first/second loop follows the selected
#    RED->YELLOW or YELLOW->RED order. GPS field calibration remains available
#    and takes precedence once TEE/GREEN references are captured.
# -----------------------------------------------------------------------------
marker='        private GeoRef naepoCaptureFixV1131(){'
pos=s.find(marker)
if pos<0: raise SystemExit('v1.13.2 Naepo helper anchor missing')
helpers=r'''        private boolean naepoRedFlagV1132(int logicalHole){
            boolean second=logicalHole>9;return variant==0?!second:second;
        }
        private int naepoPublishedMetersV1132(int logicalHole){
            final int[] red={317,122,358,426,316,473,130,296,299};
            final int[] yellow={302,153,468,306,386,464,128,274,325};
            int ph=((logicalHole-1)%9);return naepoRedFlagV1132(logicalHole)?red[ph]:yellow[ph];
        }
        private int naepoPublishedParV1132(int logicalHole){
            final int[] red={4,3,4,5,4,5,3,4,4};
            final int[] yellow={4,3,5,4,4,5,3,4,4};
            int ph=((logicalHole-1)%9);return naepoRedFlagV1132(logicalHole)?red[ph]:yellow[ph];
        }
        private String naepoRealMapLabelV1132(){
            return "REAL MAP · "+(naepoRedFlagV1132(hole)?"RED":"YELLOW")+" GREEN";
        }

'''
s=s[:pos]+helpers+s[pos:]

# Real published par replaces the early field-only manual PAR placeholder.
old='''            if(selected==3){int ph=((h-1)%9)+1;return clamp(statePrefs.getInt("naepo_par_"+ph,4),3,5);}'''
if old in s:
    s=s.replace(old,'            if(selected==3)return naepoPublishedParV1132(h);',1)
else:
    raise SystemExit('v1.13.2 Naepo par anchor missing')

# Published distance is usable from the first tee. A captured TEE+GREEN GPS
# measurement overrides it so the field test still measures real device error.
old='''            if(selected==3)return fieldGpsMetersV190();'''
new='''            if(selected==3){int f=fieldGpsMetersV190();return f>0?f:naepoPublishedMetersV1132(hole);}'''
if old not in s: raise SystemExit('v1.13.2 verified meter anchor missing')
s=s.replace(old,new,1)

old='''            int m=fieldGpsMetersV190();return m>0?("FIELD GPS "+m+"m"):"FIELD CAL REQUIRED";'''
new='''            int m=fieldGpsMetersV190();return m>0?("FIELD GPS "+m+"m"):("TOTAL "+naepoPublishedMetersV1132(hole)+"m");'''
if old not in s: raise SystemExit('v1.13.2 verified label anchor missing')
s=s.replace(old,new,1)

old='''            return fieldGpsMetersV190()>0?"GPS FIELD VERIFIED":"GPS CALIBRATION";'''
new='''            return fieldGpsMetersV190()>0?"NAEPO REAL + GPS":"NAEPO REAL MAP";'''
if old not in s: raise SystemExit('v1.13.2 yardage source anchor missing')
s=s.replace(old,new,1)

# Source footer and home chip must no longer imply a calibration-only/schematic
# course. The source screenshot is a published real yardage sheet; we crop only
# its course diagram and stylize it without changing geometry/hazards.
old='''String srcLabel=selected==2?"RAKUTEN GORA FULL HOLE":(selected==4?"ROYAL LINKS OFFICIAL FULL HOLE":"PRINCE OFFICIAL FULL HOLE");'''
new='''String srcLabel=selected==3?"NAEPO REAL YARDAGE":(selected==2?"RAKUTEN GORA FULL HOLE":(selected==4?"ROYAL LINKS OFFICIAL FULL HOLE":"PRINCE OFFICIAL FULL HOLE"));'''
if old not in s: raise SystemExit('v1.13.2 source-footer anchor missing')
s=s.replace(old,new,1)

s=s.replace('"NAEPO FIELD"','"NAEPO REAL"')

# -----------------------------------------------------------------------------
# 3) Add a small active-green chip over the real image. We deliberately avoid
#    drawing a fabricated pinpoint over one of the two greens: the published map
#    is kept geometrically intact, while the chip states which flag is active.
# -----------------------------------------------------------------------------
nav_anchor='''            drawFieldNavV1110(c,stage,totalM);'''
idx=s.find(nav_anchor)
if idx<0: raise SystemExit('v1.13.2 full-hole nav anchor missing')
line_end=s.find('\n',idx)
insert='''\n            if(selected==3){\n                RectF ng=new RectF(stage.left+8,stage.top+7,stage.left+128,stage.top+31);\n                int nc=naepoRedFlagV1132(hole)?Color.rgb(218,62,70):Color.rgb(241,184,32);\n                box(c,ng,Color.argb(238,255,255,245),12);\n                textFit(c,naepoRealMapLabelV1132(),ng.left+7,ng.centerY()+3,ng.right-7,5.8f,nc,true);\n            }'''
s=s[:line_end]+insert+s[line_end:]

# Make the Naepo field guide useful from the first round even before capture.
old='''                return m>0?("FIELD CAL 완료 · TEE↔GREEN 직선 "+m+"m · 벙커/워터 GPS를 현장에서 추가 저장"):("내포 9H TWO-GREEN 테스트 · TEE와 GREEN을 저장하면 이 홀의 실제 GPS 거리로 전환");'''
new='''                return m>0?("REAL 야디지 + FIELD CAL · 실측 "+m+"m · GPS 오차와 남은거리 확인"):("REAL 9H TWO-GREEN 야디지 · "+naepoPublishedMetersV1132(hole)+"m · TEE 저장 후 위치 추적 시작");'''
if old in s:s=s.replace(old,new,1)

p.write_text(s)
print('applied v1.13.2 Naepo real 9-hole yardage + published Red/Yellow meters')
