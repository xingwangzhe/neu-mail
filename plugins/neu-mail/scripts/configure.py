#!/usr/bin/env python3
"""Enter credentials locally using a hidden terminal prompt."""
import argparse,getpass,json,os
parser=argparse.ArgumentParser()
parser.add_argument('--allow-hostname-mismatch', action='store_true', help='Skip hostname matching only; keep CA chain and expiry verification')
args=parser.parse_args()
from pathlib import Path
p=Path(os.environ.get('NEU_MAIL_CONFIG','~/.config/neu-mail/account.json')).expanduser()
host=input('IMAP hostname: ').strip()
username=input('Full email address: ').strip()
password=getpass.getpass('Client-specific password (hidden): ')
if not host or not username or not password: raise SystemExit('All fields required')
p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
os.fchmod(fd,0o600)
with os.fdopen(fd,'w') as f: json.dump({'host':host,'port':993,'username':username,'password':password,'allow_hostname_mismatch':args.allow_hostname_mismatch},f)
print('Saved local account configuration with permissions 0600. No credentials included in plugin.')
