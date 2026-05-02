import { ReactNode, useCallback, useEffect, useState } from 'react';
import { Link, useParams, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { useSidebar } from '../context/SidebarContext';
import { WorkspaceSidebarRefreshProvider } from '../context/WorkspaceSidebarRefreshContext';
import { invitationsAPI } from '../api/invitations';
import { workspacesAPI, WorkspaceDetail } from '../api/workspaces';
import { MessageSquare, Search, Bell, Menu, X } from 'lucide-react';

interface AppLayoutProps {
  children: ReactNode;
  showWorkspaceSidebar?: boolean;
}

export function AppLayout({ children, showWorkspaceSidebar = true }: AppLayoutProps) {
  const { isOpen, toggle } = useSidebar();
  const { workspaceId, channelId } = useParams();
  const location = useLocation();
  const [workspace, setWorkspace] = useState<WorkspaceDetail | null>(null);
  const [loading, setLoading] = useState(showWorkspaceSidebar);
  const [pendingInvitationCount, setPendingInvitationCount] = useState(0);
  const [sidebarDataVersion, setSidebarDataVersion] = useState(0);
  const refreshWorkspaceSidebar = useCallback(() => setSidebarDataVersion((v) => v + 1), []);

  const refreshInvitationCount = useCallback(async () => {
    try {
      const list = await invitationsAPI.getInvitations();
      setPendingInvitationCount(list.filter((inv) => inv.status === 'pending').length);
    } catch {
      setPendingInvitationCount(0);
    }
  }, []);

  useEffect(() => {
    void refreshInvitationCount();
  }, [location.pathname, refreshInvitationCount]);

  useEffect(() => {
    const tick = () => {
      if (document.visibilityState === 'visible') {
        void refreshInvitationCount();
      }
    };
    const id = window.setInterval(tick, 45000);
    document.addEventListener('visibilitychange', tick);
    return () => {
      window.clearInterval(id);
      document.removeEventListener('visibilitychange', tick);
    };
  }, [refreshInvitationCount]);

  useEffect(() => {
    if (showWorkspaceSidebar) {
      loadWorkspace();
    }
  }, [workspaceId, channelId, showWorkspaceSidebar, sidebarDataVersion]);

  const loadWorkspace = async () => {
    try {
      let wId = workspaceId ? Number(workspaceId) : null;

      // If we're on a channel page without workspaceId, find the workspace
      if (!wId && channelId) {
        const channelIdNum = Number(channelId);
        const workspaces = await workspacesAPI.getWorkspaces();

        for (const ws of workspaces) {
          const detail = await workspacesAPI.getWorkspaceDetail(ws.id);
          const hasChannel = detail.channels.some((c) => Number(c.id) === channelIdNum);
          if (hasChannel) {
            wId = ws.id;
            break;
          }
        }
      }

      // If we're on dashboard/search/invitations, get the first workspace
      if (!wId && ['/dashboard', '/search', '/invitations'].includes(location.pathname)) {
        const workspaces = await workspacesAPI.getWorkspaces();
        if (workspaces.length > 0) {
          wId = workspaces[0].id;
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

  return (
    <WorkspaceSidebarRefreshProvider refresh={refreshWorkspaceSidebar}>
    <div className="flex h-screen overflow-hidden bg-gray-100">
      {/* Sidebar - conditionally render based on isOpen */}
      {showWorkspaceSidebar && (
        <div
          className={`${
            isOpen ? 'w-60' : 'w-0'
          } transition-all duration-300 ease-in-out overflow-hidden flex-shrink-0`}
        >
          {loading ? (
            <div className="w-60 bg-gray-900 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            </div>
          ) : (
            <Sidebar workspace={workspace} currentChannelId={channelId} />
          )}
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navigation */}
        <div className="bg-white border-b border-gray-200 px-4 h-14 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center space-x-3">
            {showWorkspaceSidebar && (
              <button
                onClick={toggle}
                className="p-2 hover:bg-gray-100 rounded-md text-gray-600"
                title={isOpen ? 'Hide sidebar' : 'Show sidebar'}
              >
                {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            )}

            <Link to="/dashboard" className="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
              <MessageSquare className="h-5 w-5" />
              <span className="font-semibold">WorkspaceChat</span>
            </Link>
          </div>

          <div className="flex items-center space-x-2">
            <Link
              to="/search"
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
              title="Search"
            >
              <Search className="h-5 w-5" />
            </Link>

            <Link
              to="/invitations"
              className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
              title="Invitations"
            >
              <Bell className="h-5 w-5" />
              {pendingInvitationCount > 0 && (
                <span className="absolute top-0 right-0 min-w-[1.125rem] h-[1.125rem] px-1 flex items-center justify-center rounded-full bg-red-600 text-white text-[10px] font-semibold leading-none">
                  {pendingInvitationCount > 99 ? '99+' : pendingInvitationCount}
                </span>
              )}
            </Link>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden">
          {children}
        </div>
      </div>
    </div>
    </WorkspaceSidebarRefreshProvider>
  );
}
