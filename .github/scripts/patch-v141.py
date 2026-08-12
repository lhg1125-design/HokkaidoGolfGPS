from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

def rep(old,new,label,count=1):
    global s
    if old not in s: raise SystemExit('v1.4.1 missing '+label)
    s=s.replace(old,new,count)

# CI/preview gets an internal synthetic GPS fix so the screenshots demonstrate the real GPS target engine.
rep('''            if (previewMode) { selected=0; variant=0; hole=11; }
            else {''','''            if (previewMode) {
                selected=0; variant=0; hole=11;
                Location demo=new Location(LocationManager.GPS_PROVIDER);
                demo.setLatitude(43.2585100);demo.setLongitude(143.2283600);demo.setAccuracy(5f);
                demo.setTime(System.currentTimeMillis());demo.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos());
                location=demo;lastFixElapsed=SystemClock.elapsedRealtime();
            }
            else {''','preview GPS')

# Clean baked headers completely: Canvas origin begins below the Android status bar.
rep('RectF head=new RectF(0,h*.035f,w,h*.145f);gradient(c,head,DEEP,GREEN,0);','RectF head=new RectF(0,0,w,h*.145f);gradient(c,head,DEEP,GREEN,0);','input header cover')
rep('RectF header=new RectF(0,h*.035f,w,h*.128f);gradient(c,header,DEEP,GREEN,0);','RectF header=new RectF(0,0,w,h*.128f);gradient(c,header,DEEP,GREEN,0);','card header cover')

# Score-input optical spacing: separate player tag, relative score, labels, and values.
rep('''                goldText(c,rel,card.left+136,card.top+34,16.5f,delta>0?CORAL:(delta<0?GREEN:INK));
                text(c,"타수",card.left+115,card.top+78,13,Color.GRAY,true);
                goldText(c,""+st,card.left+226,card.top+92,34f,INK);
                text(c,"퍼트",card.left+420,card.top+78,13,Color.GRAY,true);
                goldText(c,""+pu,card.left+535,card.top+92,34f,INK);''','''                goldText(c,rel,card.left+144,card.top+34,15.5f,delta>0?CORAL:(delta<0?GREEN:INK));
                text(c,"타수",card.left+112,card.top+83,12.5f,Color.GRAY,true);
                goldText(c,""+st,card.left+238,card.top+88,34f,INK);
                text(c,"퍼트",card.left+410,card.top+83,12.5f,Color.GRAY,true);
                goldText(c,""+pu,card.left+532,card.top+88,34f,INK);''','score input spacing')

# Crop only the approved bear/cart artwork, avoiding surrounding title/sign text.
rep('''            Rect src=new Rect((int)(v12Home.getWidth()*.50f),(int)(v12Home.getHeight()*.11f),(int)(v12Home.getWidth()*.83f),(int)(v12Home.getHeight()*.28f));
            RectF dst=new RectF(w*.58f,h*.055f,w*.96f,h*.245f);c.drawBitmap(v12Home,src,dst,p);''','''            Rect src=new Rect((int)(v12Home.getWidth()*.56f),(int)(v12Home.getHeight()*.16f),(int)(v12Home.getWidth()*.80f),(int)(v12Home.getHeight()*.245f));
            RectF dst=new RectF(w*.64f,h*.060f,w*.95f,h*.205f);c.drawBitmap(v12Home,src,dst,p);''','bear crop')

s=s.replace('V1.4 · FIVE SCREEN GPS','V1.4.1 · FIVE SCREEN GPS')
p.write_text(s)
print('applied v1.4.1 preview GPS + header/spacing/artwork crop polish')
