import { createContext, useContext, type ReactNode } from 'react';

const WorkspaceSidebarRefreshContext = createContext<() => void>(() => {});

export function WorkspaceSidebarRefreshProvider({
  children,
  refresh,
}: {
  children: ReactNode;
  refresh: () => void;
}) {
  return (
    <WorkspaceSidebarRefreshContext.Provider value={refresh}>
      {children}
    </WorkspaceSidebarRefreshContext.Provider>
  );
}

export function useWorkspaceSidebarRefresh() {
  return useContext(WorkspaceSidebarRefreshContext);
}
