import { useQuery } from "@tanstack/react-query";
import { getJob } from "../services/search";

export function useJob(jobId: string | null) {
  const query = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => {
      if (!jobId) {
        throw new Error("Nenhum job selecionado.");
      }
      return getJob(jobId);
    },
    enabled: jobId !== null,
    refetchInterval: (q) => {
      const job = q.state.data;
      return job && (job.status === "queued" || job.status === "running") ? 1500 : false;
    },
  });

  const data = query.data;
  const isRunning = data?.status === "queued" || data?.status === "running";
  const stage = data?.stage ?? null;
  const progress = data?.progress ?? 0;

  return { ...query, isRunning, stage, progress };
}
