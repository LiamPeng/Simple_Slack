import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { AppLayout } from '../components/AppLayout';
import { workspacesAPI, WorkspaceDetail, CreateChannelData } from '../api/workspaces';
import { Plus, Hash, Lock, Users, UserPlus, Shield, Settings } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function WorkspaceDetailPage() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const { user } = useAuth();
  const [workspace, setWorkspace] = useState<WorkspaceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [showInviteUser, setShowInviteUser] = useState(false);

  useEffect(() => {
    loadWorkspace();
  }, [workspaceId]);

  const loadWorkspace = async () => {
    try {
      const data = await workspacesAPI.getWorkspaceDetail(Number(workspaceId));
      setWorkspace(data);
    } catch (error) {
      console.error('Error loading workspace:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </AppLayout>
    );
  }

  if (!workspace) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <p className="text-gray-600">Workspace not found</p>
        </div>
      </AppLayout>
    );
  }

  const currentMembership = workspace.members.find((member) => member.user_id === user?.id);
  const isCurrentUserAdmin = currentMembership?.role === 'admin';

  const handlePromoteDemote = async (userId: number, role: 'admin' | 'member') => {
    try {
      await workspacesAPI.updateMemberRole(workspace.id, userId, role);
      await loadWorkspace();
    } catch (error) {
      console.error('Failed to update role:', error);
    }
  };

  const handleRemoveMember = async (userId: number) => {
    try {
      await workspacesAPI.removeMember(workspace.id, userId);
      await loadWorkspace();
    } catch (error) {
      console.error('Failed to remove member:', error);
    }
  };

  return (
    <AppLayout>
      <div className="h-full overflow-y-auto bg-white">
        {/* Workspace Header */}
        <div className="border-b border-gray-200 px-6 py-4">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">{workspace.name}</h1>
                <button className="p-1.5 hover:bg-gray-100 rounded">
                  <Settings className="h-4 w-4 text-gray-600" />
                </button>
              </div>
              <p className="text-gray-600 text-sm">{workspace.description}</p>
              <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                <div className="flex items-center">
                  <Users className="h-3.5 w-3.5 mr-1" />
                  {workspace.members.length} members
                </div>
                <div className="flex items-center">
                  <Hash className="h-3.5 w-3.5 mr-1" />
                  {workspace.channels.length} channels
                </div>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowInviteUser(true)}
                className="flex items-center space-x-2 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <UserPlus className="h-4 w-4" />
                <span>Invite</span>
              </button>
              <button
                onClick={() => setShowCreateChannel(true)}
                className="flex items-center space-x-2 px-3 py-2 text-sm border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                <Plus className="h-4 w-4" />
                <span>New Channel</span>
              </button>
            </div>
          </div>
        </div>

        {/* Members List */}
        <div className="px-6 py-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Workspace Members</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workspace.members.map((member) => (
              <div key={member.id} className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                <div className="w-10 h-10 rounded bg-blue-600 flex items-center justify-center text-white font-semibold flex-shrink-0">
                  {member.username.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <p className="font-medium text-gray-900 truncate">{member.username}</p>
                    {member.role === 'admin' && (
                      <Shield className="h-3.5 w-3.5 text-blue-600 flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-xs text-gray-500 truncate">{member.email}</p>
                </div>
                {isCurrentUserAdmin && member.user_id !== user?.id && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() =>
                        handlePromoteDemote(member.user_id, member.role === 'admin' ? 'member' : 'admin')
                      }
                      className="text-xs px-2 py-1 rounded border border-gray-300 hover:bg-gray-100"
                    >
                      {member.role === 'admin' ? 'Demote' : 'Promote'}
                    </button>
                    <button
                      onClick={() => handleRemoveMember(member.user_id)}
                      className="text-xs px-2 py-1 rounded border border-red-200 text-red-600 hover:bg-red-50"
                    >
                      Remove
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {showCreateChannel && (
        <CreateChannelModal
          workspaceId={Number(workspaceId)}
          onClose={() => setShowCreateChannel(false)}
          onCreated={loadWorkspace}
        />
      )}

      {showInviteUser && (
        <InviteUserModal
          workspaceId={Number(workspaceId)}
          onClose={() => setShowInviteUser(false)}
        />
      )}
    </AppLayout>
  );
}

function CreateChannelModal({
  workspaceId,
  onClose,
  onCreated,
}: {
  workspaceId: number;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [name, setName] = useState('');
  const [channelType, setChannelType] = useState<'public' | 'private'>('public');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data: CreateChannelData = { name, channel_type: channelType };
      await workspacesAPI.createChannel(workspaceId, data);
      onCreated();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create channel');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Create Channel</h2>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Channel Name
              </label>
              <input
                id="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Channel Type</label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="channelType"
                    value="public"
                    checked={channelType === 'public'}
                    onChange={(e) => setChannelType(e.target.value as 'public')}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Public - Anyone in workspace can view</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="channelType"
                    value="private"
                    checked={channelType === 'private'}
                    onChange={(e) => setChannelType(e.target.value as 'private')}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Private - Only invited members can view</span>
                </label>
              </div>
            </div>
          </div>

          <div className="mt-6 flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function InviteUserModal({ workspaceId, onClose }: { workspaceId: number; onClose: () => void }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      await workspacesAPI.inviteUser(workspaceId, email);
      setSuccess(true);
      setEmail('');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to send invitation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Invite User to Workspace</h2>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
            Invitation sent successfully!
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter email to invite"
            />
          </div>

          <div className="mt-6 flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Close
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Invitation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
