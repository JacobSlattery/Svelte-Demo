<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import SettingsPanel from "../lib/WaveformSettings.svelte";
  import WaveformChart from "../lib/WaveformChart.svelte";


  let socket: WebSocket;
  let waveformData: [number, number][] = [];

  let generate_wave = false;
  let frequency = 65;
  let amplitude = 0.5;
  let samples = 500;
  let frame_size = 0.1;
  let frame_rate = 24;

  onMount(() => {
    socket = new WebSocket("ws://localhost:8000/ws/waveform");
    socket.binaryType = "arraybuffer";
    socket.addEventListener("open", () => {
      console.log("WebSocket connection established");
    });

    socket.addEventListener("message", (event) => {
      const flat_array = new Float32Array(event.data);
      let result: [number, number][] = [];
      for (let i = 0; i < flat_array.length; i += 2) {
        result.push([flat_array[i], flat_array[i + 1]]);
      }
      waveformData = result;
    });
  });

  $: if (socket?.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ generate_wave, frequency, amplitude, samples, frame_size, frame_rate }));
  }

  onDestroy(() => {
    socket?.close();
  });
</script>

<div>
  <SettingsPanel bind:generate_wave bind:frequency bind:amplitude bind:samples bind:frame_size bind:frame_rate />
  <div class="p-4 bg-gray-900 rounded-lg shadow-md space-y-4">
    <WaveformChart data={waveformData} width="auto" height="400" />
  </div>
</div>  