#!/usr/bin/env python3
"""Extract reported Bun versions, and export daily exclusive type stacks."""
import collections
import datetime as dt
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'part3/data'
# Even the Bun template field can contain an editor/plugin/kernel version.
# Validate base versions against the saved official release history.
KNOWN_BASES={line.split('\t')[1].removeprefix('bun-v') for line in (ROOT/'data/releases.tsv').read_text().splitlines()}
KNOWN_BASES.update(tag for _,tag in json.loads((ROOT/'part2/data/releases.json').read_text()))
def plausible(version):
    return version.split('-')[0] in KNOWN_BASES

VERSION=re.compile(r'(?<![\w.])v?(\d+\.\d+\.\d+)(?:[-.]?(canary|debug|dev)(?:[.\w+-]*))?(?:\+[\w.-]+)?',re.I)
PROMPT=re.compile(r'(?im)^\s*(?:#{1,6}\s*)?What version of Bun (?:is running|are you using)\??[^\n]*\n')
NEXT=re.compile(r'(?im)^\s*(?:#{1,6}\s*[^\n]+|What (?:platform|steps|is the expected|do you see)|Additional information)')
EXPLICIT=re.compile(r'\bbun(?:\s+version)?\s*[:=]?\s*v?\d+\.\d+\.\d+(?:[-.](?:canary|debug|dev)[\w.+-]*)?(?:\+[\w.-]+)?',re.I)

def normalize(match):
    return match.group(1)+(('-'+match.group(2).lower()) if match.group(2) else '')

def reported_version(title,body):
    prompt=PROMPT.search(body)
    if prompt:
        section=body[prompt.end():];end=NEXT.search(section)
        if end:section=section[:end.start()]
        # A template version field is stronger evidence than a title comparison.
        matches=list(VERSION.finditer(section[:1000]))
        all_candidates=sorted({normalize(m) for m in matches})
        candidates=[v for v in all_candidates if plausible(v)]
        rejected=[v for v in all_candidates if not plausible(v)]
        if all_candidates:
            return dict(version=candidates[0] if len(candidates)==1 else 'multiple' if candidates else 'unknown',candidates=candidates,rejected_candidates=rejected,
                        source='version field',evidence=section.strip()[:180])
    # Only explicitly adjacent Bun version strings; never bare dependency tokens.
    contexts=EXPLICIT.findall(title+'\n'+body[:700])
    all_candidates=sorted({normalize(m) for text in contexts for m in VERSION.finditer(text)})
    candidates=[v for v in all_candidates if plausible(v)]
    return dict(version=candidates[0] if len(candidates)==1 else 'multiple' if candidates else 'unknown',
                candidates=candidates,rejected_candidates=[v for v in all_candidates if not plausible(v)],source='explicit Bun version' if candidates else 'not stated',evidence='; '.join(contexts)[:180])

def bucket(signals):
    return next(iter(signals)) if len(signals)==1 else 'multiple' if signals else 'unknown'

def main():
    classification=json.loads((DATA/'classification.json').read_text())
    rows=[]
    for line in (DATA/'classified.jsonl').read_text().splitlines():
        r=json.loads(line)
        if not r['bug']:continue
        version=reported_version(r['title'],r['excerpt'])
        rows.append(dict(n=r['n'],day=r['created'][:10],title=r['title'],**version,
                         symptoms=bucket(r['symptoms']),components=bucket(r['components'])))
    (DATA/'versions.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows))
    dates=[];day=dt.date.fromisoformat(classification['start'][:10]);end=dt.date.fromisoformat(classification['generated'][:10])
    while day<=end:dates.append(day.isoformat());day+=dt.timedelta(days=1)
    counts=collections.Counter(r['version'] for r in rows)
    types={axis:{k:v['label'] for k,v in classification['rules'][axis].items()}|{'multiple':'Multiple type signals','unknown':'No title signal'} for axis in ['symptoms','components']}
    daily=collections.defaultdict(collections.Counter)
    for r in rows:
        for axis in types:daily[(r['version'],r['day'],axis)][r[axis]]+=1
    payload=dict(generated=classification['generated'],days=dates,types=types,counts=dict(counts),
                 top_versions=[v for v,_ in counts.most_common() if v not in {'unknown','multiple'}][:4],
                 daily=[dict(version=v,day=d,axis=axis,counts=dict(c)) for (v,d,axis),c in sorted(daily.items())])
    (DATA/'version-daily.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
    print('Reported versions:',counts.most_common(12))
if __name__=='__main__':main()
