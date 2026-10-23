import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Worktrees may share node_modules. Keep optimizer state local to this app.
  cacheDir: '.vite',
  build: {
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            { name: 'catalog', test: /[\\/]src[\\/]data[\\/]catalog\.json$/, priority: 40 },
            { name: 'react', test: /node_modules[\\/](react|react-dom|scheduler)[\\/]/, priority: 30 },
            { name: 'workflow', test: /node_modules[\\/]@xyflow[\\/]/, priority: 20 },
            { name: 'charts', test: /node_modules[\\/]recharts[\\/]/, priority: 10 },
            { name: 'libraries', test: /node_modules[\\/]/, priority: 1 },
          ],
        },
      },
    },
  },
});
