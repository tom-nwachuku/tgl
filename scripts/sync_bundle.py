"""Build/check the portable skill bundle from the canonical repository files."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tgl_installer', ROOT / 'install/tgl-install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
FILES = installer.SKILL_FILES
BUNDLE = ROOT / 'connector/skill-bundle'


def sync(check=False):
    expected = {name:(ROOT / name).read_bytes() for name in FILES}
    manifest = {'version':'1.1.0', 'files':{name:hashlib.sha256(data).hexdigest() for name,data in expected.items()}}
    expected['VERSION'] = b'1.1.0\n'
    expected['MANIFEST.json'] = (json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode()
    if check:
        wrong = [name for name,data in expected.items() if not (BUNDLE/name).is_file() or (BUNDLE/name).read_bytes()!=data]
        extras = [str(p.relative_to(BUNDLE)) for p in BUNDLE.rglob('*') if p.is_file() and str(p.relative_to(BUNDLE)) not in expected]
        if wrong or extras:
            raise SystemExit('Bundle drift: '+repr({'changed':wrong,'extra':extras}))
    else:
        for name,data in expected.items():
            p=BUNDLE/name
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(data)
    print('Bundle matches canonical skill: %d files' % len(expected))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true')
    sync(ap.parse_args().check)
