// static/api/sidebar.js
import { fetchSidebarTopics } from "./api.js";

export function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  const isOpen = !sidebar.classList.contains("-translate-x-full");

  if (isOpen) {
    sidebar.classList.add("-translate-x-full");
    overlay.classList.add("hidden");
  } else {
    sidebar.classList.remove("-translate-x-full");
    overlay.classList.remove("hidden");
  }
}

export function closeSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  sidebar.classList.add("-translate-x-full");
  overlay.classList.add("hidden");
}

export function toggleSubtopics(submenuId, arrowId) {
  const subMenu = document.getElementById(submenuId);
  const arrow = document.getElementById(arrowId);

  if (subMenu.style.maxHeight && subMenu.style.maxHeight !== "0px") {
    subMenu.style.maxHeight = "0px";
    arrow.style.transform = "rotate(0deg)";
  } else {
    subMenu.style.maxHeight = subMenu.scrollHeight + "px";
    arrow.style.transform = "rotate(90deg)";
  }
}

function subMenuMaxHeight(itemCount) {
  return `${itemCount * 38}px`;
}

function scrollActiveSubtopicIntoView() {
  const sidebarEl = document.getElementById("sidebar");
  const activeLink = sidebarEl.querySelector(".active-subtopic");

  if (!activeLink || !sidebarEl) return;

  const sidebarScrollTop = sidebarEl.scrollTop;
  const sidebarHeight = sidebarEl.clientHeight;
  const activeOffsetTop = activeLink.offsetTop;
  const activeHeight = activeLink.offsetHeight;
  const margin = 8;

  if (activeOffsetTop + activeHeight > sidebarScrollTop + sidebarHeight) {
    sidebarEl.scrollTop = activeOffsetTop + activeHeight - sidebarHeight + margin;
  } else if (activeOffsetTop < sidebarScrollTop) {
    sidebarEl.scrollTop = activeOffsetTop - margin;
  }
}

export async function loadTopics() {
  try {
    const topics = await fetchSidebarTopics();

    const sidebar = document.getElementById("sidebar-topic-list");
    sidebar.innerHTML = "";

    const currentPath = window.location.pathname.toLowerCase();

    topics.forEach(topic => {
      const onlyOneSameSub =
        topic.subtopics &&
        topic.subtopics.length === 1 &&
        topic.subtopics[0].title.trim().toLowerCase() === topic.title.trim().toLowerCase();

      if (onlyOneSameSub) {
        const sub = topic.subtopics[0];
        const isActive = currentPath === `/python/${sub.slug.toLowerCase()}`;
        const activeClass = isActive ? "active-subtopic font-semibold text-green-700" : "";

        sidebar.innerHTML += `
          <li>
            <a href="/python/${sub.slug}" class="block ${activeClass}" onclick="window.sidebar.closeSidebar()">${sub.title}</a>
          </li>
        `;
      } else if (topic.subtopics && topic.subtopics.length > 0) {
        const topicId = `sub-${topic.id}`;
        const arrowId = `arrow-${topic.id}`;
        const hasActiveSub = topic.subtopics.some(
          sub => currentPath === `/python/${sub.slug.toLowerCase()}`
        );

        sidebar.innerHTML += `
          <li>
            <button
              onclick="window.sidebar.toggleSubtopics('${topicId}', '${arrowId}')"
              class="w-full text-left font-semibold hover:text-green-600 flex justify-between items-center focus:outline-none"
              aria-expanded="${hasActiveSub}"
              aria-controls="${topicId}"
            >
              ${topic.title}
              <span
                id="${arrowId}"
                class="inline-block transition-transform duration-300 text-green-600"
                style="transform: ${hasActiveSub ? 'rotate(90deg)' : 'rotate(0deg)'}"
                aria-hidden="true"
              >
                &#9656;
              </span>
            </button>
            <ul
              id="${topicId}"
              class="pl-5 mt-2 space-y-2 overflow-hidden transition-all duration-300 ease-in-out text-sm"
              style="max-height: ${hasActiveSub ? subMenuMaxHeight(topic.subtopics.length) : '0px'};"
            >
              ${topic.subtopics
                .map(sub => {
                  const isActive = currentPath === `/python/${sub.slug.toLowerCase()}`;
                  const activeClass = isActive ? "active-subtopic font-semibold text-green-700" : "";
                  return `
                    <li>
                      <a href="/python/${sub.slug}" class="block ${activeClass}" onclick="window.sidebar.closeSidebar()">
                        ${sub.title}
                      </a>
                    </li>
                  `;
                })
                .join("")}
            </ul>
          </li>
        `;
      } else {
        const isActive = currentPath === `/python/${topic.slug.toLowerCase()}`;
        const activeClass = isActive ? "active-subtopic font-semibold text-green-700" : "";

        sidebar.innerHTML += `
          <li>
            <a href="/python/${topic.slug}" class="block ${activeClass}" onclick="window.sidebar.closeSidebar()">${topic.title}</a>
          </li>
        `;
      }
    });

    scrollActiveSubtopicIntoView();
  } catch (error) {
    console.error("Failed to load topics:", error);
    const sidebar = document.getElementById("sidebar-topic-list");
    sidebar.innerHTML = `<li class="text-sm text-red-500">Failed to load topics.</li>`;
  }
}

// Initialize after DOM ready
document.addEventListener("DOMContentLoaded", loadTopics);
