import { ReactNode, useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { workspacesAPI, WorkspaceDetail } from '../api/workspaces';
import { MessageSquare, Search, Bell } from 'lucide-react';

interface WorkspaceLayoutProps {
  children: ReactNode;
  currentChannelId?: string;
}

export function WorkspaceLayout({ children, currentChannelId }: WorkspaceLayoutProps) {
  const { workspaceId, channelId } = useParams();
  const [workspace, setWorkspace] = useState<WorkspaceDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWorkspace();
  }, [workspaceId, channelId]);

  const loadWorkspace = async () => {
    try {
      let wId = workspaceId ? Number(workspaceId) : null;

      if (!wId && channelId) {
        const channelIdNum = Number(channelId);
        const workspaces = await workspacesAPI.getWorkspaces();

        for (const ws of workspaces) {
          const detail = await workspacesAPI.getWorkspaceDetail(ws.id);
          const hasChannel = detail.channels.some(c => c.id === channelIdNum);
          if (hasChannel) {
            wId = ws.id;
            break;
          }
        }
      }

      if (wId) {
        const data = await workspacesAPI.getWorkspaceDetail(wId);
        setWorkspace(data);
      }
    } catch (error) {
      console.error('Error loading workspace:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen bg-gray-100">
        <div className="w-60 bg-gray-900"></div>
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-100">
      <Sidebar workspace={workspace} currentChannelId={currentChannelId || channelId} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navigation */}
        <div className="bg-white border-b border-gray-200 px-4 h-14 flex items-center justify-between flex-shrink-0">
          <Link to="/dashboard" className="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
            <MessageSquare className="h-5 w-5" />
            <span className="font-semibold">WorkspaceChat</span>
          </Link>

          <div className="flex items-center space-x-2">
            <Link
              to="/search"
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
            >
              <Search className="h-5 w-5" />
            </Link>

            <Link
              to="/invitations"
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
            >
              <Bell className="h-5 w-5" />
            </Link>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden">
          {children}
        </div>
      </div>
    </div>
  );
}
