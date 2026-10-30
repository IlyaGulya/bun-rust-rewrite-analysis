#!/usr/bin/env python3
"""Render GitHub-readable PNG figures from committed report inputs.

Requires matplotlib (see requirements-readme.txt) and Node.js. Calculation of
rolling/indexed series is delegated to the same JS module used in the HTML.
"""
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/readme';OUT.mkdir(parents=True,exist_ok=True)
D=ROOT/'part3/data'
load=lambda p:json.loads(p.read_text())
c=load(D/'classification.json');v=load(D/'version-daily.json');safe=load(D/'safety.json')
p2=json.loads((ROOT/'part2/data/series.js').read_text()[10:-2])
node=r"""
const fs=require('fs'),{build}=require('./part3/combined-series.js');
const v=JSON.parse(fs.readFileSync('part3/data/version-daily.json')),p=JSON.parse(fs.readFileSync('part3/data/popularity.json')),s=JSON.parse(fs.readFileSync('part3/data/safety.json'));
const counts={};for(const r of v.daily){if(r.axis!=='symptoms')continue;counts[r.day]||={};for(const [k,n]of Object.entries(r.counts))counts[r.day][k]=(counts[r.day][k]||0)+n;}
const args={days:v.days,counts,types:Object.keys(v.types.symptoms),downloads:Object.fromEntries(p.npm.daily.map(r=>[r.day,r.downloads])),firstPartial:v.days[0],lastPartial:v.days.at(-1),merge:s.merge,stable:s.stable};
console.log(JSON.stringify({indexed:build({...args,windowDays:7,mode:'index'}),ratio7:build({...args,windowDays:7,mode:'rate'}).growthRatio,ratio28:build({...args,windowDays:28,mode:'rate'}).growthRatio}));
"""
series=json.loads(subprocess.check_output(['node','-e',node],cwd=ROOT,text=True))
PAPER='#141b23';INK='#dde5ec';MUTED='#a3afbc';GRID='#303c48';PRE='#8c92e8';POST='#e47839';CYAN='#30b1d2'
COLORS={'crash':'#4f86c6','panic':'#de7344','hang':'#32a89a','memory':'#b184d6','performance':'#c9a53c','correctness':'#d576a3','failure':'#6ea343','unknown':'#657585','multiple':'#8895a3'}
SHORT={'crash':'Crash or fatal signal','panic':'Panic or failed check','hang':'Hang or deadlock','memory':'Memory problems','performance':'Performance','correctness':'Wrong or missing result','failure':'Reported error','unknown':'No title match','multiple':'Several type matches'}
plt.rcParams.update({'figure.facecolor':PAPER,'axes.facecolor':PAPER,'savefig.facecolor':PAPER,'text.color':INK,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,'font.family':'DejaVu Sans','font.size':10.5,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'axes.axisbelow':True,'axes.grid':True,'grid.color':GRID,'grid.alpha':.75,'grid.linewidth':.65,'legend.frameon':False,'legend.labelcolor':INK,'svg.fonttype':'none'})
parse=lambda d:dt.datetime.fromisoformat(d.replace('Z','+00:00')).replace(tzinfo=None)
dates=[parse(d) for d in v['days']]
PHASES=['pre','canary','stable']
PHASE_NAMES=['Before merge','Canary period','After Rust stable']
PHASE_COLORS=[PRE,MUTED,POST]
def clean(ax):
    ax.grid(axis='x',visible=False);ax.tick_params(length=0,pad=8)
def timeline(ax):
    clean(ax);ax.set_xlim(dates[0],dates[-1]+dt.timedelta(days=1))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
def events(ax,labels=True):
    ax.axvspan(parse(safe['merge']),parse(safe['stable']),color=MUTED,alpha=.08,zorder=0)
    for date,label in [(safe['merge'],'Rewrite merged · 14 May'),(safe['stable'],'1.4.0 stable · 20 Aug')]:
        x=parse(date);ax.axvline(x,color=CYAN,alpha=.6,ls='--',lw=1)
        if labels:ax.text(x+dt.timedelta(days=2),.96,label,transform=ax.get_xaxis_transform(),rotation=90,va='top',ha='left',fontsize=9,color=INK,bbox={'facecolor':PAPER,'edgecolor':'none','pad':1})
