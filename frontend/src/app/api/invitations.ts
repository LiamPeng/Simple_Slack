import apiClient from './client';

export interface Invitation {
  id: number;
  inviter: {
    id: number;
    username: string;
  };
  invitee: number;
  workspace: {
    id: number;
    name: string;
  };
  channel: number | null;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
  responded_at: string | null;
}

export const invitationsAPI = {
  getInvitations: async (): Promise<Invitation[]> => {
    const response = await apiClient.get('/api/invitations/');
    return response.data;
  },

  acceptInvitation: async (invitationId: number): Promise<void> => {
    await apiClient.post(`/api/invitations/${invitationId}/accept/`);
  },

  rejectInvitation: async (invitationId: number): Promise<void> => {
    await apiClient.post(`/api/invitations/${invitationId}/reject/`);
  },
};
