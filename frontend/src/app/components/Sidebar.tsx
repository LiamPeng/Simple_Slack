import { Link, useParams, useNavigate } from 'react-router-dom';
import { Hash, Lock, Plus, ChevronDown, ChevronRight, Users, Settings, LogOut, MessageCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useState, useMemo, useEffect } from 'react';
import { WorkspaceSwitcher } from './WorkspaceSwitcher';
import { StartDirectMessageModal } from './StartDirectMessageModal';
import { getApiErrorMessage } from '../api/client';
import { workspacesAPI, CreateChannelData } from '../api/workspaces';
import type { WorkspaceDetail } from '../api/workspaces';

interface SidebarProps {
  workspace: WorkspaceDetail | null;
  currentChannelId?: string;
}

export function Sidebar({ workspace, currentChannelId }: SidebarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showWorkspaceSwitcher, setShowWorkspaceSwitcher] = useState(false);
  const [showStartDM, setShowStartDM] = useState(false);
  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [showCreatePrivateChannel, setShowCreatePrivateChannel] = useState(false);

  // Collapsible sections state - load from localStorage
  const [sectionsCollapsed, setSectionsCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebar-sections-collapsed');
    return saved ? JSON.parse(saved) : { channels: false, privateChannels: false, directMessages: false };
  });

  // Save to localStorage when state changes
  useEffect(() => {
    localStorage.setItem('sidebar-sections-collapsed', JSON.stringify(sectionsCollapsed));
  }, [sectionsCollapsed]);

  const toggleSection = (section: 'channels' | 'privateChannels' | 'directMessages') => {
    setSectionsCollapsed((prev: any) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const publicChannels = workspace?.channels.filter(c => c.channel_type === 'public') || [];
  const privateChannels = workspace?.channels.filter(c => c.channel_type === 'private') || [];
  const directChannels = workspace?.channels.filter(c => c.channel_type === 'direct') || [];
  const renderUnreadBadge = (count: number) =>
    count > 0 ? (
      <span className="ml-auto min-w-[1.125rem] h-[1.125rem] px-1 flex items-center justify-center rounded-full bg-red-600 text-white text-[10px] font-semibold leading-none">
        {count > 99 ? '99+' : count}
      </span>
    ) : null;

  return (
    <div className="w-60 bg-gray-900 text-gray-100 flex flex-col h-screen">
      {/* Workspace Header */}
      <div className="px-4 py-3 border-b border-gray-800">
        <button
          onClick={() => setShowWorkspaceSwitcher(true)}
          className="w-full flex items-center justify-between hover:bg-gray-800 px-3 py-2 rounded"
        >
          <span className="font-bold text-white truncate">
            {workspace?.name || 'Select Workspace'}
          </span>
          <ChevronDown className="h-4 w-4 text-gray-400 flex-shrink-0" />
        </button>
      </div>

      {/* Channels Section */}
      <div className="flex-1 overflow-y-auto">
        {workspace && (
          <>
            {/* Public Channels */}
            <div className="px-2 py-3">
              <div className="w-full flex items-center justify-between px-3 py-1 text-gray-400 hover:text-gray-200 text-sm group">
                <button
                  onClick={() => toggleSection('channels')}
                  className="flex items-center space-x-1 flex-1"
                >
                  {sectionsCollapsed.channels ? (
                    <ChevronRight className="h-3 w-3" />
                  ) : (
                    <ChevronDown className="h-3 w-3" />
                  )}
                  <span className="font-semibold">Channels</span>
                </button>
                <button
                  onClick={() => setShowCreateChannel(true)}
                  className="opacity-0 group-hover:opacity-100 hover:text-white"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>

              {!sectionsCollapsed.channels && (
                <div className="mt-1 space-y-0.5">
                  {publicChannels.map((channel) => (
                    <Link
                      key={channel.id}
                      to={`/channels/${channel.id}`}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm ${
                        currentChannelId === String(channel.id)
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                      }`}
                    >
                      <Hash className="h-4 w-4 flex-shrink-0" />
                      <span className="truncate">{channel.name}</span>
                      {renderUnreadBadge(channel.unread_count ?? 0)}
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Private Channels */}
            <div className="px-2 py-3 border-t border-gray-800">
              <div className="w-full flex items-center justify-between px-3 py-1 text-gray-400 hover:text-gray-200 text-sm group">
                <button
                  onClick={() => toggleSection('privateChannels')}
                  className="flex items-center space-x-1 flex-1"
                >
                  {sectionsCollapsed.privateChannels ? (
                    <ChevronRight className="h-3 w-3" />
                  ) : (
                    <ChevronDown className="h-3 w-3" />
                  )}
                  <span className="font-semibold">Private Channels</span>
                </button>
                <button
                  onClick={() => setShowCreatePrivateChannel(true)}
                  className="opacity-0 group-hover:opacity-100 hover:text-white"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>

              {!sectionsCollapsed.privateChannels && privateChannels.length > 0 && (
                <div className="mt-1 space-y-0.5">
                  {privateChannels.map((channel) => (
                    <Link
                      key={channel.id}
                      to={`/channels/${channel.id}`}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm ${
                        currentChannelId === String(channel.id)
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                      }`}
                    >
                      <Lock className="h-4 w-4 flex-shrink-0" />
                      <span className="truncate">{channel.name}</span>
                      {renderUnreadBadge(channel.unread_count ?? 0)}
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Direct Messages Section */}
            <div className="px-2 py-3 border-t border-gray-800">
              <div className="w-full flex items-center justify-between px-3 py-1 text-gray-400 hover:text-gray-200 text-sm group">
                <button
                  onClick={() => toggleSection('directMessages')}
                  className="flex items-center space-x-1 flex-1"
                >
                  {sectionsCollapsed.directMessages ? (
                    <ChevronRight className="h-3 w-3" />
                  ) : (
                    <ChevronDown className="h-3 w-3" />
                  )}
                  <span className="font-semibold">Direct Messages</span>
                </button>
                <button
                  onClick={() => setShowStartDM(true)}
                  className="opacity-0 group-hover:opacity-100 hover:text-white"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>

              {!sectionsCollapsed.directMessages && (
                <div className="mt-1 space-y-0.5">
                  {directChannels.map((channel) => {
                    const displayName = channel.other_user?.username || 'Unknown';

                    return (
                      <Link
                        key={channel.id}
                        to={`/channels/${channel.id}`}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm ${
                          currentChannelId === String(channel.id)
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                        }`}
                      >
                        <div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
                          {displayName.charAt(0).toUpperCase()}
                        </div>
                        <span className="truncate">{displayName}</span>
                        {renderUnreadBadge(channel.unread_count ?? 0)}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Members Section */}
            <div className="px-2 py-3 border-t border-gray-800">
              <Link
                to={`/workspaces/${workspace.id}`}
                className="w-full flex items-center justify-between px-3 py-1 text-gray-400 hover:text-gray-200 text-sm"
              >
                <span className="flex items-center space-x-1">
                  <Users className="h-3 w-3" />
                  <span className="font-semibold">Members</span>
                </span>
                <span className="text-xs">{workspace.members.length}</span>
              </Link>
            </div>
          </>
        )}
      </div>

      {/* User Info Footer */}
      <div className="border-t border-gray-800 p-2 relative">
        <button
          onClick={() => setShowUserMenu(!showUserMenu)}
          className="w-full flex items-center space-x-2 px-2 py-2 hover:bg-gray-800 rounded"
        >
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white font-semibold flex-shrink-0">
            {user?.username.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 text-left min-w-0">
            <div className="text-sm font-medium text-white truncate">{user?.username}</div>
            <div className="text-xs text-gray-400 truncate">{user?.email}</div>
          </div>
          <Settings className="h-4 w-4 text-gray-400 flex-shrink-0" />
        </button>

        {showUserMenu && (
          <div className="absolute bottom-full left-2 right-2 mb-2 bg-gray-800 rounded shadow-lg border border-gray-700 py-1">
            <button
              onClick={handleLogout}
              className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white"
            >
              <LogOut className="h-4 w-4" />
              <span>Log out</span>
            </button>
          </div>
        )}
      </div>

      {showWorkspaceSwitcher && (
        <WorkspaceSwitcher
          currentWorkspaceId={workspace?.id}
          onClose={() => setShowWorkspaceSwitcher(false)}
        />
      )}

      {showStartDM && workspace && (
        <StartDirectMessageModal
          workspaceId={workspace.id}
          members={workspace.members}
          onClose={() => setShowStartDM(false)}
        />
      )}

      {showCreateChannel && workspace && (
        <CreateChannelModal
          workspaceId={workspace.id}
          channelType="public"
          onClose={() => setShowCreateChannel(false)}
        />
      )}

      {showCreatePrivateChannel && workspace && (
        <CreateChannelModal
          workspaceId={workspace.id}
          channelType="private"
          onClose={() => setShowCreatePrivateChannel(false)}
        />
      )}
    </div>
  );
}

interface CreateChannelModalProps {
  workspaceId: number;
  channelType: 'public' | 'private';
  onClose: () => void;
}

function CreateChannelModal({ workspaceId, channelType, onClose }: CreateChannelModalProps) {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data: CreateChannelData = { name, channel_type: channelType };
      const channel = await workspacesAPI.createChannel(workspaceId, data);
      navigate(`/channels/${channel.id}`);
      onClose();
      // Reload the page to refresh sidebar
      window.location.reload();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, 'Failed to create channel'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="bg-white rounded-lg max-w-md w-full p-6" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Create {channelType === 'public' ? 'Public' : 'Private'} Channel
        </h2>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Channel Name
            </label>
            <input
              id="name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. announcements"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500">
              {channelType === 'public'
                ? 'Anyone in the workspace can view and join this channel.'
                : 'Only invited members can view this channel.'}
            </p>
          </div>

          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim()}
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
