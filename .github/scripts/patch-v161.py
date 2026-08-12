from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.6 · FIELD GPS CAPTURE' not in s:
    raise SystemExit('v1.6.1 base version not found')
s=s.replace('V1.6 · FIELD GPS CAPTURE','V1.6.1 · HAZARD + BACKUP',1)

# Imports for offline Field Pack backup / restore.
s=s.replace('import android.content.Context;','import android.content.ClipData;\nimport android.content.ClipboardManager;\nimport android.content.Context;',1)
s=s.replace('import android.view.View;','import android.view.View;\nimport org.json.JSONObject;\nimport java.util.Iterator;',1)

# Extra interactive rects.
anchor='''        private final RectF holePrevBtn=new RectF(),holeNextBtn=new RectF();'''
if anchor not in s:
    raise SystemExit('v1.6.1 rect anchor missing')
s=s.replace(anchor,anchor+'''\n        private final RectF hazardBunkerBtn=new RectF(),hazardWaterBtn=new RectF();\n        private final RectF packExportBtn=new RectF(),packImportBtn=new RectF();''',1)

# Draw saved hazard GPS summary + capture controls on live course after guide hazards.
anchor='''            drawHoleHazards(c,courseRect);\n            drawHolePager(c,h*.126f);'''
if anchor not in s:
    raise SystemExit('v1.6.1 course overlay anchor missing')
s=s.replace(anchor,'''            drawHoleHazards(c,courseRect);\n            drawCapturedHazardSummary(c,courseRect);\n            drawHazardCaptureButtons(c,courseRect);\n            drawHolePager(c,h*.126f);''',1)

# Add two offline Field Pack buttons to the round summary screen.
anchor='''            RectF shareBtn=new RectF(m,h*.765f,w-m,h*.838f);goldButton(c,shareBtn,Color.rgb(50,146,214),"공유하기",Color.WHITE,20f);\n            setFourNav(w,h);drawGoldenNav(c);'''
if anchor not in s:
    raise SystemExit('v1.6.1 summary button anchor missing')
s=s.replace(anchor,'''            RectF shareBtn=new RectF(m,h*.765f,w-m,h*.838f);goldButton(c,shareBtn,Color.rgb(50,146,214),"공유하기",Color.WHITE,20f);\n            packExportBtn.set(m,h*.852f,w*.485f,h*.905f);\n            packImportBtn.set(w*.515f,h*.852f,w-m,h*.905f);\n            goldButton(c,packExportBtn,Color.rgb(238,246,226),"PACK 백업",DEEP,16.5f);\n            goldButton(c,packImportBtn,Color.rgb(238,246,226),"PACK 복원",DEEP,16.5f);\n            setFourNav(w,h);drawGoldenNav(c);''',1)

# Insert hazard GPS and Field Pack helpers before scorecard rendering.
marker='        private void score(Canvas c){'
idx=s.find(marker)
if idx<0:
    raise SystemExit('v1.6.1 helper insertion marker missing')
