import apiClient from './client';

export interface Message {
  id: number;
  channel: number;
  sender: {
    id: number;
    username: string;
  };
  content: string;
  created_at: string;
  updated_at: string;
}

export interface ChannelMember {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
  };
  joined_at: string;
}

export interface ChannelDetail {
  id: number;
  workspace: number;
  name: string;
  channel_type: 'public' | 'private' | 'direct';
  creator: number;
  created_at: string;
  members: ChannelMember[];
  other_user?: {
    id: number;
    username: string;
    email: string;
  };
}

export interface CreateMessageData {
  content: string;
}

export const channelsAPI = {
  getChannelDetail: async (channelId: number): Promise<ChannelDetail> => {
    const response = await apiClient.get(`/api/channels/${channelId}/`);
    return response.data;
  },

  getMessages: async (channelId: number): Promise<Message[]> => {
    const response = await apiClient.get(`/api/channels/${channelId}/messages/`);
    return response.data;
  },

  createMessage: async (channelId: number, data: CreateMessageData): Promise<Message> => {
    const response = await apiClient.post(`/api/channels/${channelId}/messages/`, data);
    return response.data;
  },
};
