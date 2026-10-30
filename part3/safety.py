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
    groups={'pre':[d for d in dates if d<c['merge'][:10]],'canary':[d for d in dates if c['merge'][:10]<d<c['stable'][:10]],'stable':[d for d in dates if d>c['stable'][:10]]}
    stats={}
    for variant in daily:
        stats[variant]={}
        for key in ['all','crash','leak','memory']:
            values={}
            for period,days in groups.items():
                count=sum(daily[variant][d][key] for d in days);downloads=sum(dl[d] for d in days)
                values[period]={'n':count,'downloads':downloads,'days':len(days),'rate':count/downloads*1e6 if downloads else None}
            values['stable_vs_canary_pct']=(values['stable']['rate']/values['canary']['rate']-1)*100 if values['canary']['rate'] else None
            stats[variant][key]=values
    payload={'generated':c['generated'],'merge':c['merge'][:10],'stable':c['stable'][:10],
        'phase_order':['pre','canary','stable'],
        'phases':{'pre':{'label':'Before merge','start':min(groups['pre']),'end':max(groups['pre'])},'canary':{'label':'Canary period: Zig stable + Rust canary','start':min(groups['canary']),'end':max(groups['canary'])},'stable':{'label':'After Rust stable','start':min(groups['stable']),'end':max(groups['stable'])}},
        'first_partial':first,'last_partial':last,'download_through':pop['npm']['valid_through'],
        'labels':{'all':'All possible bug reports','crash':'Crash reports','leak':'Memory leak reports','memory':'Memory keyword reports'},
        'daily':{v:{d:dict(x) for d,x in sorted(ds.items())} for v,ds in daily.items()},'stats':stats,
        'leak_examples':[r for r in rows if r['flags']['title']['leak'] and r['day'] in dates and r['day'] not in {c['merge'][:10],c['stable'][:10]}],
        'leak_rule':LEAK.pattern,'method':'Three calendar periods are separate from reported version families. Merge and stable-release days are excluded from phase summaries. Title matches do not confirm defects. All versions and installation channels are included. No causal Rust effect is measured.'}
    (D/'safety.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    (D/'safety-audit.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows))
    for variant,metrics in stats.items():
        print(variant,{key:{phase:(value[phase]['n'],round(value[phase]['rate'],3)) for phase in ['pre','canary','stable']} for key,value in metrics.items()})
if __name__=='__main__':main()
