import { create } from "zustand";
import type { OutreachChannel } from "../types/api";

interface OutreachState {
  leadIds: string[];
  channel: OutreachChannel;
  selectLeads: (leadIds: string[]) => void;
  setChannel: (channel: OutreachChannel) => void;
  clear: () => void;
}

export const useOutreachStore = create<OutreachState>()((set) => ({
  leadIds: [],
  channel: "email",
  selectLeads: (leadIds) => set({ leadIds }),
  setChannel: (channel) => set({ channel }),
  clear: () => set({ leadIds: [], channel: "email" }),
}));