def header(fig,title,subtitle):
    fig.text(.065,.97,title,ha='left',va='top',fontsize=16,fontweight='bold')
    fig.text(.065,.907,subtitle,ha='left',va='top',fontsize=10.2,color=MUTED)
def save(fig,name,foot):
    fig.text(.065,.035,foot,ha='left',va='bottom',fontsize=9,color=MUTED,linespacing=1.5)
    fig.savefig(OUT/(name+'.png'),dpi=160);plt.close(fig)
def arr(xs):return np.array([np.nan if x is None else x for x in xs],dtype=float)

# 1. Exclusive signal stacks and npm growth use their own common pre-period bases.
fig,ax=plt.subplots(figsize=(12,6.6));fig.subplots_adjust(left=.085,right=.96,bottom=.18,top=.73)
header(fig,'Reports and npm requests across three release periods','Daily data through 30 October 2026 · previous 7 days · before-merge daily mean = 100')
keys=['unknown','multiple','crash','panic','hang','memory','performance','correctness','failure'];bottom=np.zeros(len(dates));handles=[]
for key in keys:
    y=arr(series['indexed']['reportSeries'][key]);ax.bar(dates,np.nan_to_num(y),bottom=bottom,width=.96,color=COLORS[key],linewidth=0)
    bottom+=np.nan_to_num(y);handles.append(Patch(color=COLORS[key],label=SHORT[key]))
line=ax.plot(dates,arr(series['indexed']['downloadSeries']),color=INK,lw=2.4,label='npm request growth')[0]
fig.legend([line]+handles,[line.get_label()]+[x.get_label() for x in handles],loc='upper left',bbox_to_anchor=(.06,.858),ncol=5,fontsize=9,columnspacing=1.3,handlelength=1.3)
ax.axhline(100,color=MUTED,lw=.8,ls=':');ax.set_ylabel('Growth index · before merge = 100');timeline(ax);events(ax)
save(fig,'01-growth-and-reports','Each report enters one stack group. npm data ends 28 Oct; rates and growth indices stop there.\nShaded dates: Zig stable + Rust canary. npm requests cover all versions and do not count users or a Rust effect.')

# 2. Three disjoint date groups; neither group is a language cohort.
fig,axs=plt.subplots(1,2,figsize=(12,5.5));fig.subplots_adjust(left=.15,right=.96,bottom=.25,top=.70,wspace=.50)
header(fig,'Crash and memory leak reports in three date periods','Reports per million all-version npm requests · date periods do not identify language use')
for ax,key,title in zip(axs,['crash','leak'],['Crash or fatal signal','Memory leak or retained memory']):
    st=safe['stats']['title'][key];values=[st[k]['rate'] for k in PHASES]
    ax.barh([2,1,0],values,height=.50,color=PHASE_COLORS);ax.set_yticks([2,1,0],PHASE_NAMES);ax.set_xlim(0,max(values)*1.55);ax.set_ylim(-.6,2.6)
    ax.set_title(title,loc='left',fontsize=12,pad=15,fontweight='bold');ax.set_xlabel('Reports / million npm requests');ax.grid(axis='y',visible=False);ax.grid(axis='x',visible=True);ax.tick_params(length=0)
    for y,val,phase in zip([2,1,0],values,PHASES):ax.text(val+max(values)*.035,y,f"{val:.3f} · n={st[phase]['n']}",va='center',fontsize=10,color=INK)
save(fig,'02-crashes-and-leaks','Periods: 14 Nov–13 May (181 days); 15 May–19 Aug (97); 21 Aug–28 Oct (69). Both event days are excluded.\nStable stayed on Zig during the canary period. Counts include all versions. Leaks: 15 / 7 / 5 reports. No causal effect is estimated.')

