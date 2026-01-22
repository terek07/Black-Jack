// Determine the API base URL based on environment
const getApiBaseUrl = () => {
  // In Codespaces, use the environment variable if available
  if (import.meta.env.VITE_API_BASE_URL) {
    // Remove trailing slash if present to avoid double slashes in URLs
    return import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '');
  }
  
  // Local development fallback
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl();
