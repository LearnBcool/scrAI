import type { JobStatusValue } from "../types/api";

interface JobProgressProps {
  progress: number;
  message: string | null;
  status?: JobStatusValue;
}

export default function JobProgress({ progress, message, status }: JobProgressProps) {
  const percent = Math.round(Math.max(0, Math.min(1, progress)) * 100);
  const isFailed = status === "failed";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="mb-3 flex items-center justify-between gap-4">
        <span className="text-sm font-medium text-slate-400">Progresso da busca</span>
        <span
          className={`text-3xl font-black ${isFailed ? "text-rose-400" : "text-cyan-400"}`}
        >
          {percent}%
        </span>
      </div>

      <div className="h-3 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isFailed ? "bg-rose-500" : "bg-cyan-400"
          }`}
          style={{ width: `${percent}%` }}
        />
      </div>

      {message && <p className="mt-4 text-sm text-slate-400">{message}</p>}
    </div>
  );
}