# 3. A ratio against a fixed pooled pre-period reference (not percent-change ratios).
fig,ax=plt.subplots(figsize=(12,5.7));fig.subplots_adjust(left=.085,right=.96,bottom=.20,top=.76)
header(fig,'Are reports growing faster than npm requests?','Q = report growth index / npm growth index · all possible bug reports · before-merge reference = 1')
ax.plot(dates,arr(series['ratio7']),color='#798896',alpha=.60,lw=1,label='Previous 7 days')
ax.plot(dates,arr(series['ratio28']),color=POST,lw=2.6,label='Previous 28 days')
ax.axhline(1,color=MUTED,ls='--',lw=1,label='Before-merge reference = 1');ax.set_ylim(bottom=0);ax.set_ylabel('Relative reports / npm requests');timeline(ax);events(ax)
ax.legend(loc='upper center',bbox_to_anchor=(.5,1.15),ncol=3,fontsize=10)
ax.text(.98,.90,f"Canary period: {safe['stats']['title']['all']['canary']['rate']/safe['stats']['title']['all']['pre']['rate']:.3f}× · After stable: {safe['stats']['title']['all']['stable']['rate']/safe['stats']['title']['all']['pre']['rate']:.3f}×",ha='right',va='top',transform=ax.transAxes,color=POST,fontsize=12,fontweight='bold',bbox={'facecolor':PAPER,'edgecolor':'none','pad':4})
save(fig,'03-relative-growth','Below 1: fewer reports per npm request than before the merge. A rising line means the rate is increasing.\nnpm requests do not count active users. Shading marks the canary period. Windows can cross event dates.')

# 4. Three arrival-date groups retain overlapping component matches.
fig,ax=plt.subplots(figsize=(12,7.4));fig.subplots_adjust(left=.25,right=.94,bottom=.18,top=.77)
header(fig,'Which components do report titles name in each period?','Overlapping title matches · 1,802 before merge / 1,004 in canary period / 1,385 after stable')
ks=[k for k in c['periods']['pre']['components'] if k!='unclassified'];y=np.arange(len(ks));maxshare=0
for original,off,col,label in zip(['pre','pre_stable','stable'],[-.24,0,.24],PHASE_COLORS,PHASE_NAMES):
    data=c['periods'][original]['components'];vals=[data[k]['share'] for k in ks];maxshare=max(maxshare,max(vals))
    ax.barh(y+off,vals,height=.22,color=col,label=label)
ax.set_yticks(y,[c['periods']['pre']['components'][k]['label'] for k in ks]);ax.invert_yaxis();ax.set_xlabel('Share of possible bug reports (%)');ax.set_xlim(0,maxshare*1.15);ax.grid(axis='y',visible=False);ax.grid(axis='x',visible=True);ax.tick_params(length=0)
fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.06,.85),ncol=3)
save(fig,'04-component-mix','These report-date groups use exact event timestamps; the npm rate tables use complete days and exclude both event days.\nA report can match several components. Title detail and labels differ. This does not identify a defect cause or language effect.')

# 5. Raw daily, exclusive type stacks for three explicitly named representative versions.
selected=['1.3.14','1.4.0','1.4.4'];buckets={version:{k:np.zeros(len(dates)) for k in keys} for version in selected};indices={d:i for i,d in enumerate(v['days'])}
for row in v['daily']:
    if row['axis']=='symptoms' and row['version'] in buckets:
        for k,n in row['counts'].items():buckets[row['version']][k][indices[row['day']]]+=n
active=[i for i in range(len(dates)) if any(sum(buckets[ver][k][i] for k in keys)>0 for ver in selected)];left=dates[max(0,min(active)-7)]
fig,axs=plt.subplots(3,1,figsize=(12,8.8),sharex=True,sharey=True);fig.subplots_adjust(left=.085,right=.96,bottom=.16,top=.75,hspace=.45)
header(fig,'Which problem types were reported for each version?','One column per UTC report-opening day · Zig line 1.3.14; Rust lines 1.4.0 and 1.4.4')
fig.legend([Patch(color=COLORS[k],label=SHORT[k]) for k in keys],[SHORT[k] for k in keys],loc='upper left',bbox_to_anchor=(.06,.865),ncol=5,fontsize=9,handlelength=1.3)
for i,(ax,version) in enumerate(zip(axs,selected)):
    bottom=np.zeros(len(dates))
    for k in keys:ax.bar(dates,buckets[version][k],bottom=bottom,width=.95,color=COLORS[k],linewidth=0);bottom+=buckets[version][k]
    ax.set_title(f"Bun {version}  ·  {v['counts'][version]} reports",loc='left',fontsize=12,fontweight='bold',pad=7)
    ax.set_ylabel('Reports');timeline(ax);ax.set_xlim(left,dates[-1]+dt.timedelta(days=1));events(ax,labels=i==0)
