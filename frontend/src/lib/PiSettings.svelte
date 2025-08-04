<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let digits: number;
  export let duration: number;
  export let crossfade: number;
  export let key_root: string;
  export let harmony_type: string;
  export let harmony_speed: number;
  export let octave_doubling: boolean;
  export let harmony_movement: string;

  const dispatch = createEventDispatcher();

  function update() {
    dispatch("change", {
      digits,
      duration,
      crossfade,
      key_root,
      harmony_type,
      harmony_speed,
      octave_doubling,
      harmony_movement
    });
  }
</script>

<section class="p-4 bg-white rounded-lg shadow-md space-y-4">
  <h2 class="text-lg font-semibold">π Melody Settings</h2>
  <div class="grid grid-cols-2 gap-4">
    <label class="flex flex-col">
      Digits
      <input type="number" bind:value={digits} min="1" class="mt-1 p-1 border rounded" on:change={update} />
    </label>
    <label class="flex flex-col">
      Duration (s)
      <input type="number" bind:value={duration} step="0.1" min="0.1" class="mt-1 p-1 border rounded" on:change={update} />
    </label>
    <label class="flex flex-col">
      Crossfade (s)
      <input type="number" bind:value={crossfade} step="0.01" min="0" class="mt-1 p-1 border rounded" on:change={update} />
    </label>
    <label class="flex flex-col">
      Key Root
      <input type="text" bind:value={key_root} class="mt-1 p-1 border rounded" on:change={update} />
    </label>
    <label class="flex flex-col">
      Harmony Type
      <select bind:value={harmony_type} class="mt-1 p-1 border rounded" on:change={update}>
        <option value="third">Third</option>
        <option value="fifth">Fifth</option>
        <option value="sixth">Sixth</option>
      </select>
    </label>
    <label class="flex flex-col">
      Harmony Speed
      <input type="number" bind:value={harmony_speed} min="1" class="mt-1 p-1 border rounded" on:change={update} />
    </label>
    <label class="flex items-center space-x-2">
      <input type="checkbox" bind:checked={octave_doubling} on:change={update} />
      <span>Octave Doubling</span>
    </label>
    <label class="flex flex-col">
      Harmony Movement
      <select bind:value={harmony_movement} class="mt-1 p-1 border rounded" on:change={update}>
        <option value="random">Random</option>
        <option value="intervals">Intervals</option>
        <option value="chordal">Chordal</option>
      </select>
    </label>
  </div>
</section>
