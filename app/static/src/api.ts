// app/static/src/api.ts
import axios, { AxiosError } from 'axios';
import { toast } from './ui/toast'; // Import toast utility

// Create Axios instance with base URL and credentials
const api = axios.create({
  baseURL: '/api/v1/', // Assuming your API is under /api/v1/
  withCredentials: true, // Essential for sending cookies (auth) and receiving Set-Cookie
});

// --- Request Interceptor ---
// Automatically attach CSRF token to requests
api.interceptors.request.use(
  (config) => {
    // Get CSRF token from meta tag
    const meta = document.querySelector('meta[name="csrf"]') as HTMLMetaElement | null;
    if (meta && meta.content) {
      // Add CSRF token to headers for XHR requests
      config.headers['X-CSRF-Token'] = meta.content;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- Response Interceptor ---
// Handle global errors like 401 (Unauthorized) and display toasts for others
api.interceptors.response.use(
  (response) => {
    // Any status code within the range of 2xx causes this function to trigger
    return response;
  },
  (error: AxiosError) => {
    // Any status codes outside the range of 2xx cause this function to trigger

    // --- Handle Network/Request Errors ---
    if (!error.response) {
      // Network error or request couldn't be made
      toast.error('Network error. Please check your connection.');
      console.error('Network Error:', error.message);
      return Promise.reject(error);
    }

    const status = error.response.status;
    const data = error.response.data as any; // Type as 'any' for flexibility

    // --- Handle Specific Status Codes ---
    if (status === 401) {
      // Unauthorized - likely token expired or invalid
      toast.error('Session expired. Please log in again.');
      // Redirect to login page
      window.location.href = '/';
      return Promise.reject(error); // Stop further processing
    }

    if (status === 403) {
        // Forbidden - CSRF or permission issue
        toast.error(data?.detail || 'Access forbidden.');
        return Promise.reject(error);
    }

    if (status === 422) {
        // Validation Error - show field-specific errors if possible, otherwise generic
        const detail = data?.detail;
        if (Array.isArray(detail)) {
            // Pydantic validation errors usually come as an array
            const messages = detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
            toast.error(`Validation Error: ${messages}`);
        } else {
             toast.error(data?.detail || 'Validation failed.');
        }
        return Promise.reject(error); // Let calling code handle specifics if needed
    }

    if (status >= 500) {
        // Server Error
        toast.error('Server error. Please try again later.');
        return Promise.reject(error);
    }

    // --- Generic Error Handling ---
    // For other 4xx errors or unexpected responses
    const message = data?.detail || error.message || `Request failed with status ${status}`;
    toast.error(message);

    return Promise.reject(error);
  }
);

export default api;
