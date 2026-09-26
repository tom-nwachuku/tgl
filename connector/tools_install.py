"""Return the complete, build-time skill bundle after verifying its hashes."""
import hashlib
import json
from pathlib import Path
from mcp.server.mcpserver.exceptions import ToolError

BUNDLE_DIR = Path(__file__).resolve().parent / 'skill-bundle'
INSTRUCTIONS = (
    'These are skill files, not a completed installation. Save them to an isolated '
    'folder that Muse can read. Read SKILL.md and docs/tutorial.md, then follow '
    'the user-authorized installation. For a terminal install, run '
    'python3 install/tgl-install.py --yes --target YOUR_SKILL_FOLDER. '
    'Read back the installed SKILL.md before claiming success. The installed skill '
    'guides planning and reviewed builds; this hosted service cannot execute code. '
    'Human approval is a workflow instruction, not a server-enforced permission gate.'
)


def install():
    try:
        manifest = json.loads((BUNDLE_DIR/'MANIFEST.json').read_text())
        files = {}
        for name, digest in manifest['files'].items():
            if name.startswith('/') or '..' in Path(name).parts:
                raise ValueError('unsafe manifest path')
            data = (BUNDLE_DIR/name).read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError('bundle integrity mismatch')
            files[name] = data.decode('utf-8')
        files['VERSION'] = (BUNDLE_DIR/'VERSION').read_text()
        files['MANIFEST.json'] = (BUNDLE_DIR/'MANIFEST.json').read_text()
    except (OSError, ValueError, KeyError, TypeError):
        raise ToolError('The install bundle is unavailable or failed its integrity check. Retry later or use the canonical GitHub repository.') from None
    return {'files':files,'instructions':INSTRUCTIONS,'version':manifest['version']}
