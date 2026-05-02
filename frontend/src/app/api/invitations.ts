import apiClient from './client';

export interface Invitation {
  id: number;
  inviter: number;
  inviter_username: string;
  invitee: number | null;
  invitee_email: string;
  workspace: number;
  workspace_name: string;
  channel: number | null;
  status: 'pending' | 'accepted' | 'declined';
  created_at: string;
  responded_at: string | null;
  last_notified_at: string | null;
  notification_count: number;
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

  cancelInvitation: async (invitationId: number): Promise<void> => {
    await apiClient.post(`/api/invitations/${invitationId}/cancel/`);
  },

  resendInvitation: async (invitationId: number): Promise<Invitation> => {
    const response = await apiClient.post(`/api/invitations/${invitationId}/resend/`);
    return response.data;
  },
};
