import axios from 'axios';

// Create an Axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetches recommendations from the backend.
 * @param {string} prompt - The user's chat message.
 * @returns {Promise<object>} - The API response.
 */
export const fetchRecommendations = (prompt) => {
  return apiClient.post('/recommend', { prompt: prompt, top_k: 3 });
};

/**
 * Fetches data for the analytics dashboard.
 * @returns {Promise<object>} - The API response.
 */
export const fetchAnalyticsData = () => {
  return apiClient.get('/analytics-data');
};