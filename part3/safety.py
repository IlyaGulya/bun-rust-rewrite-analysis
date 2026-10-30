#!/usr/bin/env python3
"""Compare report signals per npm request; no inference of confirmed defects."""
import collections
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'part3/data'
# Explicit allocated-memory context: excludes generic memory usage / OOM alone.
LEAK=re.compile(r'\bmemory\s+leak\w*\b|\bleak(?:s|ing|ed)?\b.{0,140}(?:\bmemory\b|\bRSS\b|\bheap\b|\bbytes\b|\b[KMGT]Bs?\b|GC root|Exception root|RefData|LSAN)|(?:\bmemory\b|\bRSS\b|\bheap\b).{0,100}\bleak(?:s|ing|ed)?\b|\bretain\w*\b.{0,100}(?:off.heap|heap|RSS).{0,80}unbounded|\b(?:RSS|memory|heap)\b.{0,80}\bnot (?:released|freed|reclaimed)\b.{0,100}(?:unbounded|grows)',re.I)
# A test's memory cap failing and disk-space leaks are not RAM-leak reports.
TEST_CAP=re.compile(r'leak[\w.-]*\.test\..*(?:headroom|cap|flak)',re.I)
DISK=re.compile(r'temp director|TMPDIR|temp files|directory fd|file descriptor',re.I)
RAM=re.compile(r'\bmemory\b|\bRSS\b|\bheap\b|GC root|LSAN',re.I)

def leak_signal(text):
    if TEST_CAP.search(text) or (DISK.search(text) and not RAM.search(text)):return False
    return bool(LEAK.search(text))

def clean_body(body):
    return re.sub(r'```[\s\S]*?(?:```|$)','',body[:2500])

def main():
    c=json.loads((D/'classification.json').read_text());pop=json.loads((D/'popularity.json').read_text())
    crash=re.compile(c['rules']['symptoms']['crash']['regex'],re.I)
    memory=re.compile(c['rules']['symptoms']['memory']['regex'],re.I)
    dl={r['day']:r['downloads'] for r in pop['npm']['daily']}
    rows=[];daily={k:collections.defaultdict(collections.Counter) for k in ['title','expanded']}
    for line in (D/'classified.jsonl').read_text().splitlines():
        r=json.loads(line)
        if not r['bug']:continue
        entry={'n':r['n'],'day':r['created'][:10],'title':r['title'],'flags':{}}
        for variant,text in [('title',r['title']),('expanded',r['title']+'\n'+clean_body(r['excerpt']))]:
            flags={'all':True,'crash':bool(crash.search(text)),'leak':leak_signal(text),'memory':bool(memory.search(text))}
            entry['flags'][variant]=flags
            for key,flag in flags.items():daily[variant][entry['day']][key]+=flag
        rows.append(entry)
    first,last=c['start'][:10],c['generated'][:10]
    dates=sorted(d for d in dl if first<d<last and d<=pop['npm']['valid_through'])
    groups={'pre':[d for d in dates if d<c['merge'][:10]],'post':[d for d in dates if d>c['merge'][:10]],'stable':[d for d in dates if d>c['stable'][:10]]}
    stats={}
    for variant in daily:
        stats[variant]={}
        for key in ['all','crash','leak','memory']:
            values={}
            for period,days in groups.items():
                count=sum(daily[variant][d][key] for d in days);downloads=sum(dl[d] for d in days)
                values[period]={'n':count,'downloads':downloads,'days':len(days),'rate':count/downloads*1e6 if downloads else None}
            a,b=values['pre']['rate'],values['post']['rate']
            values['change_pct']=(b/a-1)*100 if a else None
            stats[variant][key]=values
    payload={'generated':c['generated'],'merge':c['merge'][:10],'stable':c['stable'][:10],
        'first_partial':first,'last_partial':last,'download_through':pop['npm']['valid_through'],
        'labels':{'all':'All possible bug reports','crash':'Crash reports','leak':'Memory leak reports','memory':'All memory problem reports'},
        'daily':{v:{d:dict(x) for d,x in sorted(ds.items())} for v,ds in daily.items()},'stats':stats,
        'leak_examples':[r for r in rows if r['flags']['title']['leak'] and r['day'] in dates and r['day']!=c['merge'][:10]],
        'leak_rule':LEAK.pattern,'method':'Title signals are primary; title plus bounded body is sensitivity only. Categories overlap. All builds and channels; not confirmed defects or user risk.'}
    (D/'safety.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    (D/'safety-audit.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows))
    for variant,metrics in stats.items():
        print(variant,{k:(v['pre']['n'],round(v['pre']['rate'],3),v['post']['n'],round(v['post']['rate'],3),round(v['change_pct'],1) if v['change_pct'] is not None else None) for k,v in metrics.items()})
if __name__=='__main__':main()
