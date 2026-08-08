import { useQuery } from "@tanstack/react-query";
import { listLeads } from "../services/search";

export interface LeadsFilters {
  segment?: string;
  city?: string;
  q?: string;
}

export function useLeads(jobId: string | null, filters: LeadsFilters = {}, enabled = true) {
  return useQuery({
    queryKey: [
      "leads",
      jobId,
      filters.segment ?? "",
      filters.city ?? "",
      filters.q ?? "",
    ],
    queryFn: () => listLeads({ job_id: jobId ?? undefined, ...filters }),
    enabled: jobId !== null && enabled,
  });
}
