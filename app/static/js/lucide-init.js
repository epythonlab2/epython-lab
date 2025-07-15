import { createIcons, icons } from 'lucide';

// Export so Rollup includes these in the global bundle object
export { createIcons, icons };

// Optional: auto-run createIcons on DOMContentLoaded if you want
window.addEventListener('DOMContentLoaded', () => {
  createIcons({ icons });
});
