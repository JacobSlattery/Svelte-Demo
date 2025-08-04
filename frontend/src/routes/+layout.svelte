<script lang="ts">
  import { page } from "$app/stores";
  import "../app.css";
</script>

<div class="grid grid-rows-[auto_1fr] h-screen">
  <!-- Row 1: full-width header -->
  <header class="row-start-1 row-end-2 bg-gray-100 p-4 shadow">
    <h1 class="text-2xl font-bold">Svelte Demo</h1>
  </header>

  <!-- Row 2: grid with fixed nav and main -->
  <div class="row-start-2 grid grid-cols-[auto_1fr]">

    <nav class="flex flex-col bg-gray-800 text-white p-2 space-y-2">
      <a href="/" 
        class="flex items-center justify-center w-12 h-12 rounded hover:bg-gray-700"
        class:selected={$page.url.pathname === "/"}
        title="Wave Visualizer">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><path fill="currentColor" d="M19 19h-2v-6h2zM4 10H2v12h2zm10 0h-2v12h2zm10 0h-2v12h2zM9 6H7v20h2zm20 0h-2v20h2z"/></svg>
        <span class="sr-only">
          Home
        </span>
      </a>
      <a
        href="/pi"
        class="flex items-center justify-center w-12 h-12 rounded hover:bg-gray-700"
        class:selected={$page.url.pathname === "/pi"}
        title="Sounds of Pi"
        >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 32 32"
          class="w-6 h-6 text-white"
          fill="currentColor">
          <path d="M25 4H10a2 2 0 0 0-2 2v14.556A3.96 3.96 0 0 0 6 20a4 4 0 1 0 4 4V12h15v8.556A3.96 3.96 0 0 0 23 20a4 4 0 1 0 4 4V6a2 2 0 0 0-2-2M6 26a2 2 0 1 1 2-2a2 2 0 0 1-2 2m17 0a2 2 0 1 1 2-2a2.003 2.003 0 0 1-2 2M10 6h15v4H10Z"/>
        </svg>
        <span class="sr-only">
          Sounds of Pi
        </span>
      </a>
    </nav>

    <!-- Main content -->
    <main class="p-2 overflow-auto">
      <slot />
    </main>
  </div>
</div>