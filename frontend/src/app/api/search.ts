import apiClient from './client';

/** Matches GET /api/search/ payload (flat channel + names for UI). */
export interface SearchResult {
  id: number;
  body: string;
  created_at: string;
  sender: { id: number; username: string };
  channel: number;
  channel_name: string;
  workspace_name: string;
}

export const searchAPI = {
  searchMessages: async (query: string): Promise<SearchResult[]> => {
    const response = await apiClient.get('/api/search/', {
      params: { q: query },
    });
    return response.data;
  },
};
