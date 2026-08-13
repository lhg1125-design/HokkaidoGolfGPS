from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
old='''                int ph=((h-1)%9)+1;int pa=parForHole(h);double meters=pa==3?165.0:(pa==5?485.0:345.0);\n                double baseLat=36.6743245+(ph-5)*0.000055,baseLon=126.6698247+(ph-5)*0.000035;\n                double teeLat=baseLat-meters/111111.0,teeLon=baseLon;boolean second=h>9;boolean red=(variant==0?!second:second);\n                double greenLon=baseLon+(red?-0.00015:0.00015);'''
new='''                int ph=((h-1)%9)+1;double meters=naepoPublishedMetersV1132(h);\n                double baseLat=36.6743245+(ph-5)*0.000055,baseLon=126.6698247+(ph-5)*0.000035;\n                double teeLat=baseLat-meters/111111.0,teeLon=baseLon;\n                double greenLon=baseLon;'''
if old not in s:
    raise SystemExit('v1.13.2 SIM reference anchor missing')
s=s.replace(old,new,1)
p.write_text(s)
print('aligned V1.13.2 Naepo SIM references to published Red/Yellow meter pack')

# The next V1.13.3 patch is intentionally robust against small whitespace/body
# differences in the already-patched preview touch block. Harden that script
# immediately before it runs in the sequential patch chain.
fixer=Path('.github/scripts/fix-patch-v1133-touch.py')
if fixer.exists():
    code=fixer.read_text()
    exec(compile(code,str(fixer),'exec'),{})
