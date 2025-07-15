import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

export default {
  input: './app/static/js/lucide-init.js', // Your entry JS file
  output: {
    file: './app/static/js/lucide-bundle.js', // Output bundled JS file
    format: 'umd',  // UMD format makes the bundle compatible with global object in browsers
    name: 'lucide',  // The global variable to attach to the window
  },
  plugins: [
    resolve(),  // Resolves modules in node_modules
    commonjs(), // Converts CommonJS modules to ES6 modules
  ],
};
