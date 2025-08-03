<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import SettingsPanel from '../lib/SettingsPanel.svelte';
  import WaveformChart from '../lib/WaveformChart.svelte';


  let socket = new WebSocket("ws://localhost:8000/ws/waveform");
  let waveformData: [number, number][] = [];

  let frequency = 20;
  let amplitude = 0.5;
  let samples = 100;
  let frame_size = 0.1;
  let frame_rate = 30;
  let ready = false;

  function sendSettings() {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ frequency, amplitude, samples, frame_size, frame_rate }));
    }
  }

  onMount(() => {
    socket = new WebSocket('ws://localhost:8000/ws/waveform');
    socket.addEventListener('open', () => {
      console.log('WebSocket connection established');
      ready = true;
      sendSettings();
    });

    socket.addEventListener('message', (evt) => {
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

<div class="flex flex-col md:flex-row h-screen">
  <div class="flex-1 min-w-[300px] p-4 flex flex-col bg-gray-100">
    <SettingsPanel bind:frequency bind:amplitude bind:samples bind:frame_size bind:frame_rate />
  </div>
  <div class="flex-1 min-w-[300px] p-4 flex flex-col relative">
    <WaveformChart data={waveformData} width={800} height={400} />
  </div>
</div>