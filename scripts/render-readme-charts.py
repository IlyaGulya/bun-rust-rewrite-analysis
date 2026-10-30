#!/usr/bin/env python3
"""Render GitHub-readable PNG figures from committed report inputs.

Requires matplotlib (see requirements-readme.txt) and Node.js. Calculation of
rolling/indexed series is delegated to the same JS module used in the HTML.
"""
import datetime as dt
import json
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
def clean(ax):
    ax.grid(axis='x',visible=False);ax.tick_params(length=0,pad=8)
def timeline(ax):
    clean(ax);ax.set_xlim(dates[0],dates[-1]+dt.timedelta(days=1))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
def events(ax,labels=True):
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
header(fig,'Reports grew more slowly than npm requests','Daily data through 30 October 2026 · previous 7 days · before-merge daily mean = 100')
keys=['unknown','multiple','crash','panic','hang','memory','performance','correctness','failure'];bottom=np.zeros(len(dates));handles=[]
for key in keys:
    y=arr(series['indexed']['reportSeries'][key]);ax.bar(dates,np.nan_to_num(y),bottom=bottom,width=.96,color=COLORS[key],linewidth=0)
    bottom+=np.nan_to_num(y);handles.append(Patch(color=COLORS[key],label=SHORT[key]))
line=ax.plot(dates,arr(series['indexed']['downloadSeries']),color=INK,lw=2.4,label='npm request growth')[0]
fig.legend([line]+handles,[line.get_label()]+[x.get_label() for x in handles],loc='upper left',bbox_to_anchor=(.06,.858),ncol=5,fontsize=9,columnspacing=1.3,handlelength=1.3)
ax.axhline(100,color=MUTED,lw=.8,ls=':');ax.set_ylabel('Growth index · before merge = 100');timeline(ax);events(ax)
save(fig,'01-growth-and-reports','Each report enters one stack group. npm data ends 28 Oct; rates and growth indices stop there.\nReports cover all installation methods. npm includes automated builds and repeat downloads; it does not count users.')

# 2. Separate scales keep the rare memory-retention signal visible.
fig,axs=plt.subplots(1,2,figsize=(12,4.7));fig.subplots_adjust(left=.10,right=.96,bottom=.25,top=.70,wspace=.32)
header(fig,'Crash and memory leak report rates fell','Complete days with both sources · reports per million npm requests · title matches do not confirm defects')
for ax,key,title in zip(axs,['crash','leak'],['Crash or fatal signal','Memory leak or retained memory']):
    st=safe['stats']['title'][key];values=[st['pre']['rate'],st['post']['rate']]
    ax.barh([1,0],values,height=.50,color=[PRE,POST]);ax.set_yticks([1,0],['Before','After']);ax.set_xlim(0,max(values)*1.50);ax.set_ylim(-.6,1.6)
    ax.set_title(title,loc='left',fontsize=12,pad=15,fontweight='bold');ax.set_xlabel('Reports / million npm requests');ax.grid(axis='y',visible=False);ax.grid(axis='x',visible=True);ax.tick_params(length=0)
    for y,val,phase in zip([1,0],values,['pre','post']):ax.text(val+max(values)*.035,y,f"{val:.2f}  ·  n={st[phase]['n']}",va='center',fontsize=10,color=INK)
    ax.text(.99,.92,f"{st['change_pct']:.1f}%",transform=ax.transAxes,ha='right',fontsize=14,color=POST,fontweight='bold')
save(fig,'02-crashes-and-leaks','Before: 14 Nov–13 May (23.08m requests). After: 15 May–28 Oct (70.54m). Excludes merge day and partial days.\nLeak count: 15 → 13 reports. Most of the rate decrease comes from more npm requests. This does not prove a Rust effect.')

# 3. A ratio against a fixed pooled pre-period reference (not percent-change ratios).
fig,ax=plt.subplots(figsize=(12,5.7));fig.subplots_adjust(left=.085,right=.96,bottom=.20,top=.76)
header(fig,'Are reports growing faster than npm requests?','Q = report growth index / npm growth index · all possible bug reports · before-merge reference = 1')
ax.plot(dates,arr(series['ratio7']),color='#798896',alpha=.60,lw=1,label='Previous 7 days')
ax.plot(dates,arr(series['ratio28']),color=POST,lw=2.6,label='Previous 28 days')
ax.axhline(1,color=MUTED,ls='--',lw=1,label='Before-merge reference = 1');ax.set_ylim(bottom=0);ax.set_ylabel('Relative reports / npm requests');timeline(ax);events(ax)
ax.legend(loc='upper center',bbox_to_anchor=(.5,1.15),ncol=3,fontsize=10)
ax.text(.98,.90,'Period rates: after / before = 0.435×',ha='right',va='top',transform=ax.transAxes,color=POST,fontsize=12,fontweight='bold',bbox={'facecolor':PAPER,'edgecolor':'none','pad':4})
save(fig,'03-relative-growth','Below 1: fewer reports per npm request than before the merge. A rising line means the rate is increasing.\nnpm requests do not count active users. Time windows across the merge include days from both periods.')

