import apiClient from './client';
import { Message } from './channels';

export interface SearchResult extends Message {
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
