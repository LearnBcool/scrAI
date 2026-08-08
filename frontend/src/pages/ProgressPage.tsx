import { useEffect } from "react";
import { ArrowLeft, Loader2, SearchX } from "lucide-react";
import { useNavigation } from "../store/navigation";
import { useJob } from "../hooks/useJob";
import JobProgress from "../components/JobProgress";
import StageTimeline from "../components/StageTimeline";
import EmptyState from "../components/EmptyState";

export default function ProgressPage() {
  const jobId = useNavigation((state) => state.jobId);
  const lastQuery = useNavigation((state) => state.lastQuery);
  const navigate = useNavigation((state) => state.navigate);

  const { data: job, isPending, isError, error, stage, progress } = useJob(jobId);

  useEffect(() => {
    if (
      job &&
      (job.status === "completed" || job.status === "partial" || job.status === "failed")
    ) {
      navigate("leads");
    }
  }, [job, navigate]);

  if (!jobId) {
    return (
      <EmptyState
        icon={SearchX}
        title="Nenhuma busca em andamento"
        message="Inicie uma nova busca para acompanhar o progresso."
        actionLabel="Nova busca"
        onAction={() => navigate("new")}
      />
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      <button
        type="button"
        onClick={() => navigate("new")}
        className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-400 transition hover:text-cyan-300"
      >
        <ArrowLeft className="h-4 w-4" />
        Voltar
      </button>

      <div className="mb-8">
        <h1 className="text-3xl font-black">Buscando leads</h1>
        <p className="mt-1 text-slate-400">
          {lastQuery ? `Consulta: "${lastQuery}"` : "Acompanhe o andamento da sua busca."}
        </p>
      </div>

      {isPending && !job && (
        <div className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-900 p-6 text-slate-400">
          <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
          Carregando status da busca...
        </div>
      )}

      {isError && !job && (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-sm text-rose-300">
          {error instanceof Error ? error.message : "Não foi possível consultar o status da busca."}
        </div>
      )}

      {job && (
        <div className="space-y-6">
          <JobProgress progress={progress} message={job.message} status={job.status} />

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="mb-5 text-sm font-semibold uppercase tracking-wider text-slate-400">
              Etapas da busca
            </h2>
            <StageTimeline stage={stage} status={job.status} />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-800 bg-slate-900 px-6 py-4 text-sm">
            <span className="text-slate-400">Leads encontrados até agora</span>
            <span className="text-xl font-black text-cyan-400">{job.lead_count}</span>
          </div>

          {job.status === "failed" && job.error && (
            <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-sm text-rose-300">
              <p className="font-bold">A busca falhou</p>
              <p className="mt-1">{job.error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
