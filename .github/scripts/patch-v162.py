from pathlib import Path
p=Path('app/src/main/java/com/hokkaidogolf/trip/FieldGpsV09Activity.java')
s=p.read_text()

if 'V1.6.1 · HAZARD + BACKUP' not in s:
    raise SystemExit('v1.6.2 base version not found')
s=s.replace('V1.6.1 · HAZARD + BACKUP','V1.6.2 · PLAYER NAMES',1)

# Native two-character player-name entry dialog.
s=s.replace('import android.app.Activity;','import android.app.Activity;\nimport android.app.AlertDialog;',1)
s=s.replace('import android.content.Context;','import android.content.Context;\nimport android.text.InputFilter;\nimport android.text.InputType;',1)
s=s.replace('import android.view.View;','import android.view.View;\nimport android.widget.EditText;\nimport android.widget.LinearLayout;\nimport android.widget.TextView;',1)

anchor='''        private final RectF packExportBtn=new RectF(),packImportBtn=new RectF();'''
if anchor not in s:
    raise SystemExit('v1.6.2 name button rect anchor missing')
s=s.replace(anchor,anchor+'''\n        private final RectF playerNamesBtn=new RectF();''',1)

marker='''        private void saveState(){'''
idx=s.find(marker)
if idx<0:
    raise SystemExit('v1.6.2 helper insertion marker missing')
helpers=r'''        private String playerName(int i){
            String n=statePrefs.getString("player_name_"+i,"");
            if(n==null)n="";n=n.trim();
            return n.length()==2?n:("P"+(i+1));
        }
        private boolean playerNamesReady(){return statePrefs.getBoolean("player_names_set",false);}
        private void showPlayerNamesDialog(final boolean startAfter){
            final EditText[] fields=new EditText[4];
            LinearLayout root=new LinearLayout(ctx);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(48,20,48,8);
            TextView guide=new TextView(ctx);guide.setText("P1~P4 이름을 두 글자로 입력하세요. 한 번 저장하면 계속 사용됩니다.");guide.setTextSize(15);guide.setTextColor(INK);guide.setPadding(0,0,0,18);guide.setTypeface(Typeface.create("sans-serif-rounded",Typeface.NORMAL));root.addView(guide);
            String[] demo={"가람","나래","다온","라온"};
            for(int i=0;i<4;i++){
                LinearLayout row=new LinearLayout(ctx);row.setOrientation(LinearLayout.HORIZONTAL);row.setPadding(0,7,0,7);
                TextView lab=new TextView(ctx);lab.setText("P"+(i+1));lab.setTextSize(18);lab.setTextColor(DEEP);lab.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));lab.setGravity(android.view.Gravity.CENTER_VERTICAL);
                row.addView(lab,new LinearLayout.LayoutParams(92,72));
                EditText ed=new EditText(ctx);fields[i]=ed;ed.setSingleLine(true);ed.setTextSize(20);ed.setTextColor(INK);ed.setHint("두 글자");ed.setSelectAllOnFocus(true);ed.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);ed.setFilters(new InputFilter[]{new InputFilter.LengthFilter(2)});ed.setTypeface(Typeface.create("sans-serif-rounded",Typeface.BOLD));
                String saved=statePrefs.getString("player_name_"+i,"");if(saved!=null&&saved.trim().length()==2)ed.setText(saved.trim());else if(previewMode)ed.setText(demo[i]);
                row.addView(ed,new LinearLayout.LayoutParams(0,72,1f));root.addView(row);
            }
            final AlertDialog dlg=new AlertDialog.Builder(ctx).setTitle("플레이어 이름 설정 · 2글자").setView(root).setPositiveButton("저장",null).setNegativeButton("취소",null).create();
            dlg.setOnShowListener(x->dlg.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
                String[] names=new String[4];
                for(int i=0;i<4;i++){names[i]=fields[i].getText().toString().trim();if(names[i].length()!=2){fields[i].setError("두 글자로 입력");fields[i].requestFocus();return;}}
                SharedPreferences.Editor ed=statePrefs.edit();for(int i=0;i<4;i++)ed.putString("player_name_"+i,names[i]);ed.putBoolean("player_names_set",true).apply();
                dlg.dismiss();showToast("플레이어 이름 저장 완료");if(startAfter){screen=1;saveState();}invalidate();
            }));
            dlg.show();
        }

'''
s=s[:idx]+helpers+s[idx:]

# Replace P1~P4 display labels with the saved two-character names everywhere possible.
s=s.replace('"P"+(i+1)', 'playerName(i)')
s=s.replace('"P"+(pl+1)', 'playerName(pl)')
s=s.replace('String[] labs={"H","PAR","P1","P2","P3","P4"};','String[] labs={"H","PAR",playerName(0),playerName(1),playerName(2),playerName(3)};',1)

# Score input gets a dedicated edit button so names can be corrected later.
anchor='''            text(c,ko[selected]+" / H"+hole+" / PAR "+par,m,h*.112f,14,Color.rgb(218,242,222),true);\n            drawHolePager(c,h*.150f);'''
if anchor not in s:
    raise SystemExit('v1.6.2 score-input name button anchor missing')
s=s.replace(anchor,'''            text(c,ko[selected]+" / H"+hole+" / PAR "+par,m,h*.112f,14,Color.rgb(218,242,222),true);\n            playerNamesBtn.set(w*.735f,h*.065f,w*.945f,h*.118f);goldButton(c,playerNamesBtn,Color.argb(50,255,255,255),"이름 수정",Color.WHITE,14.5f);\n            drawHolePager(c,h*.150f);''',1)

# Round summary identifies the primary player's saved name.
s=s.replace('goldText(c,"TOTAL",totalCard.centerX(),h*.315f,18f,Color.rgb(216,242,222));','goldText(c,playerName(0)+" · TOTAL",totalCard.centerX(),h*.315f,18f,Color.rgb(216,242,222));',1)

# One-time name entry is required before the first round begins.
start_anchor='''                if(selected>=0&&start.contains(x,y)){screen=1;saveState();invalidate();return true;}'''
if start_anchor not in s:
    raise SystemExit('v1.6.2 first-round name entry anchor missing')
s=s.replace(start_anchor,'''                if(selected>=0&&start.contains(x,y)){if(!playerNamesReady()){showPlayerNamesDialog(true);return true;}screen=1;saveState();invalidate();return true;}''',1)

# Later edits from score input.
touch_anchor='''            if(screen==2){\n                int par=currentPar();'''
if touch_anchor not in s:
    raise SystemExit('v1.6.2 edit-name touch anchor missing')
s=s.replace(touch_anchor,'''            if(screen==2){\n                if(playerNamesBtn.contains(x,y)){showPlayerNamesDialog(false);return true;}\n                int par=currentPar();''',1)

p.write_text(s)
print('applied v1.6.2 one-time two-character player names')
