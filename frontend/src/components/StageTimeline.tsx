import { Check, Loader2, X } from "lucide-react";
import type { JobStage, JobStatusValue } from "../types/api";

type StageKey = "parsing" | "searching" | "crawling" | "extracting" | "validating" | "synthesizing";

interface StageStep {
  key: StageKey;
  label: string;
}

const STAGES: StageStep[] = [
  { key: "parsing", label: "Entendendo consulta" },
  { key: "searching", label: "Buscando empresas" },
  { key: "crawling", label: "Coletando sites" },
  { key: "extracting", label: "Extraindo contatos" },
  { key: "validating", label: "Validando dados" },
  { key: "synthesizing", label: "Gerando resumo" },
];

interface StageTimelineProps {
  stage: JobStage;
  status: JobStatusValue;
}

export default function StageTimeline({ stage, status }: StageTimelineProps) {
  const activeIndex =
    stage === "done" || stage === null
      ? STAGES.length
      : Math.max(0, STAGES.findIndex((step) => step.key === stage));

  const isFailed = status === "failed";

  return (
    <ol className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
      {STAGES.map((step, index) => {
        const isFailedStep = isFailed && index === activeIndex;
        const isComplete = !isFailedStep && (index < activeIndex || isFailed);
        const isActive = !isFailed && index === activeIndex;

        const dotClass = isComplete
          ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-300"
          : isActive
            ? "border-cyan-400/60 bg-cyan-400/15 text-cyan-300"
            : isFailedStep
              ? "border-rose-500/40 bg-rose-500/15 text-rose-300"
              : "border-slate-700 bg-slate-800/60 text-slate-500";

        return (
          <li
            key={step.key}
            className={`rounded-2xl border p-4 transition ${
              isComplete
                ? "border-emerald-500/20"
                : isActive
                  ? "border-cyan-400/40"
                  : isFailedStep
                    ? "border-rose-500/30"
                    : "border-slate-800"
            } ${isActive ? "bg-cyan-400/5" : ""}`}
          >
            <div className={`flex h-10 w-10 items-center justify-center rounded-full border ${dotClass}`}>
              {isComplete ? (
                <Check className="h-5 w-5" />
              ) : isActive ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : isFailedStep ? (
                <X className="h-5 w-5" />
              ) : (
                <span className="text-sm font-bold">{index + 1}</span>
              )}
            </div>
            <p
              className={`mt-3 text-sm font-semibold ${
                isActive ? "text-cyan-300" : isComplete ? "text-emerald-300/90" : "text-slate-500"
              }`}
            >
              {step.label}
            </p>
          </li>
        );
      })}
    </ol>
  );
}