# 4. Title-based components, independent of the exclusive stacks above.
fig,ax=plt.subplots(figsize=(12,7.0));fig.subplots_adjust(left=.25,right=.92,bottom=.18,top=.77)
header(fig,'Which components do report titles name?','Component mentions in titles · reports can match several groups · 1,802 before / 2,389 after')
a=c['periods']['pre']['components'];b=c['periods']['post']['components'];ks=[k for k in a if k!='unclassified'];y=np.arange(len(ks))
ax.barh(y-.18,[a[k]['share'] for k in ks],height=.32,color=PRE,label='Before merge')
ax.barh(y+.18,[b[k]['share'] for k in ks],height=.32,color=POST,label='After merge')
ax.set_yticks(y,[a[k]['label'] for k in ks]);ax.invert_yaxis();ax.set_xlabel('Share of possible bug reports (%)');ax.set_xlim(0,18);ax.grid(axis='y',visible=False);ax.grid(axis='x',visible=True);ax.tick_params(length=0)
for i,k in enumerate(ks):
    for d,off,col in [(a,-.18,PRE),(b,.18,POST)]:ax.text(d[k]['share']+.14,i+off,f"{d[k]['share']:.2f}%",va='center',fontsize=9,color=col)
fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.06,.85),ncol=2)
save(fig,'04-component-mix','No component title match: 61.6% before → 48.3% after. Groups overlap. Mentions do not establish the cause.\nTitle detail and labels differ between periods. This comparison uses different dates from the npm rate tables.')

# 5. Raw daily, exclusive type stacks for three explicitly named representative versions.
selected=['1.3.14','1.4.0','1.4.4'];buckets={version:{k:np.zeros(len(dates)) for k in keys} for version in selected};indices={d:i for i,d in enumerate(v['days'])}
for row in v['daily']:
    if row['axis']=='symptoms' and row['version'] in buckets:
        for k,n in row['counts'].items():buckets[row['version']][k][indices[row['day']]]+=n
active=[i for i in range(len(dates)) if any(sum(buckets[ver][k][i] for k in keys)>0 for ver in selected)];left=dates[max(0,min(active)-7)]
fig,axs=plt.subplots(3,1,figsize=(12,8.8),sharex=True,sharey=True);fig.subplots_adjust(left=.085,right=.96,bottom=.16,top=.75,hspace=.45)
header(fig,'Which problem types were reported for each version?','One column per UTC report-opening day · selected versions · each report enters one stack group')
fig.legend([Patch(color=COLORS[k],label=SHORT[k]) for k in keys],[SHORT[k] for k in keys],loc='upper left',bbox_to_anchor=(.06,.865),ncol=5,fontsize=9,handlelength=1.3)
for i,(ax,version) in enumerate(zip(axs,selected)):
    bottom=np.zeros(len(dates))
    for k in keys:ax.bar(dates,buckets[version][k],bottom=bottom,width=.95,color=COLORS[k],linewidth=0);bottom+=buckets[version][k]
    ax.set_title(f"Bun {version}  ·  {v['counts'][version]} reports",loc='left',fontsize=12,fontweight='bold',pad=7)
    ax.set_ylabel('Reports');timeline(ax);ax.set_xlim(left,dates[-1]+dt.timedelta(days=1));events(ax,labels=i==0)
save(fig,'05-daily-versions','These are three selected versions. The website includes other versions, unknown versions, and reports with several versions.\nA stated version does not confirm an affected runtime. Plain 1.4.0 does not identify the channel. The final day is partial.')

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

manifest={'snapshot':c['generated'],'npm_through':safe['download_through'],'files':sorted(p.name for p in OUT.glob('*.png')),'calculation_source':'part3/combined-series.js','stats':safe['stats']['title']}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Rendered',len(manifest['files']),'README figures.')
