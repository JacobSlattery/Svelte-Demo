<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import SettingsPanel from "../lib/WaveformSettings.svelte";
  import WaveformChart from "../lib/WaveformChart.svelte";


  let socket = new WebSocket("ws://localhost:8000/ws/waveform");
  let waveformData: [number, number][] = [];

  let frequency = 65;
  let amplitude = 0.5;
  let samples = 500;
  let frame_size = 0.1;
  let frame_rate = 24;
  let ready = false;

  function sendSettings() {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ frequency, amplitude, samples, frame_size, frame_rate }));
    }
  }

  onMount(() => {
    socket = new WebSocket("ws://localhost:8000/ws/waveform");
    socket.addEventListener("open", () => {
      console.log("WebSocket connection established");
      ready = true;
      sendSettings();
    });

    socket.addEventListener("message", (evt) => {
      const msg = JSON.parse(evt.data);
      waveformData = msg.data;
    });
  });

  $: if (ready) sendSettings();

  $: if (socket?.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ frequency, amplitude, samples, frame_size, frame_rate }));
  }

  onDestroy(() => {
    socket?.close();
  });
</script>

<div>
  <SettingsPanel bind:frequency bind:amplitude bind:samples bind:frame_size bind:frame_rate />
  <div class="p-4 bg-gray-900 rounded-lg shadow-md space-y-4">
    <WaveformChart data={waveformData} width="auto" height="400" />
  </div>
</div>  