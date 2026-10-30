const assert=require('node:assert/strict');
const {build}=require('./combined-series.js');
const input={days:['2026-05-11','2026-05-12','2026-05-13','2026-05-14','2026-05-15','2026-05-16'],counts:{'2026-05-11':{a:99},'2026-05-12':{a:2,b:2},'2026-05-13':{a:6,b:2},'2026-05-14':{a:4},'2026-05-15':{a:3,b:1},'2026-05-16':{a:7}},types:['a','b'],downloads:{'2026-05-11':100,'2026-05-12':100,'2026-05-13':300,'2026-05-14':500,'2026-05-15':800},firstPartial:'2026-05-11',lastPartial:'2026-05-16',merge:'2026-05-14',stable:'2026-05-14'};
const raw=build(input);assert.equal(raw.reportSeries.a[5],7);assert.equal(raw.downloadSeries[5],null);
assert.deepEqual(raw.periods.pre,{days:2,reports:12,downloads:400,reportsPerDay:6,downloadsPerDay:200,rate:30000});
assert.equal(raw.periods.post.days,1);assert.equal(raw.periods.post.rate,5000); // omit event and partial days
const rate=build({...input,mode:'rate',windowDays:2});
assert.equal(rate.reportSeries.a[2],8/400*1e6); // ratio of sums, not mean of daily ratios
assert.equal(rate.reportSeries.b[2],4/400*1e6);
assert.equal(rate.reportSeries.a[1],null);assert.equal(rate.reportSeries.a[5],null);
const index=build({...input,mode:'index'});assert.equal(index.reportSeries.a[2],100);assert.equal(index.reportSeries.b[2],2/6*100);assert.equal(index.downloadSeries[2],150);
const zero=build({...input,counts:{},mode:'index'});assert(zero.reportSeries.a.every(v=>v===null));
const noDownload=build({...input,downloads:{...input.downloads,'2026-05-15':0},mode:'rate'});assert.equal(noDownload.reportSeries.a[4],null);
const average=build({...input,windowDays:2});assert.equal(average.reportSeries.a[2],4);assert.equal(average.reportSeries.a[5],null);
console.log('Combined chart: checked matched days, partial-day exclusions, missing/zero downloads, ratio-of-sums smoothing and common-base indices.');
const fs=require('fs'),path=require('path');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'data/version-daily.json'))),pop=JSON.parse(fs.readFileSync(path.join(__dirname,'data/popularity.json')));
const counts={};for(const r of data.daily){if(r.axis!=='symptoms')continue;counts[r.day]||={};for(const [k,v] of Object.entries(r.counts))counts[r.day][k]=(counts[r.day][k]||0)+v;}
const types=Object.keys(data.types.symptoms),downloads=Object.fromEntries(pop.npm.daily.map(r=>[r.day,r.downloads]));
const real={days:data.days,counts,types,downloads,firstPartial:data.days[0],lastPartial:data.days.at(-1),merge:'2026-05-14',stable:'2026-08-20'};
const ratios=build({...real,mode:'rate'}),indexed=build({...real,mode:'index'});
const validPre=[];
data.days.forEach((d,i)=>{
 if(d!==real.firstPartial&&d!==real.lastPartial&&downloads[d]>0){
  const reports=Object.values(counts[d]||{}).reduce((a,b)=>a+b,0),stack=types.reduce((a,k)=>a+ratios.reportSeries[k][i],0);
  assert(Math.abs(stack-reports/downloads[d]*1e6)<1e-7);
  if(d<real.merge)validPre.push(types.reduce((a,k)=>a+indexed.reportSeries[k][i],0));
 }else assert(types.every(k=>ratios.reportSeries[k][i]===null));
});
assert(Math.abs(validPre.reduce((a,b)=>a+b,0)/validPre.length-100)<1e-7);
console.log('Real snapshot: daily type-rate stacks conserve total reports; pre-merge report index averages exactly 100.');
assert.equal(rate.growthRatio[2],1); // (12 / 400) / (6 / 200)
assert.equal(rate.growthRatio[5],null);assert.equal(noDownload.growthRatio[4],null);assert(zero.growthRatio.every(v=>v===null));
data.days.forEach((d,i)=>{
 const q=ratios.growthRatio[i];if(q===null)return;
 const r=types.reduce((sum,k)=>sum+indexed.reportSeries[k][i],0),dl=indexed.downloadSeries[i];
 assert(Math.abs(q-r/dl)<1e-9);
 const dailyRate=types.reduce((sum,k)=>sum+ratios.reportSeries[k][i],0);
 assert(Math.abs(q-dailyRate/ratios.periods.pre.rate)<1e-9);
});
console.log('Relative-growth ratio equals report-index/download-index and normalized rate/baseline rate; undefined denominators remain gaps.');
