import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;

function clearAuthAndRedirect(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
    window.location.href = '/login';
  }
}

async function refreshAccessToken(): Promise<string> {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    throw new Error('Missing refresh token');
  }

  const refreshResponse = await refreshClient.post<{ access: string; refresh?: string }>(
    '/api/auth/refresh/',
    { refresh: refreshToken },
  );

  localStorage.setItem('access_token', refreshResponse.data.access);
  if (refreshResponse.data.refresh) {
    localStorage.setItem('refresh_token', refreshResponse.data.refresh);
  }

  return refreshResponse.data.access;
}

apiClient.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem('access_token');
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

  if (csrfToken && config.method !== 'get') {
    config.headers['X-CSRFToken'] = csrfToken;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;
    const requestUrl = String(originalRequest?.url || '');
    const shouldSkipRefresh =
      requestUrl.includes('/api/auth/login/') ||
      requestUrl.includes('/api/auth/register/') ||
      requestUrl.includes('/api/auth/refresh/');

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !shouldSkipRefresh) {
      originalRequest._retry = true;

      if (!localStorage.getItem('refresh_token')) {
        clearAuthAndRedirect();
        return Promise.reject(error);
      }

      try {
        let newAccessToken: string;
        if (isRefreshing && refreshPromise) {
          newAccessToken = await refreshPromise;
        } else {
          isRefreshing = true;
          refreshPromise = refreshAccessToken().finally(() => {
            isRefreshing = false;
            refreshPromise = null;
          });
          newAccessToken = await refreshPromise;
        }

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        clearAuthAndRedirect();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
