import adapter from '@sveltejs/adapter-static';
import { vitePreprocess} from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Enable TypeScript, PostCSS (for Tailwind), etc.
  preprocess: vitePreprocess(),

  kit: {
    // Use the static adapter to output to 'build/'
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: "index.html"
    }),
  }
};

export default config;