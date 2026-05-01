import apiClient from './client';

export interface User {
  id: number;
  user_id: number;
  username: string;
  email: string;
  nickname: string;
  created_at: string;
}

export interface RegisterData {
  username: string;
  email: string;
  nickname?: string;
  password: string;
  passwordConfirm: string;
}

export interface LoginData {
  username: string;
  password: string;
}

interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}

function persistTokens(access: string, refresh: string): void {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

export const authAPI = {
  register: async (data: RegisterData): Promise<User> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/register/', {
      username: data.username,
      email: data.email,
      nickname: data.nickname ?? '',
      password: data.password,
    });
    persistTokens(response.data.access, response.data.refresh);
    return response.data.user;
  },

  login: async (data: LoginData): Promise<User> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/login/', data);
    persistTokens(response.data.access, response.data.refresh);
    return response.data.user;
  },

  logout: async (): Promise<void> => {
    const refresh = localStorage.getItem('refresh_token');
    if (refresh) {
      await apiClient.post('/api/auth/logout/', { refresh });
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/auth/me/');
    return response.data;
  },
};
