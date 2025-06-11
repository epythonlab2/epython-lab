// embedYouTubeInit.js
document.addEventListener('DOMContentLoaded', function () {
    const interval = setInterval(() => {
      const container = document.querySelector('.quill-content');
      if (container && container.innerHTML.includes("youtu")) {
        window.embedYouTubeLinks();
        clearInterval(interval);
      }
    }, 300);
  });
  