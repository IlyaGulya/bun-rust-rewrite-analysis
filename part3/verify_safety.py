#!/usr/bin/env python3
"""Leak-classification edge cases and independent paired-exposure checks."""
import collections
import json
from pathlib import Path
from safety import leak_signal
D=Path(__file__).resolve().parent/'data'
for text in ['Memory leak','Bun.build leaks native memory per call','Every React commit leaks ~21 KB of native memory','Async node:fs ops leak a GC root per call','request retains the response body off-heap — RSS grows unbounded','worker RSS is not released between files; unbounded growth OOM']:
    assert leak_signal(text),text
for text in ['High memory usage','Out of memory when allocating a large array','heap-use-after-free','bun install leaks temp directories in TMPDIR; filled 25 GB','serve-body-leak.test.ts absolute 512MB end-memory cap has no headroom; flakes','leaks one directory fd per reload','lexical scope leakage']:
    assert not leak_signal(text),text
s=json.loads((D/'safety.json').read_text());p=json.loads((D/'popularity.json').read_text())
rows=[json.loads(l) for l in (D/'safety-audit.jsonl').read_text().splitlines()]
assert len(rows)==len({r['n'] for r in rows})
assert all(isinstance(r['title'],str) for r in rows)
byday={v:collections.defaultdict(collections.Counter) for v in ['title','expanded']}
for r in rows:
    assert r['flags']['title']['leak']==leak_signal(r['title'])
    for v in byday:
        assert r['flags'][v]['all']
        for k,x in r['flags'][v].items():byday[v][r['day']][k]+=x
for v in byday:assert {d:dict(x) for d,x in byday[v].items()}==s['daily'][v]
dl={r['day']:r['downloads'] for r in p['npm']['daily']}
valid={d for d in dl if s['first_partial']<d<s['last_partial'] and d<=s['download_through']}
for v in ['title','expanded']:
    for key,stats in s['stats'][v].items():
        for phase,test in [('pre',lambda d:d<s['merge']),('canary',lambda d:s['merge']<d<s['stable']),('stable',lambda d:d>s['stable'])]:
            days={d for d in valid if test(d)};count=sum(r['flags'][v][key] for r in rows if r['day'] in days);den=sum(dl[d] for d in days)
            x=stats[phase];assert (x['n'],x['downloads'],x['days'])==(count,den,len(days))
            assert abs(x['rate']-count*1e6/den)<1e-9
assert len(s['leak_examples'])==sum(s['stats']['title']['leak'][k]['n'] for k in s['phase_order'])
assert [s['stats']['title']['all'][k]['days'] for k in s['phase_order']]==[181,97,69]
for variant in s['stats'].values():
    for metrics in variant.values():
        expected=(metrics['stable']['rate']/metrics['canary']['rate']-1)*100 if metrics['canary']['rate'] else None
        assert metrics['stable_vs_canary_pct']==expected
assert s['stats']['title']['all']['stable']['rate']>s['stats']['title']['all']['canary']['rate']
page=(D.parent.parent/'index.html').read_text()
assert 'id="p3-safety-rate-chart"' in page and 'id="p3-growth-ratio-chart"' in page and '__SAFETY_DATA__' not in page
print('Safety analysis verified: explicit memory retention versus OOM/disk/fd signals, audit counts, complete-day denominators, rate changes and both plots.')
