// embedYouTube.js
window.embedYouTubeLinks = function () {
  const container = document.querySelector('.quill-content');
  if (!container) return;

  const ytLinks = container.querySelectorAll('a[href*="youtu.be"], a[href*="youtube.com/watch"]');
  if (ytLinks.length === 0) {
    console.log('No YouTube links found.');
    return;
  }

  ytLinks.forEach(link => {
    if (link.dataset.processed) return;

    let videoId = null;
    try {
      const url = new URL(link.href);
      if (url.hostname === 'youtu.be') {
        videoId = url.pathname.slice(1);
      } else if (url.hostname.includes('youtube.com')) {
        videoId = url.searchParams.get('v');
      }
    } catch (err) {
      console.warn('Invalid YouTube URL:', link.href);
      return;
    }

    if (!videoId) return;

    const embed = document.createElement('div');
    embed.className = 'video-embed';
      embed.innerHTML = `
        <div class="video-title text-base font-semibold mb-2">${link.textContent.trim()}</div>
        <a href="${link.href}" target="_blank" rel="noopener noreferrer" aria-label="Watch Video: ${link.textContent.trim()}">
          <div class="thumbnail" aria-hidden="true">
            <img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg" alt="Video Thumbnail" />
            <div class="play-button"></div>
          </div>
        </a>
      `;
    

    link.parentElement.replaceChild(embed, link);
    embed.dataset.processed = "true";
  });
};
