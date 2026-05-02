import apiClient from './client';

import type { Invitation } from './invitations';

export interface Workspace {
  id: number;
  name: string;
  description: string;
  creator: number;
  created_at: string;
}

export interface WorkspaceMember {
  id: number;
  user_id: number;
  username: string;
  email: string;
  role: 'admin' | 'member';
  joined_at: string;
}

export interface WorkspaceDetail extends Workspace {
  channels: Channel[];
  members: WorkspaceMember[];
}

export interface Channel {
  id: number;
  workspace: number;
  name: string;
  channel_type: 'public' | 'private' | 'direct';
  creator: number;
  created_at: string;
  other_user?: {
    id: number;
    username: string;
    email: string;
  };
}

export interface CreateWorkspaceData {
  name: string;
  description: string;
}

export interface CreateChannelData {
  name: string;
  channel_type: 'public' | 'private' | 'direct';
}

export const workspacesAPI = {
  getWorkspaces: async (): Promise<Workspace[]> => {
    const response = await apiClient.get('/api/workspaces/');
    return response.data;
  },

  createWorkspace: async (data: CreateWorkspaceData): Promise<Workspace> => {
    const response = await apiClient.post('/api/workspaces/', data);
    return response.data;
  },

  getWorkspaceDetail: async (workspaceId: number): Promise<WorkspaceDetail> => {
    const response = await apiClient.get(`/api/workspaces/${workspaceId}/`);
    return response.data;
  },

  createChannel: async (workspaceId: number, data: CreateChannelData): Promise<Channel> => {
    const response = await apiClient.post(`/api/workspaces/${workspaceId}/channels/`, data);
    return response.data;
  },

  inviteUser: async (workspaceId: number, inviteeEmail: string): Promise<void> => {
    await apiClient.post(`/api/workspaces/${workspaceId}/invite/`, {
      invitee_email: inviteeEmail,
    });
  },

  updateMemberRole: async (workspaceId: number, userId: number, role: 'admin' | 'member'): Promise<WorkspaceMember> => {
    const response = await apiClient.patch(`/api/workspaces/${workspaceId}/members/${userId}/role/`, { role });
    return response.data;
  },

  removeMember: async (workspaceId: number, userId: number): Promise<void> => {
    await apiClient.delete(`/api/workspaces/${workspaceId}/members/${userId}/`);
  },

  getWorkspaceSentInvitations: async (workspaceId: number): Promise<Invitation[]> => {
    const response = await apiClient.get(`/api/workspaces/${workspaceId}/invitations/`);
    return response.data;
  },
};
