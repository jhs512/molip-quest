"""Check required release containers. Does not certify mobile signing or runtime."""
import sys
import zipfile
from pathlib import Path


def verify(root):
    windows = root / 'molip-quest-windows-x64-setup.exe'
    android = root / 'molip-quest-android.apk'
    ios = root / 'molip-quest-ios.ipa'
    for path in (windows, android, ios):
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f'Missing installer: {path.name}')
    with windows.open('rb') as stream:
        if stream.read(2) != b'MZ':
            raise ValueError('Windows installer is not an executable')
    with zipfile.ZipFile(android) as apk:
        if 'AndroidManifest.xml' not in apk.namelist():
            raise ValueError('APK has no Android manifest')
    with zipfile.ZipFile(ios) as ipa:
        if not any(p.startswith('Payload/') and p.endswith('.app/Info.plist') for p in ipa.namelist()):
            raise ValueError('IPA has no iOS application payload')


if __name__ == '__main__':
    verify(Path(sys.argv[1]))
    print('All three installer containers are present. Signing and device testing are separate release requirements.')
