import { useEffect, useState } from "react";
import {
  AlertTriangle,
  Loader2,
  Search,
  SearchX,
  Sparkles,
  Users,
} from "lucide-react";
import { useNavigation } from "../store/navigation";
import { useJob } from "../hooks/useJob";
import { useLeads } from "../hooks/useLeads";
import type { LeadsFilters } from "../hooks/useLeads";
import { useOutreachStore } from "../store/outreach";
import LeadCard from "../components/LeadCard";
import EmptyState from "../components/EmptyState";
import type { OutreachChannel } from "../types/api";

const inputClass =
  "w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-cyan-400";

export default function LeadsPage() {
  const jobId = useNavigation((state) => state.jobId);
  const navigate = useNavigation((state) => state.navigate);

  const { data: job } = useJob(jobId);

  const [segment, setSegment] = useState("");
  const [city, setCity] = useState("");
  const [q, setQ] = useState("");
  const [filters, setFilters] = useState<LeadsFilters>({});

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      setFilters({
        segment: segment.trim() || undefined,
        city: city.trim() || undefined,
        q: q.trim() || undefined,
      });
    }, 350);
    return () => window.clearTimeout(timeout);
  }, [segment, city, q]);

  const jobDone =
    job?.status === "completed" || job?.status === "partial" || job?.status === "failed";

  const leadsQuery = useLeads(jobId, filters, jobDone);

  const { selectLeads, setChannel } = useOutreachStore();

  const openOutreach = (leadId: string, channel: OutreachChannel) => {
    selectLeads([leadId]);
    setChannel(channel);
    navigate("outreach");
  };

  const selectAll = () => {
    if (!leadsQuery.data) return;
    selectLeads(leadsQuery.data.leads.map((lead) => lead.id));
    setChannel("email");
    navigate("outreach");
  };

  if (!jobId) {
    return (
      <EmptyState
        icon={SearchX}
        title="Nenhuma busca realizada"
        message="Inicie uma nova busca para visualizar os leads encontrados."
        actionLabel="Nova busca"
        onAction={() => navigate("new")}
      />
    );
  }

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black">Leads encontrados</h1>
          <p className="mt-1 text-slate-400">
            {job ? `Busca: "${job.query}"` : "Resultados da sua busca."}
          </p>
        </div>

        {leadsQuery.data && leadsQuery.data.leads.length > 0 && (
          <button
            type="button"
            onClick={selectAll}
            className="inline-flex items-center gap-2 rounded-xl border border-cyan-400/40 bg-cyan-400/10 px-4 py-2.5 text-sm font-semibold text-cyan-300 transition hover:bg-cyan-400/20"
          >
            <Users className="h-4 w-4" />
            Selecionar todos ({leadsQuery.data.leads.length})
          </button>
        )}
      </div>

      {job?.status === "failed" && job.error && (
        <div className="mb-6 flex items-start gap-3 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
          <div>
            <p className="font-bold">A busca falhou durante a execução</p>
            <p className="mt-1">{job.error}</p>
          </div>
        </div>
      )}

      {job && !jobDone && (
        <div className="mb-6 flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-900 p-5 text-slate-300">
          <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
          A busca ainda está em andamento.
          <button
            type="button"
            onClick={() => navigate("progress")}
            className="font-semibold text-cyan-300 hover:underline"
          >
            Acompanhar progresso
          </button>
        </div>
      )}

      {leadsQuery.data?.summary && (
        <div className="mb-6 rounded-2xl border border-cyan-500/20 bg-gradient-to-br from-cyan-500/10 to-slate-900 p-6">
          <p className="mb-2 flex items-center gap-2 text-sm font-semibold text-cyan-300">
            <Sparkles className="h-4 w-4" />
            Resumo gerado pela IA
          </p>
          <p className="text-sm leading-relaxed text-slate-300">{leadsQuery.data.summary}</p>
        </div>
      )}

      {leadsQuery.data && leadsQuery.data.rejected > 0 && (
        <div className="mb-6 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-300">
          {leadsQuery.data.rejected} leads foram rejeitados durante a validação.
        </div>
      )}

      <div className="mb-6 grid gap-4 rounded-2xl border border-slate-800 bg-slate-900 p-5 md:grid-cols-3">
        <label className="block">
          <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">
            Segmento
          </span>
          <input
            type="text"
            value={segment}
            onChange={(event) => setSegment(event.target.value)}
            placeholder="Filtrar por segmento"
            className={inputClass}
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">
            Cidade
          </span>
          <input
            type="text"
            value={city}
            onChange={(event) => setCity(event.target.value)}
            placeholder="Filtrar por cidade"
            className={inputClass}
          />
        </label>

        <label className="block">
          <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-500">
            Busca
          </span>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={q}
              onChange={(event) => setQ(event.target.value)}
              placeholder="Nome, e-mail, site..."
              className={`${inputClass} pl-9`}
            />
          </div>
        </label>
      </div>

      {jobDone && leadsQuery.isPending && (
        <div className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-900 p-6 text-slate-400">
          <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
          Carregando leads...
        </div>
      )}

      {jobDone && leadsQuery.isError && (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-sm text-rose-300">
          {leadsQuery.error instanceof Error
            ? leadsQuery.error.message
            : "Não foi possível carregar os leads."}
        </div>
      )}

      {leadsQuery.data && leadsQuery.data.leads.length === 0 && !leadsQuery.isPending && (
        <EmptyState
          icon={SearchX}
          title="Nenhum lead encontrado"
          message={
            filters.segment || filters.city || filters.q
              ? "Ajuste os filtros ou refine a busca para encontrar novos leads."
              : "Tente uma nova busca com termos mais amplos."
          }
          actionLabel="Nova busca"
          onAction={() => navigate("new")}
        />
      )}

      {leadsQuery.data && leadsQuery.data.leads.length > 0 && (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {leadsQuery.data.leads.map((lead) => (
            <LeadCard
              key={lead.id}
              lead={lead}
              onEmail={(item) => openOutreach(item.id, "email")}
              onWhatsapp={(item) => openOutreach(item.id, "whatsapp")}
            />
          ))}
        </div>
      )}
    </div>
  );
}
