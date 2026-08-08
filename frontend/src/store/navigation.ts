import { create } from "zustand";

export type View = "new" | "progress" | "leads" | "outreach";

interface NavigationState {
  view: View;
  jobId: string | null;
  lastQuery: string | null;
  setView: (view: View) => void;
  setJob: (jobId: string, query: string) => void;
  navigate: (view: View) => void;
}

export const useNavigation = create<NavigationState>()((set) => ({
  view: "new",
  jobId: null,
  lastQuery: null,
  setView: (view) => set({ view }),
  setJob: (jobId, query) => set({ jobId, lastQuery: query }),
  navigate: (view) => set({ view }),
}));
