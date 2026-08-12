from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

def rep(old,new,label,count=1):
    global s
    if old not in s: raise SystemExit('v1.4.2 missing '+label)
    s=s.replace(old,new,count)

# Preview-only clock never goes stale. Real field mode keeps the same 15 s safety lock.
rep('''        private int fixAgeSec(){if(location==null||lastFixElapsed==0)return 999;return (int)Math.min(999,(SystemClock.elapsedRealtime()-lastFixElapsed)/1000);}''','''        private int fixAgeSec(){if(previewMode&&location!=null)return 0;if(location==null||lastFixElapsed==0)return 999;return (int)Math.min(999,(SystemClock.elapsedRealtime()-lastFixElapsed)/1000);}''','preview fix age')

# Relative score becomes a clean status pill instead of crowding the P1/P2 label.
rep('''                goldText(c,rel,card.left+144,card.top+34,15.5f,delta>0?CORAL:(delta<0?GREEN:INK));
                text(c,"타수",card.left+112,card.top+83,12.5f,Color.GRAY,true);''','''                RectF relTag=new RectF(card.right-110,card.top+14,card.right-24,card.top+54);
                int relBg=delta>0?Color.rgb(255,235,228):(delta<0?Color.rgb(229,244,218):SOFT);
                int relFg=delta>0?CORAL:(delta<0?GREEN:INK);box(c,relTag,relBg,18);goldText(c,rel,relTag.centerX(),relTag.centerY(),15.5f,relFg);
                text(c,"타수",card.left+112,card.top+83,12.5f,Color.GRAY,true);''','relative score pill')

s=s.replace('V1.4.1 · FIVE SCREEN GPS','V1.4.2 · FIVE SCREEN GPS')
p.write_text(s)
print('applied v1.4.2 preview GPS freshness + score input optical status pill')
