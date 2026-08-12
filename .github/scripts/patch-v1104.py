from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.10.3 · JP/KR FULL HOLE' not in s:
    raise SystemExit('v1.10.4 requires v1.10.3 JP/KR full-hole renderer')
s=s.replace('V1.10.3 · JP/KR FULL HOLE','V1.10.4 · HOKKAIDO FULL HOLE',1)

old='''            if(selected==1)return variant==0?("yardage_furano_palmer"+hh):("yardage_furano_king"+hh);\n            if(selected==4)return variant==0?("yardage_royallinks_queens"+hh):("yardage_royallinks_kings"+hh);'''
new='''            if(selected==1)return variant==0?("yardage_furano_palmer"+hh):("yardage_furano_king"+hh);\n            if(selected==2)return "yardage_sahoro_"+hh;\n            if(selected==4)return variant==0?("yardage_royallinks_queens"+hh):("yardage_royallinks_kings"+hh);'''
if old not in s:
    raise SystemExit('v1.10.4 full-hole resource anchor missing')
s=s.replace(old,new,1)

old='String srcLabel=selected==4?"ROYAL LINKS OFFICIAL FULL HOLE":"PRINCE OFFICIAL FULL HOLE";'
new='String srcLabel=selected==2?"RAKUTEN GORA FULL HOLE":(selected==4?"ROYAL LINKS OFFICIAL FULL HOLE":"PRINCE OFFICIAL FULL HOLE");'
if old not in s:
    raise SystemExit('v1.10.4 source label anchor missing')
s=s.replace(old,new,1)

p.write_text(s)
print('applied v1.10.4 Sahoro 18-hole Rakuten GORA full-hole renderer')
