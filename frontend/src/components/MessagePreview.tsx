import { MessageSquare, User } from "lucide-react";
import type { OutreachChannel, OutreachRecipient } from "../types/api";

interface MessagePreviewProps {
  channel: OutreachChannel;
  recipients: OutreachRecipient[];
}

export default function MessagePreview({ channel, recipients }: MessagePreviewProps) {
  const channelLabel = channel === "email" ? "E-mail" : "WhatsApp";

  if (recipients.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center text-sm text-slate-500">
        Nenhuma mensagem gerada ainda. Ajuste o template e gere a prévia.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="flex items-center gap-2 text-sm font-semibold text-slate-400">
        <MessageSquare className="h-4 w-4 text-cyan-400" />
        Prévia — {recipients.length} mensagem(ns) via {channelLabel}
      </p>

      {recipients.map((recipient) => (
        <div
          key={recipient.lead_id}
          className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
        >
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-300">
              <User className="h-3.5 w-3.5" />
              {recipient.name}
            </span>
            <span className="text-xs text-slate-500">{recipient.contact}</span>
          </div>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
            {recipient.message}
          </p>
        </div>
      ))}
    </div>
  );
}
