<script lang="ts">
  export let settings: {
    amplitude: number;
    frequency: number;
  };
</script>

<div class="p-4 bg-white rounded-lg shadow-md space-y-4">
  <h2 class="text-xl font-semibold">Settings</h2>

  <div>
    <label class="block mb-1">Amplitude: {settings.amplitude.toFixed(1)}
      <input
        type="range"
        min="0"
        max="5"
        step="0.1"
        bind:value={settings.amplitude}
        class="w-full"
      />
    </label>
  </div>

  <div>
    <label class="block mb-1">Frequency: {settings.frequency.toFixed(1)} Hz
      <input
        type="range"
        min="0.5"
        max="10"
        step="0.1"
        bind:value={settings.frequency}
        class="w-full"
      />
    </label>
  </div>
</div>