save(fig,'05-daily-versions','These are three selected versions. The website includes other versions, unknown versions, and reports with several versions.\nFamily follows the version line, not the report date. Shaded dates had Zig stable + Rust canary. The final day is partial.')

# 6. Whole-window issue follow-up and a stable-release strip, in the original chart idiom.
fig,(ax,rel)=plt.subplots(2,1,figsize=(12,6.5),sharex=True,gridspec_kw={'height_ratios':[4,1]});fig.subplots_adjust(left=.085,right=.96,bottom=.19,top=.77,hspace=.32)
header(fig,'Stable releases resumed; closure shares still differ','Possible bug reports by opening week and current state · stable releases below')
w=c['weekly'];xs=[parse(r['start']) for r in w];fixed=np.array([r['fixed'] for r in w]);other=np.array([r['bugs']-r['fixed'] for r in w]);widths=[6.2 if not r['partial'] else 1.7 if i==len(w)-1 else 6.2 for i,r in enumerate(w)]
ax.bar(xs,fixed,width=widths,align='edge',color=[CYAN if not r['partial'] else '#657585' for r in w],label='Marked as fixed')
ax.bar(xs,other,bottom=fixed,width=widths,align='edge',color=[POST if not r['partial'] else '#8895a3' for r in w],label='Other closure or still open')
ax.set_ylabel('Possible bug reports / week');ax.legend(handles=[Patch(color=CYAN,label='Marked as fixed'),Patch(color=POST,label='Other closure or still open')],loc='upper left',bbox_to_anchor=(0,1.18),ncol=2);timeline(ax);events(ax)
rel.grid(visible=False);rel.set_yticks([]);rel.set_ylim(-1,1);rel.axhline(0,color=GRID,lw=1.5)
for i,(d,tag) in enumerate(p2['releases']):
    if v['days'][0]<=d<=v['days'][-1]:
        x=parse(d);rel.plot([x,x],[-.15,.15],color=MUTED,lw=1.5)
        if tag=='1.3.14' or tag.startswith('1.4.'):
            lane=.55 if tag in ['1.4.1','1.4.3'] else -.65
            rel.text(x,lane,tag,ha='center',va='center',color=CYAN if tag.startswith('1.4.') else MUTED,fontsize=9)
rel.axvspan(parse(safe['merge']),parse(safe['stable']),color=POST,alpha=.12)
rel.text(parse('2026-06-30'),.58,'98 days: merge → first Rust stable',ha='center',fontsize=9,color=POST)
rel.set_ylabel('Stable\nreleases',rotation=0,labelpad=34,va='center');timeline(rel)
save(fig,'06-release-and-followup','Before-merge states were observed in August; after-merge states in October. The first and last weeks are partial (grey).\nUse the 30-day table to compare equal follow-up times. The release strip labels selected versions.')

# 7. Weekly version map with an aligned npm context strip.
from matplotlib.colors import ListedColormap
m=load(D/'family-matrix.json');rows=m['rows'];top=sorted([r for r in rows if r['family']!='unclear'],key=lambda r:-r['total'])[:12];picked={r['key'] for r in top};shown=top.copy()
for family in ['zig','rust','unclear']:
    rest=[r for r in rows if r['family']==family and r['key'] not in picked]
    shown += [r for r in rest if r['version'] in ['unknown','multiple']]
    rest=[r for r in rest if r['version'] not in ['unknown','multiple']]
    if rest:shown.append({'family':family,'version':'other','weekly':[{'all':sum(r['weekly'][i].get('all',0) for r in rest)} for i in range(len(m['weeks']))]})
