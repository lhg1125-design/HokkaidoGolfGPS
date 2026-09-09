from pathlib import Path
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
manifest=ET.parse(root/'app/src/main/AndroidManifest.xml').getroot()
app=manifest.find('application'); assert app is not None
assert not app.findall('service')
assert not app.findall('receiver')
assert not app.findall('provider')
assert len(app.findall('activity'))==1

src=(root/'app/src/main/java/com/vwid/hvaccontrolprobe/MainActivity.java').read_text(encoding='utf-8')
for forbidden in [
    'BOOT_COMPLETED','LOCKED_BOOT_COMPLETED','startService(','startForegroundService(',
    'AlarmManager','JobScheduler','0xC6','0xB7','0xB8','0xB9','0xBD','ARM CONTROL'
]:
    assert forbidden not in src, forbidden

# Read-only factory queries only. The 3-arg 0x010A query is copied from factory
# BNR/RZC/XP/BXF/JFT CanBox update activities, which issue it on screen open.
assert 'write2Read(0x010A)' in src
assert 'write2Read(0x0112)' in src
assert 'write3.invoke(tw,0x010A,0x00FF,1)' in src
assert 'write3.invoke(tw,0x050D,1,1)' in src
assert 'write3.invoke(tw,0x050D,1,0)' in src
assert 'short[] events={(short)0x010A,(short)0x0112,(short)0x0501,(short)0x050D}' in src
assert 'CANBOX RESPONSE' in src
assert 'msg.arg1==1?Event.CANBOX:Event.MCU' in src
assert 'LIVE HVAC RX' in src
print('PASS: CanBox trace contains no HVAC control or boot/background control')
print('PASS: exact factory read-only CanBox version query + MCU/config/HVAC capture present')
