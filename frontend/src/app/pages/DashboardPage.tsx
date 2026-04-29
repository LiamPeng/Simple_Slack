import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AppLayout } from '../components/AppLayout';
import { workspacesAPI, Workspace } from '../api/workspaces';
import { invitationsAPI, Invitation } from '../api/invitations';
import { Plus, Users, Calendar, Bell } from 'lucide-react';

export function DashboardPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [workspacesData, invitationsData] = await Promise.all([
        workspacesAPI.getWorkspaces(),
        invitationsAPI.getInvitations(),
      ]);
      setWorkspaces(workspacesData);
      setInvitations(invitationsData.filter(inv => inv.status === 'pending'));
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full bg-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="h-full overflow-y-auto bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {invitations.length > 0 && (
          <div className="mb-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Bell className="h-5 w-5 text-blue-600" />
              <h3 className="font-semibold text-blue-900">Pending Invitations</h3>
            </div>
            <p className="text-sm text-blue-700">
              You have {invitations.length} pending invitation{invitations.length !== 1 ? 's' : ''}.{' '}
              <Link to="/invitations" className="underline font-medium">
                View all
              </Link>
            </p>
          </div>
        )}

        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Your Workspaces</h1>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <Plus className="h-5 w-5" />
            <span>Create Workspace</span>
          </button>
        </div>

        {workspaces.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No workspaces yet</h3>
            <p className="text-gray-600 mb-4">Create your first workspace to get started</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Create Workspace
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {workspaces.map((workspace) => (
              <Link
                key={workspace.id}
                to={`/workspaces/${workspace.id}`}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{workspace.name}</h3>
                <p className="text-gray-600 text-sm mb-4 line-clamp-2">{workspace.description}</p>
                <div className="flex items-center text-xs text-gray-500">
                  <Calendar className="h-4 w-4 mr-1" />
                  Created {new Date(workspace.created_at).toLocaleDateString()}
                </div>
              </Link>
            ))}
          </div>
        )}
        </div>

        {showCreateModal && (
          <CreateWorkspaceModal
            onClose={() => setShowCreateModal(false)}
            onCreated={loadData}
          />
        )}
      </div>
    </AppLayout>
  );
}

function CreateWorkspaceModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await workspacesAPI.createWorkspace({ name, description });
      onCreated();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create workspace');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Create Workspace</h2>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Workspace Name
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
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
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
