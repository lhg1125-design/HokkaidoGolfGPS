from pathlib import Path
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
manifest = ET.parse(root / 'app/src/main/AndroidManifest.xml').getroot()
ns = '{http://schemas.android.com/apk/res/android}'
assert not manifest.findall('uses-permission'), 'Collector must request no permissions'
app = manifest.find('application')
assert app is not None
assert not app.findall('service')
assert not app.findall('receiver')
assert not app.findall('provider')
assert len(app.findall('activity')) == 1
assert app.attrib.get(ns + 'allowBackup') == 'false'
assert app.attrib.get(ns + 'usesCleartextTraffic') == 'false'
source = '\n'.join(p.read_text(encoding='utf-8') for p in (root / 'app/src/main/java').rglob('*.java'))
for forbidden in ['TWUtil', 'ProcessBuilder', 'Runtime.getRuntime', 'getRuntime().exec', 'android.permission.INTERNET', 'android.permission.WRITE_EXTERNAL_STORAGE', 'android.permission.MANAGE_EXTERNAL_STORAGE', 'sendBroadcast(', 'startForegroundService(', 'startService(', 'Class.forName(', 'DexClassLoader']:
    assert forbidden not in source, forbidden
assert 'com.tw.ac' in source and 'com.zht.car.accontroller' in source
assert 'ZipOutputStream' in source
assert 'report.json' in source
assert 'FileInputStream(source)' in source
assert 'MediaStore.Downloads.EXTERNAL_CONTENT_URI' in source
print('PASS: no permissions, services, receivers, MCU commands, or network access')
print('PASS: bounded APK-only collection and user-visible ZIP export are present')
