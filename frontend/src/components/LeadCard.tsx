import { useState } from "react";
import {
  Check,
  Copy,
  ExternalLink,
  Globe,
  Link2,
  Mail,
  MessageCircle,
  Phone,
  User,
} from "lucide-react";
import type { Lead } from "../types/api";
import { confidencePercent, formatEmail, formatPhone } from "../utils/format";

interface LeadCardProps {
  lead: Lead;
  onEmail?: (lead: Lead) => void;
  onWhatsapp?: (lead: Lead) => void;
}

interface CopyButtonProps {
  value: string;
  label: string;
}

function CopyButton({ value, label }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard indisponível
    }
  };

  return (
    <button
      type="button"
      onClick={handleCopy}
      title={`Copiar ${label}`}
      aria-label={`Copiar ${label}`}
      className="ml-1 inline-flex shrink-0 items-center rounded-md p-1 text-slate-500 transition hover:bg-slate-800 hover:text-cyan-300"
    >
      {copied ? (
        <Check className="h-3.5 w-3.5 text-emerald-400" />
      ) : (
        <Copy className="h-3.5 w-3.5" />
      )}
    </button>
  );
}

export default function LeadCard({ lead, onEmail, onWhatsapp }: LeadCardProps) {
  const percent = confidencePercent(lead.confidence);

  const confidenceClass =
    lead.confidence < 0.5
      ? "border-amber-500/30 bg-amber-500/10 text-amber-300"
      : lead.confidence < 0.8
        ? "border-cyan-500/30 bg-cyan-500/10 text-cyan-300"
        : "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";

  const websiteUrl = lead.website
    ? /^https?:\/\//i.test(lead.website)
      ? lead.website
      : `https://${lead.website}`
    : null;

  const chips: string[] = [];
  if (lead.segment) chips.push(lead.segment);
  if (lead.city) chips.push(lead.city);
  if (lead.state) chips.push(lead.state);

  return (
    <article className="flex flex-col rounded-2xl border border-slate-800 bg-slate-900 p-6 transition hover:border-cyan-400/40">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="flex items-center gap-2 truncate text-lg font-bold text-slate-100">
            <User className="h-4 w-4 shrink-0 text-cyan-400" />
            {lead.name}
          </h3>

          {chips.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {chips.map((chip) => (
                <span
                  key={chip}
                  className="rounded-full border border-slate-700 bg-slate-800/60 px-2.5 py-0.5 text-xs text-slate-300"
                >
                  {chip}
                </span>
              ))}
            </div>
          )}
        </div>

        <span
          className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-bold ${confidenceClass}`}
        >
          {percent}% confiança
        </span>
      </div>

      <div className="space-y-2.5 text-sm">
        {lead.emails.length > 0 && (
          <div className="flex flex-wrap items-center gap-x-1 gap-y-1 text-slate-300">
            <Mail className="h-4 w-4 shrink-0 text-slate-500" />
            {lead.emails.map((email) => (
              <span key={email} className="inline-flex items-center text-cyan-300">
                {formatEmail(email)}
                <CopyButton value={email} label="e-mail" />
              </span>
            ))}
          </div>
        )}

        {lead.phones.length > 0 && (
          <div className="flex flex-wrap items-center gap-x-1 gap-y-1 text-slate-300">
            <Phone className="h-4 w-4 shrink-0 text-slate-500" />
            {lead.phones.map((phone) => (
              <span key={phone} className="inline-flex items-center">
                {formatPhone(phone)}
                <CopyButton value={phone} label="telefone" />
              </span>
            ))}
          </div>
        )}

        {lead.whatsapp.length > 0 && (
          <div className="flex flex-wrap items-center gap-x-1 gap-y-1 text-slate-300">
            <MessageCircle className="h-4 w-4 shrink-0 text-slate-500" />
            {lead.whatsapp.map((whatsapp) => (
              <span key={whatsapp} className="inline-flex items-center">
                {formatPhone(whatsapp)}
                <CopyButton value={whatsapp} label="whatsapp" />
              </span>
            ))}
          </div>
        )}
      </div>

      {(websiteUrl || lead.source_url) && (
        <div className="mt-4 space-y-1.5 border-t border-slate-800 pt-4 text-xs">
          {websiteUrl && (
            <a
              href={websiteUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-slate-400 transition hover:text-cyan-300"
            >
              <Globe className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{lead.website}</span>
              <ExternalLink className="h-3 w-3 shrink-0" />
            </a>
          )}

          {lead.source_url && (
            <a
              href={lead.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-slate-500 transition hover:text-cyan-300"
            >
              <Link2 className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">Fonte: {lead.source_url}</span>
              <ExternalLink className="h-3 w-3 shrink-0" />
            </a>
          )}
        </div>
      )}

      <div className="mt-auto flex gap-3 pt-5">
        <button
          type="button"
          disabled={lead.emails.length === 0}
          onClick={() => onEmail?.(lead)}
          className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-cyan-400/40 bg-cyan-400/10 px-3 py-2.5 text-sm font-semibold text-cyan-300 transition hover:bg-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Mail className="h-4 w-4" />
          Enviar e-mail
        </button>

        <button
          type="button"
          disabled={lead.whatsapp.length === 0}
          onClick={() => onWhatsapp?.(lead)}
          className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-3 py-2.5 text-sm font-semibold text-emerald-300 transition hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <MessageCircle className="h-4 w-4" />
          WhatsApp
        </button>
      </div>
    </article>
  );
}
