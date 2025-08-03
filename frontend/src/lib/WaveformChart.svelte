<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import * as echarts from 'echarts';
  import type { ECharts, EChartsOption } from 'echarts';

  export let data: [number, number][] = [];
  export let width = 500;
  export let height = 400;

  let chartDom: HTMLDivElement;
  let chart: ECharts;

  onMount(() => {
    chart = echarts.init(chartDom);

    const option: EChartsOption = {
      animation: true,
      grid: {
        top: 40,
        left: 50,
        right: 40,
        bottom: 50
      },
      xAxis: {
        show: false,
      },
      yAxis: {
        show: false,
        min: -1,
        max: 1,
      },
      series: [
        {
          type: 'line',
          showSymbol: false,
          clip: true,
          data: data
        }
      ]
    };

    chart.setOption(option);
    const ro = new ResizeObserver(() => chart.resize());
    ro.observe(chartDom);
  });

  $: if (chart) {
    chart.setOption({ series: [{ data }] });
  }

  onDestroy(() => {
    if (chart) {
      chart.dispose();
    }
  });
</script>

<div
  bind:this={chartDom}
  style="width: {width}px; height: {height}px;"
></div>
