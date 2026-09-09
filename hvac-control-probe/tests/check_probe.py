from pathlib import Path
import re, xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
manifest=ET.parse(root/'app/src/main/AndroidManifest.xml').getroot()
app=manifest.find('application'); assert app is not None
assert not app.findall('service')
assert not app.findall('receiver')
assert not app.findall('provider')
assert len(app.findall('activity'))==1
src=(root/'app/src/main/java/com/vwid/hvaccontrolprobe/MainActivity.java').read_text(encoding='utf-8')
# No boot/startup vehicle command path.
for forbidden in ['BOOT_COMPLETED','LOCKED_BOOT_COMPLETED','startService(','startForegroundService(','AlarmManager','JobScheduler']:
    assert forbidden not in src, forbidden
# Exact legacy VW read and control dispatch only.
assert 'write4.invoke(tw,0x0501,what,2' in src
assert 'writeLegacy(0x90,0x21,0)' in src
assert 'writeLegacy(0xC6,cmd,value)' in src
for cmd in ['0xB7','0xB8','0xB9','0xBD']:
    assert cmd in src, cmd
# UI must require explicit arm and live state; no optimistic update.
assert 'armBox.isChecked()' in src
assert 'state.valid' in src
assert 'NO CONFIRM' in src
print('PASS: manual activity only; no boot/background vehicle control')
print('PASS: whitelisted VW query/control family and RX confirmation guards present')
