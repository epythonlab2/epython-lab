// static/api/tutorial.js
import { fetchSubtopicData } from './api.js';

document.addEventListener("DOMContentLoaded", async () => {
  const topicSlug = window.FLASK_DATA.topicSlug;
  const subtopicSlug = window.FLASK_DATA.subtopicSlug;

  // Track local progress
  let storedProgress = {};
  try {
    storedProgress = JSON.parse(localStorage.getItem("progress")) || {};
    if (!storedProgress[topicSlug]) storedProgress[topicSlug] = [];
    if (!storedProgress[topicSlug].includes(subtopicSlug)) {
      storedProgress[topicSlug].push(subtopicSlug);
      localStorage.setItem("progress", JSON.stringify(storedProgress));
    }
    localStorage.setItem("lastVisited", JSON.stringify({ topic: topicSlug, subtopic: subtopicSlug }));
  } catch (e) {
    console.warn("Progress storage error", e);
  }

  try {
    const data = await fetchSubtopicData(topicSlug, subtopicSlug);

    // Render tutorial
    document.getElementById("tutorial-title").textContent = data.title;
    document.getElementById("tutorial-content").innerHTML = `
      <div class="dynamic-code quill-content" id="dynamic-code-0">${data.content}</div>
    `;
    highlightCodeBlocks("dynamic-code-0");

    // Next subtopic link
    const nextLink = document.getElementById("next-subtopic-link");
    if (data.next_subtopic_slug) {
      nextLink.href = `/python/${data.next_subtopic_slug}`;
      nextLink.textContent = "Continue to Next Lesson →";
      nextLink.classList.remove("hidden", "cursor-not-allowed", "bg-gray-400", "hover:bg-gray-400");
    } else {
      nextLink.textContent = "You’ve completed all lessons";
      nextLink.href = "#";
      nextLink.classList.remove("hidden");
      nextLink.classList.add("cursor-not-allowed", "bg-gray-400", "hover:bg-gray-400");
    }

    // Progress Calculation
    if (Array.isArray(data.all_subtopics)) {
      const total = data.all_subtopics.length;
      const completed = Object.values(storedProgress).flat();
      const filtered = completed.filter(slug => data.all_subtopics.includes(slug));
      const unique = [...new Set(filtered)];
      const percent = Math.round((unique.length / total) * 100);

      const progressBar = document.getElementById("progress-bar");
      const progressText = document.getElementById("progress-text");

      if (progressBar) progressBar.style.width = `${percent}%`;
      if (progressText) progressText.textContent = `Progress: ${percent}%`;
    }

  } catch (err) {
    document.getElementById("tutorial-content").innerHTML = `
      <p class="text-red-600">Failed to load tutorial content.</p>
    `;
    console.error("Error loading content:", err);
  }
});

/**
 * Wraps Quill's code blocks with language-specific classes and applies Prism syntax highlighting.
 * @param {string} containerId - The container element ID where code blocks reside.
 */
function highlightCodeBlocks(containerId) {
  setTimeout(() => {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.querySelectorAll("pre code").forEach(block => Prism.highlightElement(block));
  }, 0);
}

