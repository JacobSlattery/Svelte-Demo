<script lang="ts">
  import { onDestroy } from "svelte";
  const browser = typeof window !== "undefined";
  import WaveformChart from "../../lib/WaveformChart.svelte";
  import PiSettings from "../../lib/PiSettings.svelte";

  let digits = 5;
  let duration = 1;
  let crossfade = 0.01;
  let key_root = "C4";
  let harmony_type = "third";
  let harmony_speed = 4;
  let octave_doubling = true;
  let harmony_movement = "chordal";

  let chartData: [number, number][] = [];
  let audioCtx: AudioContext | null = null;
  let playSrc: AudioBufferSourceNode | null = null;
  let rafId: number | null = null;

  async function loadAndPlayPi() {
    if (!browser) return;
    // Fetch the full waveform from the backend
    const res = await fetch(
      `http://localhost:8000/api/pi-waveform?digits=${digits}&duration=${duration}&crossfade=${crossfade}&key_root=${key_root}&harmony_type=${harmony_type}&harmony_speed=${harmony_speed}&octave_doubling=${octave_doubling}&harmony_movement=${harmony_movement}`
    );
    if (!res.ok) {
      console.error("Fetch failed with status", res.status);
      return;
    }
    let buf = await res.arrayBuffer();
    if (buf.byteLength % 4 !== 0) {
      console.error("Unexpected buffer length (bytes):", buf.byteLength);
      // Try truncating to nearest multiple of 4
      const validLength = buf.byteLength - (buf.byteLength % 4);
      console.warn("Truncating buffer to", validLength, "bytes");
      buf = buf.slice(0, validLength);
    }
    const samples = new Float32Array(buf);
    const sampleRate = 44100;

    // Initialize AudioContext on user gesture
    if (!audioCtx) {
      audioCtx = new AudioContext({ sampleRate });
      await audioCtx.resume();
    } else if (audioCtx.state === "suspended") {
      await audioCtx.resume();
    }

    // Create and play the buffer source
    if (playSrc) {
      playSrc.stop();
      playSrc.disconnect();
      playSrc = null;
    }
    const audioBuffer = audioCtx.createBuffer(1, samples.length, sampleRate);
    audioBuffer.copyToChannel(samples, 0);
    playSrc = audioCtx.createBufferSource();
    playSrc.buffer = audioBuffer;
    playSrc.connect(audioCtx.destination);
    playSrc.start();

    // Start chart animation in sync
    const windowSize = 1024;
    function updateChart() {
      if (!audioCtx || !playSrc) return;
      const t = audioCtx.currentTime; // seconds since start
      const pos = Math.floor(t * sampleRate);
      const slice = samples.subarray(pos, pos + windowSize);
      chartData = Array.from(slice, (y, i) => [i / sampleRate, y]);
      rafId = requestAnimationFrame(updateChart);
    }
    cancelAnimationFrame(rafId!);
    updateChart();
  }

  function stopPi() {
    if (!browser) return;
    if (playSrc) {
      playSrc.stop();
      playSrc.disconnect();
      playSrc = null;
    }
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    if (audioCtx) {
      audioCtx.close();
      audioCtx = null;
    }
  }

  onDestroy(() => {
    stopPi();
  });
</script>

<div>
  <PiSettings
    bind:digits
    bind:duration
    bind:crossfade
    bind:key_root
    bind:harmony_type
    bind:harmony_speed
    bind:octave_doubling
    bind:harmony_movement
  />
  <button
    class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
    on:click={loadAndPlayPi}>
    Load & Play π Melody
  </button>
  <button
    class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
    on:click={stopPi}>
    Stop
  </button>

  <WaveformChart data={chartData} width={1800} height={400} />
</div>
