import apiClient from './client';

export interface Message {
  id: number;
  channel: number;
  sender: {
    id: number;
    username: string;
  };
  body: string;
  created_at: string;
}

/** Matches ChannelMembershipSerializer from GET /api/channels/:id/ */
export interface ChannelMember {
  id: number;
  user_id: number;
  username: string;
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
  messages: Message[];
  other_user?: {
    id: number;
    username: string;
    email: string;
  };
}

export interface CreateMessageData {
  body: string;
}

export const channelsAPI = {
  getChannelDetail: async (channelId: number): Promise<ChannelDetail> => {
    const response = await apiClient.get(`/api/channels/${channelId}/`);
    return response.data;
  },

  createMessage: async (channelId: number, data: CreateMessageData): Promise<Message> => {
    const response = await apiClient.post(`/api/channels/${channelId}/messages/`, data);
    return response.data;
  },
};
