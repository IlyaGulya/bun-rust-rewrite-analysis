#!/usr/bin/env python3
"""Independent checks on comparison cohorts and download joins; offline."""
import collections
import datetime as dt
import json
import re
from pathlib import Path
D=Path(__file__).resolve().parent/'data'
load=lambda name:json.loads((D/name).read_text())
p=lambda s:dt.datetime.fromisoformat(s.replace('Z','+00:00'))
c=load('classification.json');pop=load('popularity.json');e=load('exposure.json')
rows=[json.loads(l) for l in (D/'classified.jsonl').read_text().splitlines()]
assert len(rows)==len({r['n'] for r in rows})
assert all(len(r['excerpt'])<=2500 for r in rows)
limits={'pre':(c['start'],c['merge']),'pre_stable':(c['merge'],c['stable']),'stable':(c['stable'],c['generated']),'post':(c['merge'],c['generated'])}
for key,(a,b) in limits.items():
    group=[r for r in rows if r['bug'] and p(a)<=p(r['created'])<p(b)]
    assert len(group)==c['periods'][key]['n']
    for axis in ['components','symptoms']:
        count=collections.Counter()
        for r in group:
            expected={k:match.group(0) for k,rule in c['rules'][axis].items() if (match:=re.search(rule['regex'],r['title'],re.I))}
            assert expected==r[axis]
            count.update(expected.keys())
        for k in c['rules'][axis]:assert count[k]==c['periods'][key][axis][k]['n']
        assert sum(not r[axis] for r in group)==c['periods'][key][axis]['unclassified']['n']
assert c['periods']['pre']['n']==1802 and c['periods']['post']['n']==2389
assert sum(w['bugs'] for w in c['weekly'])==sum(r['bug'] for r in rows)
assert c['weekly'][-1]['start']=='2026-10-29' and c['weekly'][-1]['partial']
assert c['weekly'][0]['partial']
daily={d['day']:d['downloads'] for d in pop['npm']['daily']}
assert len(daily)==len(pop['npm']['daily']) and max(daily)==pop['npm']['valid_through']
assert all(isinstance(v,int) and v>=0 for v in daily.values())
for w in e['weekly']:
    ds=[(dt.date.fromisoformat(w['start'])+dt.timedelta(days=i)).isoformat() for i in range(7)]
    valid=not w['partial'] and all(d in daily and d<=pop['npm']['valid_through'] for d in ds)
    if valid:
        total=sum(daily[d] for d in ds)
        assert w['npm_downloads']==total
        assert w['reports_per_million']==(round(w['bugs']*1e6/total,2) if total else None)
    else:assert w['npm_downloads'] is None and w['reports_per_million'] is None
for r in pop['github']['stars_weekly']:assert len(r['days'])==7 and sum(r['days'])==r['total']
page=(D.parent.parent/'index.html').read_text()
assert page.index('id="current-analysis"')<page.index('id="historical-analysis"')
assert page.count('<!-- part3:start -->')==page.count('<!-- part3:end -->')==1
assert '__P3_DATA__' not in page and '__POPULARITY_DATA__' not in page
assert '2026-10-29' in page and '2026-10-30' in page
print('Verified title signals, cohorts, counts, final partial week, published npm dates, weekly joins, star totals and current-first HTML.')
