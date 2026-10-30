// Only the pieces the charts use, so the inlined bundle stays a fraction of full ECharts.
import * as echarts from 'echarts/core';
import { CustomChart, LineChart, BarChart, HeatmapChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, DataZoomComponent, MarkLineComponent, MarkAreaComponent, LegendComponent, VisualMapComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([CustomChart, LineChart, BarChart, HeatmapChart, GridComponent, TooltipComponent, DataZoomComponent, MarkLineComponent, MarkAreaComponent, LegendComponent, VisualMapComponent, CanvasRenderer]);
window.echarts = echarts;
