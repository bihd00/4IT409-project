import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'
import adapter from '@sveltejs/adapter-auto';

/** @type {import('@sveltejs').Config} */
const config = {
  kit: {
    adapter: adapter()
  },
  // Consult https://svelte.dev/docs#compile-time-svelte-preprocess
  // for more information about preprocessors
  preprocess: vitePreprocess()
};

export default config;