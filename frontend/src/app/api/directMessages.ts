import apiClient from './client';
import type { Channel } from './workspaces';

export interface DirectChannelUser {
  id: number;
  username: string;
  email: string;
}

export const directMessagesAPI = {
  createDirectChannel: async (workspaceId: number, otherUserId: number): Promise<Channel> => {
    const response = await apiClient.post(`/api/workspaces/${workspaceId}/direct-channels/`, {
      other_user_id: otherUserId,
    });
    return response.data;
  },

  getOrCreateDirectChannel: async (workspaceId: number, otherUserId: number): Promise<Channel> => {
    const response = await apiClient.post(`/api/workspaces/${workspaceId}/direct-channels/get-or-create/`, {
      other_user_id: otherUserId,
    });
    return response.data;
  },
};