def order(r):return (['zig','rust','unclear'].index(r['family']),[int(x) if x.isdigit() else x for x in re.split(r'(\d+)',r['version'])])
shown.sort(key=order)
values=np.array([[w.get('all',0) for w in r['weekly']] for r in shown]);codes=np.digitize(values,[.5,1.5,4.5,9.5,24.5,49.5]);palette=['#19212a','#263e58','#345c80','#4b80aa','#69a4ce','#98cbe8','#d8effb']
fig,(ax,context)=plt.subplots(2,1,figsize=(14,10.5),sharex=True,gridspec_kw={'height_ratios':[max(4,len(shown)*.34),1.4]});fig.subplots_adjust(left=.235,right=.97,bottom=.13,top=.81,hspace=.25)
header(fig,'Which versions received reports before, during, and after the rollout?','Rows group inferred version families. Columns are report-opening weeks. Colour counts reports; it does not measure risk.')
fig.legend([Patch(color=x,label=l) for x,l in zip(palette,['0','1','2–4','5–9','10–24','25–49','50+'])],['0','1','2–4','5–9','10–24','25–49','50+'],loc='upper left',bbox_to_anchor=(.23,.88),ncol=7,title='Reports per week',fontsize=10)
ax.imshow(codes,aspect='auto',interpolation='nearest',cmap=ListedColormap(palette),vmin=0,vmax=6)
short={'unknown':'no version','multiple':'several versions','other':'other versions'}
ax.set_yticks(range(len(shown)),[r['family'].title()+' · '+short.get(r['version'],r['version']) for r in shown]);ax.grid(False);ax.tick_params(length=0,pad=8)
for i in range(len(shown)):
    for j in range(len(m['weeks'])):
        if values[i,j]>=10:ax.text(j,i,str(values[i,j]),ha='center',va='center',fontsize=7,color=PAPER if codes[i,j]>=4 else INK)
pm=load(D/'popularity.json');dl={r['day']:r['downloads'] for r in pm['npm']['daily']};weekly=[]
for start in m['weeks']:
    days=[(parse(start)+dt.timedelta(days=i)).date().isoformat() for i in range(7)];weekly.append(sum(dl[d] for d in days)/7 if all(d in dl for d in days) else np.nan)
context.plot(range(len(weekly)),weekly,color=INK,lw=2);context.set_ylabel('All-version npm\nrequests / day');clean(context);context.ticklabel_format(axis='y',style='sci',scilimits=(3,3));context.set_ylim(bottom=0)
for date,label in [(m['merge'],'Merge · 14 May'),(m['stable'],'Rust stable · 20 Aug')]:
    x=(parse(date[:10])-parse(m['weeks'][0])).days/7-.5
    ax.axvline(x,color=CYAN,lw=1.2,ls='--');context.axvline(x,color=CYAN,lw=1.2,ls='--');ax.text(x+.2,-.9,label,color=CYAN,fontsize=10,ha='left',va='bottom')
for axis in [ax,context]:axis.set_xlim(-.5,len(m['weeks'])-.5)
context.set_xticks(range(0,len(m['weeks']),4),[parse(d).strftime('%d %b') for d in m['weeks'][::4]])
save(fig,'07-version-family-map','Zig stable continued between merge and 20 Aug; Rust was canary. Families are inferred from stated versions, not verified binaries.\nUnknown, multiple, conflicting-date and old development versions remain unclear. First/last report weeks are partial.\nThe npm line uses complete weeks and all versions. There is no historical per-version installation denominator or causal Rust estimate.')

manifest={'snapshot':c['generated'],'npm_through':safe['download_through'],'files':sorted(p.name for p in OUT.glob('*.png')),'calculation_source':'part3/combined-series.js','matrix_source':'part3/data/family-matrix.json','stats':safe['stats']['title']}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Rendered',len(manifest['files']),'README figures.')
