// static/utils/debounce.js
export function debounce(func, delay) {
  let timeoutId;

  return function(...args) {
    // Clear the existing timeout (if any)
    clearTimeout(timeoutId);

    // Set a new timeout
    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
}
