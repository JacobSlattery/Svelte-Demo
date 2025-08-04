<script lang="ts">
  import { createEventDispatcher  } from "svelte";

  export let frequency: number;
  export let amplitude: number;
  export let samples: number;
  export let frame_size: number;
  export let frame_rate: number;

  let audioContext: AudioContext;
  let oscillator: OscillatorNode;
  let gainNode: GainNode;
  let playing = false;

  const dispatch = createEventDispatcher();

  function startSound() {
    audioContext = new AudioContext();
    oscillator = audioContext.createOscillator();
    gainNode = audioContext.createGain();

    oscillator.type = "sine";
    oscillator.frequency.value = frequency;
    gainNode.gain.value = amplitude;

    oscillator.connect(gainNode).connect(audioContext.destination);
    oscillator.start();
    playing = true;
    dispatch("play", { playing });
  }

  function stopSound() {
    oscillator.stop();
    audioContext.close();
    playing = false;
    dispatch("play", { playing });
  }

  $: if (playing) {
    if (oscillator) {
      oscillator.frequency.value = frequency;
    }
    if (gainNode) {
      gainNode.gain.value = amplitude;
    }
  }


</script>

<div class="p-4 bg-white rounded-lg shadow-md space-y-4">
  <h2 class="text-xl font-semibold">
    Sound Settings
  </h2>

  <div>
    <label>
      Frequency (Hz):
      <input type="range" bind:value={frequency} min="20" max="2000" step="1" />
      {frequency.toFixed(2)} Hz
    </label>
  </div>

  <div>
    <label>
      Amplitude (dBs):
      <input type="range" bind:value={amplitude} min="0" max="10" step="0.01" />
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
      Data Frame Size (Seconds):
      <input type="range" bind:value={frame_size} min="0.01" max="1" step="0.01" />
      {frame_size.toFixed(2)}
    </label>
  </div>

  <div>
    <label>
      Display Frame Rate (FPS):
      <input type="range" bind:value={frame_rate} min="1" max="144" step="1" />
      {frame_rate.toFixed(2)}
    </label>
  </div>

  <button
    class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
    on:click={playing ? stopSound : startSound}>
    {playing ? "Mute" : "Unmute"}
  </button>
</div>