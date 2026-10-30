#!/usr/bin/env python3
"""Reproducible, non-exclusive title-based issue taxonomy; never infers root cause."""
import collections
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'part3/data'
MERGE = dt.datetime.fromisoformat('2026-05-14T08:09:34+00:00')
STABLE = dt.datetime.fromisoformat('2026-08-20T14:07:21+00:00')
START = MERGE - dt.timedelta(weeks=26)
NONBUG = {'enhancement','docs','idea','question','chore','duplicate','invalid','wontfix'}
P = lambda s: dt.datetime.fromisoformat(s.replace('Z','+00:00'))

# Applied to titles only for the primary comparison. Bodies and triage labels
# have changed in length/coverage across periods; neither enters this taxonomy.
COMPONENTS = {
 'packages': ('Package manager', r'\bbun\s+(?:install|add|remove|update|pm|publish|link|unlink|outdated|patch)\b|\b(?:lockfile|bun\.lockb?|package manager|workspaces?|peer dependenc\w*|npm (?:install|registry)|registry auth)\b'),
 'build': ('Bundler / transpiler', r'\bbun\s+build\b|\b(?:bundl\w*|transpil\w*|sourcemaps?|source maps?|minif\w*|tree.shak\w*|standalone executable|single.file executable|--compile)\b'),
 'test': ('Test runner', r'\bbun(?:\s+|:)test\b|\b(?:test runner|mock\w*|jest|toEqual|toMatchObject|toThrow|expect\()'),
 'network': ('HTTP / network', r'\b(?:fetch|https?|http2|websockets?|TLS|SSL|DNS|TCP|UDP|proxy|Bun\.serve|Bun\.connect|Bun\.listen)\b|node:(?:http2?|https|tls|net|dns)'),
 'database': ('SQL / storage', r'\b(?:SQL|SQLite|MySQL|PostgreSQL|postgres|mariadb|redis|Bun\.SQL|Bun\.sqlite)\b|bun:sqlite'),
 'process': ('Processes / shell', r'\b(?:Bun\.spawn|Bun\.Shell|child_process|spawnSync|subprocess\w*|shell|SIGCHLD|process\.env|process\.exit|stdin|stdout|stderr)\b|\bbun run\b'),
 'filesystem': ('Filesystem / watch', r'\b(?:node:fs|fs\.\w+|Bun\.file|Bun\.write|readFile\w*|writeFile\w*|watch\w*|file system|filesystem|symlink\w*|readdir|fallocate)\b'),
 'modules': ('Modules / compatibility', r'\b(?:node:module|CommonJS|CJS|ESM|require\(|import\s|module resol\w*|node(?:\.js)? compat\w*)'),
 'native': ('Native / FFI / JSC', r'\b(?:FFI|NAPI|N-API|node.api|native addon\w*|JavaScriptCore|JSC|WebAssembly|WASM)\b'),
 'types': ('Types / TypeScript', r'\b(?:TypeScript|bun-types|typecheck\w*|type check\w*|type definitions?|\.d\.ts)\b'),
}
SYMPTOMS = {
 'crash': ('Crash / fatal signal', r'\b(?:crash\w*|segfault\w*|SIGSEGV|SIGABRT|SIGILL|segmentation fault|access violation|illegal instruction|bus error)\b'),
 'panic': ('Panic / assertion', r'\b(?:panic\w*|assertion fail\w*|assert\w* failed|unreachable)\b'),
 'hang': ('Hang / deadlock', r'\b(?:hang(?:s|ing)?|hung|deadlock\w*|freez\w*|frozen|infinite loop|stuck|never (?:exit\w*|finish\w*|resolv\w*))\b'),
 'memory': ('Memory use / leak', r'\b(?:memory leak\w*|memory usage|memory consumption|out.of.memory|OOM|heap corruption|use.after.free|double.free|buffer overflow)\b'),
 'performance': ('Performance', r'\b(?:slow\w*|performance|CPU (?:usage|spike)|high CPU|100% CPU|latency|throughput)\b'),
 'correctness': ('Wrong / missing result', r'\b(?:incorrect\w*|wrong|corrupt\w*|truncat\w*|mismatch\w*|missing|ignored|ignores|silently|unexpected\w*|misread\w*|drops?|deletes?|pads?)\b'),
 'failure': ('Explicit failure', r"\b(?:fails?|failure|cannot|can't|unable|does(?:n.t| not) work|not working|error)\b"),
}

def classify(title, rules):
    return {key: m.group(0) for key, (_, regex) in rules.items() if (m := re.search(regex, title, re.I))}


