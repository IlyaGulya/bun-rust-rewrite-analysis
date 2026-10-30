#!/usr/bin/env python3
"""Check version extraction edge cases and conservation of stacked counts."""
import collections
import json
from pathlib import Path
from versions import bucket, reported_version
D=Path(__file__).resolve().parent/'data'

def check(title,body,want):
    got=reported_version(title,body)['version']
    assert got==want,(title,got,want)

check('elysia 1.4.7 fails','No Bun version stated','unknown')
check('Bun v1.3.14 crashes','', '1.3.14')
check('Bun v1.3.14 is different from old Bun 1.3.13','', 'multiple')
check('Bun 1.3.13 comparison','### What version of Bun is running?\n\n```\n1.4.0-canary.9+abc123\n```\n### What platform is your computer?\nWindows 11.0.0','1.4.0-canary')
check('Dependency 1.4.7','What version of Bun is running?\n1.3.14+ab123\nWhat steps can reproduce the bug?\nInstall elysia 1.4.7','1.3.14')
check('multiple builds','What version of Bun is running?\n1.3.14 and 1.4.0\nWhat platform is your computer?\nLinux','multiple')
check('no version','What version of Bun is running?\nlatest\nWhat platform is your computer?\nmacOS 15.4.1','unknown')
check('plugin version','What version of Bun is running?\nExtension: 0.0.31\nWhat platform is your computer?\nLinux','unknown')
check('kernel version','What version of Bun is running?\nLinux 6.8.0-136-generic\nWhat platform is your computer?\nLinux','unknown')
assert bucket({})=='unknown'
assert bucket({'crash':'crash'})=='crash'
assert bucket({'crash':'crash','hang':'hang'})=='multiple'
source=[json.loads(l) for l in (D/'classified.jsonl').read_text().splitlines()]
rows=[json.loads(l) for l in (D/'versions.jsonl').read_text().splitlines()]
payload=json.loads((D/'version-daily.json').read_text())
assert len(rows)==len({r['n'] for r in rows})==sum(r['bug'] for r in source)
by_id={r['n']:r for r in source}
expected=collections.defaultdict(collections.Counter)
for row in rows:
    r=by_id[row['n']]
    assert row['version']==reported_version(r['title'],r['excerpt'])['version']
    for axis in ['symptoms','components']:
        assert row[axis]==bucket(r[axis])
        expected[(row['version'],row['day'],axis)][row[axis]]+=1
assert dict(collections.Counter(r['version'] for r in rows))==payload['counts']
actual={(r['version'],r['day'],r['axis']):collections.Counter(r['counts']) for r in payload['daily']}
assert actual==expected
for axis in ['symptoms','components']:
    assert sum(sum(r['counts'].values()) for r in payload['daily'] if r['axis']==axis)==len(rows)
assert payload['days'][-1]=='2026-10-30'
print(f'Verified version-field precedence, dependency exclusions, ambiguous versions, canary grouping, and exact daily stacks for {len(rows)} reports.')
