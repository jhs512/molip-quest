"""Check required release containers. Does not certify code signing, notarization or runtime."""
import sys
from pathlib import Path


def verify(root):
    windows = root / 'molip-quest-windows-x64-setup.exe'
    macos = root / 'molip-quest-macos-arm64.dmg'
    for path in (windows, macos):
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f'Missing installer: {path.name}')
    with windows.open('rb') as stream:
        if stream.read(2) != b'MZ':
            raise ValueError('Windows installer is not an executable')
    with macos.open('rb') as stream:
        # A UDIF disk image ends with a 512-byte 'koly' trailer.
        stream.seek(-512, 2)
        if stream.read(4) != b'koly':
            raise ValueError('macOS disk image has no UDIF trailer')


if __name__ == '__main__':
    verify(Path(sys.argv[1]))
    print('Both installer containers are present. Signing and device testing are separate release requirements.')
