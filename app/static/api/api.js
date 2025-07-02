// static/js/api.js
import client from "./client.js";

export async function fetchSubtopicData(topicSlug, subtopicSlug) {
  try {
    const response = await client.get(`/${topicSlug}/${subtopicSlug}`);
    return response.data;
  } catch (error) {
    console.error("API fetch error:", error);
    throw error;
  }
}

export async function fetchSidebarTopics() {
  try {
    const res = await client.get("/sidebar");
    return res.data;
  } catch (error) {
    console.error("Sidebar API fetch error:", error);
    throw error;
  }
}
