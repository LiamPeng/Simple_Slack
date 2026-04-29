import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { workspacesAPI, Workspace } from '../api/workspaces';
import { Plus, Check } from 'lucide-react';

interface WorkspaceSwitcherProps {
  currentWorkspaceId?: number;
  onClose: () => void;
}

export function WorkspaceSwitcher({ currentWorkspaceId, onClose }: WorkspaceSwitcherProps) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      const data = await workspacesAPI.getWorkspaces();
      setWorkspaces(data);
    } catch (error) {
      console.error('Error loading workspaces:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="bg-white rounded-lg max-w-md w-full shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900">Switch Workspace</h2>
        </div>

        {loading ? (
          <div className="p-8 flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="max-h-96 overflow-y-auto">
            {workspaces.map((workspace) => (
              <Link
                key={workspace.id}
                to={`/workspaces/${workspace.id}`}
                onClick={onClose}
                className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 border-b border-gray-100"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate">{workspace.name}</p>
                  <p className="text-sm text-gray-500 truncate">{workspace.description}</p>
                </div>
                {currentWorkspaceId === workspace.id && (
                  <Check className="h-5 w-5 text-blue-600 flex-shrink-0 ml-2" />
                )}
              </Link>
            ))}

            <Link
              to="/dashboard"
              onClick={onClose}
              className="flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 border-b border-gray-100 text-blue-600"
            >
              <Plus className="h-5 w-5" />
              <span className="font-medium">Create new workspace</span>
            </Link>

            <Link
              to="/dashboard"
              onClick={onClose}
              className="flex items-center px-4 py-3 hover:bg-gray-50 text-gray-700"
            >
              View all workspaces
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
