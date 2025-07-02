// api/content-api.js
// This module provides functions for managing topics and subtopics via API requests.
// It uses a custom Axios client to interact with backend endpoints.

import client from './client.js'; // Axios instance with pre-configured baseURL and headers

// ─────────────────────────────────────────────────────────────
// SUBTOPIC OPERATIONS
// ─────────────────────────────────────────────────────────────

/**
 * Fetch subtopic details by its ID.
 * @param {string|number} subtopicId - The ID of the subtopic.
 * @returns {Promise<Object>} - Subtopic data from the server.
 * @throws {Error} - If the request fails.
 */
export async function fetchSubtopicData(subtopicId) {
  try {
    const response = await client.get(`/subtopic/${subtopicId}`);
    if (response.status !== 200) throw new Error('Failed to load subtopic');
    return response.data;
  } catch (err) {
    throw new Error(`Error: ${err.message}`);
  }
}

/**
 * Create a new subtopic or update an existing one.
 * @param {string|number|null} subtopicId - ID of the subtopic to update, or null for create.
 * @param {Object} payload - Subtopic content, including topicId for creation.
 * @returns {Promise<Object>} - The created or updated subtopic data.
 * @throws {Error} - If the request fails.
 */
export async function saveSubtopic(subtopicId, payload) {
  try {
    const response = subtopicId
      ? await client.put(`/subtopic/${subtopicId}`, payload)
      : await client.post(`/${payload.topicId}/subtopics`, payload);

    if (![200, 201].includes(response.status)) {
      throw new Error(response.data?.error || response.data?.message || 'Failed to save subtopic');
    }

    return response.data;
  } catch (err) {
    throw new Error(`Error: ${err.message}`);
  }
}

// ─────────────────────────────────────────────────────────────
// TOPIC OPERATIONS
// ─────────────────────────────────────────────────────────────

/**
 * Fetch paginated list of topics.
 * @param {number} page - Page number (default: 1).
 * @param {number} pageSize - Number of topics per page (default: 5).
 * @returns {Promise<Object>} - Contains topics list, total pages, etc.
 * @throws {Error} - If the request fails.
 */
export async function fetchTopics(page = 1, pageSize = 5) {
  try {
    const response = await client.get('', {
      params: { page, limit: pageSize },
    });

    if (response.status === 200 && response.data) {
      return response.data;
    }

    throw new Error('Failed to load topics');
  } catch (err) {
    console.error('Error fetching topics:', err);
    throw new Error(`Error: ${err.message}`);
  }
}

/**
 * Create a new topic.
 * @param {Object} payload - Contains topic data (e.g., title).
 * @returns {Promise<Object>} - Full Axios response.
 * @throws {Error} - If creation fails.
 */
export async function createTopic(payload) {
  try {
    const response = await client.post('', payload);

    if ([200, 201].includes(response.status) && response.data) {
      return response; // Full Axios response returned to allow flexibility
    }

    throw new Error('Failed to create topic');
  } catch (err) {
    console.error('Error creating topic:', err);
    throw new Error(`Error: ${err.message}`);
  }
}

/**
 * Edit an existing topic.
 * @param {string|number} topicId - The ID of the topic to edit.
 * @param {Object} payload - New data for the topic.
 * @returns {Promise<Object>} - Status object with `ok`, `message`, and optional `topic`.
 */
export async function editTopic(topicId, payload) {
  try {
    const response = await client.put(`/${topicId}`, payload);

    if ([200, 204].includes(response.status)) {
      return {
        ok: true,
        message: response.data?.message || 'Topic updated successfully',
        topic: response.data?.topic || null,
      };
    }

    return {
      ok: false,
      message: response.data?.message || 'Failed to update topic',
    };
  } catch (err) {
    console.error('Error updating topic:', err);
    return { ok: false, message: err.message };
  }
}

/**
 * Delete a topic by ID.
 * @param {string|number} topicId - The ID of the topic to delete.
 * @returns {Promise<Object>} - Confirmation response.
 * @throws {Error} - If deletion fails.
 */
export async function deleteTopic(topicId) {
  try {
    const response = await client.delete(`/${topicId}`);

    if (response.status === 200 && response.data) {
      return response.data;
    }

    throw new Error('Failed to delete topic');
  } catch (err) {
    console.error('Error deleting topic:', err);
    throw new Error(`Error: ${err.message}`);
  }
}

/**
 * Fetch topic details by its ID.
 * @param {string|number} topicId - The ID of the topic.
 * @returns {Promise<Object>} - Topic data from the server.
 * @throws {Error} - If the request fails.
 */
export async function fetchTopicById(topicId) {
  try {
    const response = await client.get(`/${topicId}`);
    if (response.status !== 200) throw new Error('Failed to load topic');
    return response.data;
  } catch (err) {
    throw new Error(`Error: ${err.message}`);
  }
}

/**
 * Delete a subtopic by its ID.
 * @param {string|number} subtopicId - The ID of the subtopic to delete.
 * @returns {Promise<boolean>} - Returns true if deletion was successful.
 * @throws {Error} - If the deletion fails.
 */
export async function deleteSubtopicById(subtopicId) {
  try {
    const response = await client.delete(`/subtopic/${subtopicId}`);
    if (response.status !== 200) throw new Error('Failed to delete subtopic');
    return true;
  } catch (err) {
    throw new Error(`Error: ${err.message}`);
  }
}
