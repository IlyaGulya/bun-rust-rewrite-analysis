#!/usr/bin/env python3
"""Check the published snapshot independently of update.py; no network needed."""
import collections
import datetime as dt
import json
from pathlib import Path

root = Path(__file__).resolve().parent
rows = [json.loads(line) for line in (root / 'data/issues.jsonl').read_text().splitlines()]
s = json.loads((root / 'data/series.js').read_text().removeprefix('const S = ').strip().removesuffix(';'))
p = lambda value: dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
now, merge, stable = map(p, [s['generated'], s['merge'], s['release140']])
assert len(rows) == len({r['n'] for r in rows})
assert all(merge <= p(r['created']) < now for r in rows)
assert all(not r['closed'] or p(r['created']) <= p(r['closed']) <= now for r in rows)
assert s['generated'] == json.loads((root / 'data/snapshot.json').read_text())['generated']
totals = s['totals']
assert len(rows) == totals['since_merge'] == sum(d['all'] for d in s['daily'])
assert sum(r['bug'] for r in rows) == totals['bugs_since_merge']
assert sum(not r['closed'] for r in rows) == totals['open_now'] == s['backlog'][-1]['open']
since = [r for r in rows if p(r['created']) >= stable]
assert len(since) == totals['since_140']
assert sum(bool({'crash', 'hang'} & set(r['kw'])) for r in since) == totals['crash_or_hang_since_140']
for key in s['keywordNames']:
    assert sum(key in r['kw'] for r in since) == totals['kw_since_140'][key]
groups = {'post': rows, 'post_pre140': [r for r in rows if p(r['created']) < stable], 'post_140': since}
for key, group in groups.items():
    bugs = [r for r in group if r['bug']]
    mature = [r for r in bugs if (now - p(r['created'])).total_seconds() >= 30 * 86400]
    fixed30 = sum(r['fixed'] and r['closed'] is not None and
                  0 <= (p(r['closed']) - p(r['created'])).total_seconds() <= 30 * 86400 for r in mature)
    c = s['cohorts'][key]
    assert (len(bugs), sum(r['fixed'] for r in bugs), len(mature), fixed30) == (c['n'], c['fixed'], c['mature30'], c['fixed30'])
    assert c['rate30'] == (round(100 * fixed30 / len(mature), 1) if mature else None)
assert len(s['releases']) == len({tag for _, tag in s['releases']})
page = (root.parent / 'index.html').read_text()
assert page.count('<!-- part2:start -->') == page.count('<!-- part2:end -->') == 1
assert 'const P2 = ' + json.dumps(s, separators=(',', ':')) + ';' in page
assert '__DATA__' not in page
print(f"Snapshot verified: {len(rows)} issues, cohort outcomes, 30-day follow-up, keywords, backlog, releases and embedded payload.")
