<script lang="ts">
  import SettingsPanel from '../lib/SettingsPanel.svelte';
  import WaveformChart from '../lib/WaveformChart.svelte';

  // shared settings state
  let settings = {
    amplitude: 1,
    frequency: 2
  };
</script>

<div class="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
  <aside class="col-span-1">
    <SettingsPanel bind:settings />
  </aside>

  <main class="w-screen h-screen flex flex-col">
    <WaveformChart />
  </main>
</div>