from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()
old='selected=0; variant=0; hole=4;'
new='selected=FieldGpsV09Activity.this.getIntent().getIntExtra("previewCourse",0); variant=FieldGpsV09Activity.this.getIntent().getIntExtra("previewVariant",0); hole=FieldGpsV09Activity.this.getIntent().getIntExtra("previewHole",selected>=3?1:4);'
if old not in s:
    raise SystemExit('v1.7.0 preview course selector anchor missing')
s=s.replace(old,new,1)
old2='demo.setLatitude(43.2587150);demo.setLongitude(143.2283600);demo.setAccuracy(5f);'
new2='if(selected==3){demo.setLatitude(36.6743245);demo.setLongitude(126.6698247);}else if(selected==4){demo.setLatitude(36.7224490956);demo.setLongitude(126.3387438841);}else{demo.setLatitude(43.2587150);demo.setLongitude(143.2283600);}demo.setAccuracy(5f);'
if old2 not in s:
    raise SystemExit('v1.7.0 preview GPS anchor missing')
s=s.replace(old2,new2,1)
p.write_text(s)
print('applied v1.7.0 Korea-selectable preview injection')
