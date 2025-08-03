<script lang="ts">
  export let frequency: number;
  export let amplitude: number;
  export let samples: number;
  export let cycles: number;
  export let frame_rate: number;
</script>

<div class="p-4 bg-white rounded-lg shadow-md space-y-4">
  <h2 class="text-xl font-semibold">Settings</h2>

  <div>
    <label>
      Frequency:
      <input type="range" bind:value={frequency} min="20" max="2000" step="1" />
      {frequency.toFixed(2)} Hz
    </label>
  </div>

  <div>
    <label>
      Amplitude:
      <input type="range" bind:value={amplitude} min="0" max="1" step="0.01" />
      {amplitude.toFixed(2)}
    </label>
  </div>

  <div>
    <label>
      Samples:
      <input type="range" bind:value={samples} min="100" max="1000" step="1" />
      {samples.toFixed(2)}
    </label>
  </div>

  <div>
    <label>
      Cycles:
      <input type="range" bind:value={cycles} min="1" max="10" step="1" />
      {cycles.toFixed(2)}
    </label>
  </div>

  <div>
    <label>
      Frame Rate:
      <input type="range" bind:value={frame_rate} min="1" max="144" step="1" />
      {frame_rate.toFixed(2)}
    </label>
  </div>
</div>