helpers=r'''        private void drawHazardCaptureButtons(Canvas c,RectF r){
            float y2=r.bottom-12,y1=y2-42;
            hazardBunkerBtn.set(r.left+14,y1,r.centerX()-7,y2);
            hazardWaterBtn.set(r.centerX()+7,y1,r.right-14,y2);
            boolean ready=previewMode || (location!=null && location.getAccuracy()<=12 && fixAgeSec()<=15);
            int bBg=ready?Color.rgb(252,236,185):Color.argb(220,180,185,175);
            int wBg=ready?Color.rgb(216,241,250):Color.argb(220,180,185,175);
            goldButton(c,hazardBunkerBtn,bBg,"BUNKER GPS",DEEP,13.5f);
            goldButton(c,hazardWaterBtn,wBg,"WATER GPS",DEEP,13.5f);
        }

        private void drawCapturedHazardSummary(Canvas c,RectF r){
            GeoRef b=nearestHazard("b"),w=nearestHazard("w");
            float y=r.top+14;
            if(b!=null){
                String t=gpsUsable()?"B "+Math.round(distance(location,b.lat,b.lon))+"m":"B GPS";
                pill(c,new RectF(r.left+14,y,r.left+126,y+32),Color.argb(235,255,248,221),t,DEEP,7.6f);y+=36;
            }
            if(w!=null){
                String t=gpsUsable()?"W "+Math.round(distance(location,w.lat,w.lon))+"m":"W GPS";
                pill(c,new RectF(r.left+14,y,r.left+126,y+32),Color.argb(235,228,247,252),t,DEEP,7.6f);
            }
        }

        private String hazardKey(String type,int h,int slot){return "hz_"+type+"_"+selected+"_"+variant+"_"+h+"_"+slot;}
        private GeoRef getHazardRef(String type,int h,int slot){
            String k=hazardKey(type,h,slot);
            if(calPrefs.contains(k+"_lat")) return new GeoRef(Double.longBitsToDouble(calPrefs.getLong(k+"_lat",0)),Double.longBitsToDouble(calPrefs.getLong(k+"_lon",0)),false);
            if(previewMode && selected==0 && variant==0 && h==4){
                if(type.equals("b")&&slot==1) return new GeoRef(43.25936,143.22810,true);
                if(type.equals("w")&&slot==1) return new GeoRef(43.25902,143.22862,true);
            }
            return null;
        }
        private int savedHazardCount(String type,int h){int n=0;for(int i=1;i<=4;i++)if(getHazardRef(type,h,i)!=null)n++;return n;}
        private GeoRef nearestHazard(String type){
            GeoRef best=null;float bd=Float.MAX_VALUE;
            for(int i=1;i<=4;i++){
                GeoRef r=getHazardRef(type,hole,i);if(r==null)continue;
                if(!gpsUsable())return r;
                float d=distance(location,r.lat,r.lon);if(d<bd){bd=d;best=r;}
            }
            return best;
        }
        private void saveHazard(String type){
            if(location==null){showToast("GPS 위치를 먼저 잡아주세요");return;}
            if(!previewMode && (location.getAccuracy()>12 || fixAgeSec()>15)){showToast("GPS 품질이 안정된 뒤 저장하세요");return;}
            int kind=type.equals("b")?3:4;long now=SystemClock.uptimeMillis();
            String name=type.equals("b")?"BUNKER":"WATER";
            if(confirmKind!=kind || now>confirmUntil){confirmKind=kind;confirmUntil=now+3200;showToast(name+" 가장자리에서 한 번 더 눌러 저장");invalidate();return;}
            int slot=0;for(int i=1;i<=4;i++)if(getHazardRef(type,hole,i)==null){slot=i;break;}
            if(slot==0){showToast(name+" GPS 4개 저장됨");confirmKind=0;return;}
            String k=hazardKey(type,hole,slot);
            calPrefs.edit().putLong(k+"_lat",Double.doubleToRawLongBits(location.getLatitude())).putLong(k+"_lon",Double.doubleToRawLongBits(location.getLongitude())).putLong(k+"_ts",System.currentTimeMillis()).apply();
            confirmKind=0;confirmUntil=0;showToast("H"+hole+" "+name+" GPS #"+slot+" 저장 완료");invalidate();
        }

        private String buildFieldPackJson(){
            try{
                JSONObject root=new JSONObject();root.put("schema","HokkaidoGolfGPS.FieldPack.v1");root.put("createdAt",System.currentTimeMillis());
                JSONObject cal=new JSONObject();
                for(String k:calPrefs.getAll().keySet()){
                    Object v=calPrefs.getAll().get(k);if(v instanceof Long)cal.put(k,((Long)v).longValue());
                    else if(v instanceof Integer)cal.put(k,((Integer)v).intValue());else if(v instanceof String)cal.put(k,(String)v);
                }
                root.put("calibration",cal);return root.toString();
            }catch(Exception e){return "";}
        }
        private void exportFieldPack(){
            try{
                String json=buildFieldPackJson();if(json.length()==0){showToast("백업할 Field Pack이 없습니다");return;}
                ClipboardManager cm=(ClipboardManager)ctx.getSystemService(Context.CLIPBOARD_SERVICE);
                if(cm!=null)cm.setPrimaryClip(ClipData.newPlainText("HokkaidoGolfGPS Field Pack",json));
                Intent i=new Intent(Intent.ACTION_SEND);i.setType("text/plain");i.putExtra(Intent.EXTRA_SUBJECT,"HokkaidoGolfGPS Field Pack");i.putExtra(Intent.EXTRA_TEXT,json);
                ctx.startActivity(Intent.createChooser(i,"Field Pack 백업"));showToast("PACK 복사 완료 · 오프라인 백업 가능");
            }catch(Exception e){showToast("PACK 백업 실패");}
        }
        private void importFieldPack(){
            try{
                ClipboardManager cm=(ClipboardManager)ctx.getSystemService(Context.CLIPBOARD_SERVICE);
                if(cm==null || !cm.hasPrimaryClip() || cm.getPrimaryClip()==null){showToast("클립보드에 PACK이 없습니다");return;}
                CharSequence cs=cm.getPrimaryClip().getItemAt(0).coerceToText(ctx);if(cs==null){showToast("PACK 읽기 실패");return;}
                JSONObject root=new JSONObject(cs.toString());if(!root.optString("schema","").startsWith("HokkaidoGolfGPS.FieldPack")){showToast("지원하지 않는 PACK");return;}
                JSONObject cal=root.getJSONObject("calibration");SharedPreferences.Editor ed=calPrefs.edit();Iterator<String> it=cal.keys();int n=0;
                while(it.hasNext()){String k=it.next();Object v=cal.get(k);if(v instanceof Number){ed.putLong(k,((Number)v).longValue());n++;}else if(v instanceof String){ed.putString(k,(String)v);n++;}}
                ed.apply();showToast("FIELD PACK "+n+"개 복원 완료");invalidate();
            }catch(Exception e){showToast("PACK 형식 확인 필요");}
        }

'''
s=s[:idx]+helpers+s[idx:]

# Touch handling: hazard capture buttons live inside courseRect, so check them first.
touch_anchor='''            if(screen==1){\n                if(courseRect.contains(x,y)){'''
if touch_anchor not in s:
    raise SystemExit('v1.6.1 nested touch course anchor missing')
s=s.replace(touch_anchor,'''            if(screen==1){\n                if(hazardBunkerBtn.contains(x,y)){saveHazard("b");return true;}\n                if(hazardWaterBtn.contains(x,y)){saveHazard("w");return true;}\n                if(courseRect.contains(x,y)){''',1)

# Summary backup/restore touch handling near the start of ACTION_UP processing.
touch_top='''            if(e.getAction()!=MotionEvent.ACTION_UP)return true;float x=e.getX(),y=e.getY();'''
if touch_top not in s:
    raise SystemExit('v1.6.1 touch top anchor missing')
s=s.replace(touch_top,touch_top+'''\n            if(screen==4 && packExportBtn.contains(x,y)){exportFieldPack();return true;}\n            if(screen==4 && packImportBtn.contains(x,y)){importFieldPack();return true;}''',1)

p.write_text(s)
print('applied v1.6.1 hazard GPS capture + offline Field Pack backup/restore')
