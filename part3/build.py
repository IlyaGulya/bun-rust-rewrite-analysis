#!/usr/bin/env python3
"""Build the current report first, preserving the frozen original as an appendix."""
import datetime as dt
import json
from pathlib import Path
from versions import main as build_versions
from safety import main as build_safety
ROOT=Path(__file__).resolve().parents[1]
def main():
    build_versions()
    build_safety()
    data=ROOT/'part3/data';page=ROOT/'index.html'
    classification=json.loads((data/'classification.json').read_text())
    popularity=json.loads((data/'popularity.json').read_text())
    daily={r['day']:r['downloads'] for r in popularity['npm']['daily']}
    joined=[]
    for w in classification['weekly']:
        days=[(dt.date.fromisoformat(w['start'])+dt.timedelta(days=i)).isoformat() for i in range(7)]
        valid=not w['partial'] and all(d in daily and d<=popularity['npm']['valid_through'] for d in days)
        downloads=sum(daily[d] for d in days) if valid else None
        joined.append({**w,'npm_downloads':downloads,'reports_per_million':round(w['bugs']/downloads*1e6,2) if downloads else None})
    periods={}
    for key,start,end in [('pre',classification['start'][:10],classification['merge'][:10]),('post',classification['merge'][:10],classification['generated'][:10]),('stable',classification['stable'][:10],classification['generated'][:10])]:
        weeks=[w for w in joined if w['npm_downloads'] is not None and start<=w['start'] and w['end']<=end]
        bugs=sum(w['bugs'] for w in weeks); downloads=sum(w['npm_downloads'] for w in weeks)
        periods[key]={'weeks':len(weeks),'reports':bugs,'downloads':downloads,'reports_per_million':round(bugs/downloads*1e6,2) if downloads else None}
    exposure={'weekly':joined,'periods':periods,'valid_through':popularity['npm']['valid_through']}
    (data/'exposure.json').write_text(json.dumps(exposure,indent=2)+'\n')
    block=(ROOT/'part3/block.html').read_text().replace('__EXPOSURE_DATA__',json.dumps(exposure,separators=(',',':')))

    for marker,file in [('__P3_DATA__','classification.json'),('__POPULARITY_DATA__','popularity.json'),('__VERSION_DAILY_DATA__','version-daily.json'),('__SAFETY_DATA__','safety.json'),('__FAMILY_DATA__','family-matrix.json')]:
        block=block.replace(marker,json.dumps(json.loads((data/file).read_text()),ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
    block=block.replace('__COMBINED_JS__',(ROOT/'part3/combined-series.js').read_text())
    audit=[{k:r[k] for k in ['n','title','period','components','symptoms']} for line in (data/'classified.jsonl').read_text().splitlines() if (r:=json.loads(line))['bug']]
    block=block.replace('__AUDIT_DATA__',json.dumps(audit,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c'))
    start,end='<!-- part3:start -->','<!-- part3:end -->'
    section=start+'\n'+block+'\n'+end
    text=page.read_text()
    if start in text:
        a,tail=text.split(start,1);text=a+section+tail.split(end,1)[1]
    else:
        p2start,p2end='<!-- part2:start -->','<!-- part2:end -->'
        head,tail=text.split(p2start,1);p2,rest=tail.split(p2end,1);text=head+rest
        notice='<p style="max-width:1100px;margin:20px auto;padding:0 24px">'
        if notice in text:
            a,b=text.split(notice,1);text=a+b.split('</p>',1)[1]
        text=text.replace('<header class="rec">',section+'\n'+p2start+p2+p2end+'\n<details id="historical-analysis"><summary>Historical analysis · frozen 10 August 2026</summary><div class="p3-history">\n<header class="rec">',1)
        text=text.replace('<footer>','</div></details>\n<footer>',1)
        text=text.replace('Built from the GitHub API on 2026-08-10','Historical appendix built from the GitHub API on 2026-08-10',1)
    text=text.replace('<title>One PR, a million lines of Rust — what it did to Bun\'s bug reports</title>','<title>Bun rewrite analysis · updated 30 October 2026</title>')
    page.write_text(text)
    print('Built current classification, adoption and full-window charts ahead of historical appendix.')
if __name__=='__main__':main()
