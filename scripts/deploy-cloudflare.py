"""Deploy the approved public preview after Cloudflare bindings/network are configured."""
from pathlib import Path
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true', help='Check local prerequisites without contacting Cloudflare')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
project = 'br1anng-wishlist'
branch = 'codex-preview'
local_cli = root.parent / '.tools/cloudflare/node_modules/.bin/wrangler'
cli = str(local_cli) if local_cli.is_file() else shutil.which('wrangler')
missing = [name for name in ('CLOUDFLARE_ACCOUNT_ID', 'CLOUDFLARE_API_TOKEN') if not os.environ.get(name)]
if not cli:
    missing.append('Wrangler CLI')
if missing:
    print('Missing prerequisites: ' + ', '.join(missing), file=sys.stderr)
    print('Supply credentials securely in environment settings; never paste tokens in chat.', file=sys.stderr)
    raise SystemExit(2)
account = os.environ['CLOUDFLARE_ACCOUNT_ID']
if not re.fullmatch(r'[a-fA-F0-9]{32}', account):
    raise SystemExit('CLOUDFLARE_ACCOUNT_ID must be the 32-character account ID from the Cloudflare dashboard.')
if args.check:
    print('Local prerequisites present. Network access and Cloudflare authorization are not verified.')
    raise SystemExit(0)

subprocess.run([sys.executable, str(root / 'scripts/build-static.py')], check=True)
base = 'https://api.cloudflare.com/client/v4/accounts/' + urllib.parse.quote(account, safe='') + '/pages/projects'
headers = {'Authorization': 'Bearer ' + os.environ['CLOUDFLARE_API_TOKEN'], 'Content-Type': 'application/json'}

def api(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if not result.get('success'):
        codes = [str(item.get('code', 'unknown')) for item in result.get('errors', [])]
        raise SystemExit('Cloudflare API rejected the operation. Error codes: ' + ', '.join(codes))
    return result.get('result')

try:
    try:
        api(base + '/' + project)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        api(base, {'name': project, 'production_branch': 'main'})
except urllib.error.HTTPError as error:
    raise SystemExit('Cloudflare API access failed: HTTP ' + str(error.code) + '. Check network policy, account ID, and Pages Edit token scope.')
except urllib.error.URLError:
    raise SystemExit('Cloudflare API connection failed. Apply the saved environment network settings before retrying.')

environ = os.environ.copy()
environ['WRANGLER_SEND_METRICS'] = 'false'
environ['CI'] = 'true'
environ['WRANGLER_LOG_PATH'] = str(root.parent / '.tools/cloudflare/deploy.log')
subprocess.run([cli, 'pages', 'deploy', str(root / 'dist'), '--project-name', project,
                '--branch', branch, '--commit-dirty=true'], cwd=root, env=environ, check=True)
