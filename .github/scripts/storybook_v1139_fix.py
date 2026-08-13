from pathlib import Path

p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
old='speech(c,w*.19f,h*.777f,"한눈에 보고, 한 번에 입력!",DEEP);nav(c);'
new='speech(c,w*.19f,h*.777f,"한눈에 보고, 한 번에 입력!",DEEP);setFourNav(w,h);drawGoldenNav(c);'
if old not in s:
    raise SystemExit('storybook nav compatibility anchor missing')
s=s.replace(old,new,1)
p.write_text(s)
print('storybook_v1139 nav compatibility fix applied')
