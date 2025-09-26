/**
 * API service for OMR Checker frontend
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8009';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for image processing
});

/**
 * Upload and process OMR sheet
 * @param {File} file - Image file to upload
 * @param {string} examKey - Answer key identifier
 * @returns {Promise} API response with processing results
 */
export const uploadOMRSheet = async (file, examKey = 'exam1') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('exam_key', examKey);

  try {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.detail || 'Server error occurred');
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      // Something else happened
      throw new Error('Request failed: ' + error.message);
    }
  }
};

/**
 * Get available answer keys
 * @returns {Promise} List of available answer keys
 */
export const getAnswerKeys = async () => {
  try {
    const response = await api.get('/answer-keys');
    return response.data.answer_keys;
  } catch (error) {
    console.error('Failed to fetch answer keys:', error);
    return ['exam1']; // Fallback to default
  }
};

/**
 * Health check endpoint
 * @returns {Promise} Server status
 */
export const checkServerHealth = async () => {
  try {
    const response = await api.get('/');
    return response.data;
  } catch (error) {
    throw new Error('Server is not responding');
  }
};