def main():
    now = P(json.loads((ROOT/'part2/data/snapshot.json').read_text())['generated'])
    old_bodies = {r['n']:r['b'] for line in (ROOT/'data/bodies.jsonl').read_text().splitlines() if (r:=json.loads(line))}
    source = {}
    for line in (ROOT/'data/issues.jsonl').read_text().splitlines():
        r=json.loads(line)
        if START <= P(r['createdAt']) < MERGE:
            source[r['number']] = dict(n=r['number'], created=r['createdAt'], title=r['title'],
                labels=[l['name'] for l in r['labels']['nodes']], fixed=r['state']=='CLOSED' and r['stateReason']=='COMPLETED',
                closed=r['closedAt'], body=old_bodies.get(r['number'],''), text_snapshot='2026-08-10')
    raw_path=ROOT/'part2/data/raw.json'
    raw={r['number']:r for r in json.loads(raw_path.read_text())} if raw_path.exists() else {}
    # Committed audit rows retain the bounded excerpts needed for offline rebuilds.
    cache=DATA/'classified.jsonl'
    cached={r['n']:r for line in cache.read_text().splitlines() if (r:=json.loads(line))} if cache.exists() else {}
    for line in (ROOT/'part2/data/issues.jsonl').read_text().splitlines():
        r=json.loads(line);r['body']=raw.get(r['n'],{}).get('body') or cached.get(r['n'],{}).get('excerpt','')
        r['text_snapshot']=now.date().isoformat();source[r['n']]=r
    rows=[]
    for r in sorted(source.values(),key=lambda r:r['created']):
        created=P(r['created'])
        if not START <= created < now:continue
        title=r['title']; excerpt=(r.get('body') or '')[:2500]
        clean=re.sub(r'```[\s\S]*?(?:```|$)', '', excerpt)
        clean=re.sub(r'(?im)^.*(?:what version of bun|what platform|what steps|expected behavior|what do you see|additional information|no response).*$','',clean)
        comp=classify(title,COMPONENTS);sym=classify(title,SYMPTOMS)
        rows.append(dict(n=r['n'],created=r['created'],title=title,excerpt=excerpt,labels=r['labels'],
            fixed=r['fixed'],closed=r.get('closed'),text_snapshot=r['text_snapshot'],
            bug=not bool(set(r['labels'])&NONBUG),period='pre' if created<MERGE else 'pre_stable' if created<STABLE else 'stable',
            components=comp,symptoms=sym,
            expanded_components=classify(title+'\n'+clean,COMPONENTS),expanded_symptoms=classify(title+'\n'+clean,SYMPTOMS)))
    DATA.mkdir(exist_ok=True)
    cache.write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows))
    periods={}
    for period,a,b in [('pre',START,MERGE),('pre_stable',MERGE,STABLE),('stable',STABLE,now),('post',MERGE,now)]:
        group=[r for r in rows if r['bug'] and a<=P(r['created'])<b]
        stats={}
        for axis,rules in [('components',COMPONENTS),('symptoms',SYMPTOMS)]:
            counts=collections.Counter(k for r in group for k in r[axis]);expanded=collections.Counter(k for r in group for k in r['expanded_'+axis])
            stats[axis]={k:dict(label=label,n=counts[k],share=round(100*counts[k]/len(group),2),per_week=round(counts[k]/((b-a).total_seconds()/604800),2),expanded_n=expanded[k]) for k,(label,_) in rules.items()}
            stats[axis]['unclassified']=dict(label='No title signal',n=sum(not r[axis] for r in group),share=round(100*sum(not r[axis] for r in group)/len(group),2))
        periods[period]=dict(n=len(group),weeks=(b-a).total_seconds()/604800,**stats)
    # Thursday calendar buckets align exactly with daily npm data; first/last
    # partial buckets remain visible and are excluded from download ratios.
    weekly=[]; day=START.date(); end=now.date()
    while day<=end:
        stop=day+dt.timedelta(days=7)
        group=[r for r in rows if day.isoformat()<=r['created'][:10]<stop.isoformat()]
        bugs=[r for r in group if r['bug']]
        weekly.append(dict(start=day.isoformat(),end=stop.isoformat(),partial=day==START.date() or stop>now.date(),issues=len(group),bugs=len(bugs),fixed=sum(r['fixed'] for r in bugs),
            **{'s_'+k:sum(k in r['symptoms'] for r in bugs) for k in SYMPTOMS}))
        day=stop
    payload=dict(generated=now.isoformat(),start=START.isoformat(),merge=MERGE.isoformat(),stable=STABLE.isoformat(),
        taxonomy_version=1,primary='title-only, multi-label; rule matches are signals, not validated root causes',periods=periods,weekly=weekly,
        rules={'components':{k:dict(label=v[0],regex=v[1]) for k,v in COMPONENTS.items()},'symptoms':{k:dict(label=v[0],regex=v[1]) for k,v in SYMPTOMS.items()}})
    (DATA/'classification.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    print({p:d['n'] for p,d in periods.items()})

if __name__=='__main__':main()
