import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { directMessagesAPI } from '../api/directMessages';
import { useAuth } from '../context/AuthContext';
import type { WorkspaceMember } from '../api/workspaces';

interface StartDirectMessageModalProps {
  workspaceId: number;
  members: WorkspaceMember[];
  onClose: () => void;
}

export function StartDirectMessageModal({ workspaceId, members, onClose }: StartDirectMessageModalProps) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const otherMembers = members.filter((m) => m.user_id !== user?.id);

  const handleSelectUser = async (userId: number) => {
    setError('');
    setLoading(true);

    try {
      const channel = await directMessagesAPI.getOrCreateDirectChannel(workspaceId, userId);
      navigate(`/channels/${channel.id}`);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create direct message');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="bg-white rounded-lg max-w-md w-full shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900">Start Direct Message</h2>
          <p className="text-sm text-gray-600 mt-1">Select a member to message</p>
        </div>

        {error && (
          <div className="mx-4 mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="max-h-96 overflow-y-auto p-2">
          {otherMembers.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No other members in this workspace
            </div>
          ) : (
            <div className="space-y-1">
              {otherMembers.map((member) => (
                <button
                  key={member.id}
                  onClick={() => handleSelectUser(member.user_id)}
                  disabled={loading}
                  className="w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-100 rounded-md disabled:opacity-50 disabled:cursor-not-allowed text-left"
                >
                  <div className="w-10 h-10 rounded bg-blue-600 flex items-center justify-center text-white font-semibold flex-shrink-0">
                    {member.username.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{member.username}</p>
                    <p className="text-sm text-gray-500 truncate">{member.email}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
