/* Pure calculations shared by the offline report and its tests. */
const CombinedSeries = (() => {
  function build({days, counts, types, downloads, firstPartial, lastPartial, merge, stable, windowDays=1, mode='counts', baselineReportMean}) {
    const total=d=>types.reduce((s,k)=>s+((counts[d]||{})[k]||0),0);
    const eligible=d=>d!==firstPartial&&d!==lastPartial&&Number.isFinite(downloads[d])&&downloads[d]>=0;
    const base=days.filter(d=>eligible(d)&&d<merge);
    const baselineReports=baselineReportMean??(base.length?base.reduce((s,d)=>s+total(d),0)/base.length:0);
    const baselineDownloads=base.length?base.reduce((s,d)=>s+downloads[d],0)/base.length:0;
    const reportSeries=Object.fromEntries(types.map(k=>[k,[]]));
    const downloadSeries=[],growthRatio=[];
    days.forEach((day,i)=>{
      const dates=days.slice(Math.max(0,i-windowDays+1),i+1);
      const full=dates.length===windowDays;
      const countWindow=full&&(windowDays===1||dates.every(d=>d!==firstPartial&&d!==lastPartial));
      const paired=full&&dates.every(eligible);
      const hasDownloads=full&&dates.every(d=>Number.isFinite(downloads[d])&&downloads[d]>=0);
      const ds=hasDownloads?dates.reduce((s,d)=>s+downloads[d],0):null;
      const reports=dates.reduce((s,d)=>s+total(d),0);
      for(const key of types){
        const sum=dates.reduce((s,d)=>s+((counts[d]||{})[key]||0),0);
        let value=null;
        if(mode==='counts'&&countWindow)value=sum/windowDays;
        if(mode==='rate'&&paired&&ds>0)value=sum/ds*1e6;
        if(mode==='index'&&paired&&baselineReports>0)value=sum/windowDays/baselineReports*100;
        if(mode==='percent'&&countWindow&&reports>0)value=sum/reports*100;
        reportSeries[key].push(value);
      }
      growthRatio.push(paired&&ds>0&&baselineReports>0&&baselineDownloads>0?(reports/ds)/(baselineReports/baselineDownloads):null);
      downloadSeries.push(mode==='index'?(paired&&baselineDownloads>0?ds/windowDays/baselineDownloads*100:null):(hasDownloads?ds/windowDays:null));
    });
    const periods={};
    for(const [key,test] of Object.entries({pre:d=>d<merge,post:d=>d>merge,canary:d=>d>merge&&d<stable,stable:d=>d>stable})){
      const dates=days.filter(d=>eligible(d)&&test(d));
      const reports=dates.reduce((s,d)=>s+total(d),0),dl=dates.reduce((s,d)=>s+downloads[d],0);
      periods[key]={days:dates.length,reports,downloads:dl,reportsPerDay:dates.length?reports/dates.length:null,downloadsPerDay:dates.length?dl/dates.length:null,rate:dl>0?reports/dl*1e6:null};
    }
    return {reportSeries,downloadSeries,growthRatio,periods,baselineReports,baselineDownloads};
  }
  return {build};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=CombinedSeries;
