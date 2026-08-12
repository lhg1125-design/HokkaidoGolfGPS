from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
old='''        void setLocation(Location l) {
            location=l; lastFixElapsed=SystemClock.elapsedRealtime();'''
new='''        void setLocation(Location l) {
            if(previewMode)return;
            location=l; lastFixElapsed=SystemClock.elapsedRealtime();'''
if old not in s: raise SystemExit('v1.4.3 setLocation pattern missing')
s=s.replace(old,new,1)
s=s.replace('V1.4.2 · FIVE SCREEN GPS','V1.4.3 · FIVE SCREEN GPS')
p.write_text(s)
print('applied v1.4.3 stable synthetic preview location')
