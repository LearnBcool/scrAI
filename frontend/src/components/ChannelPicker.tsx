import { Mail, MessageCircle } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { OutreachChannel } from "../types/api";

interface ChannelPickerProps {
  value: OutreachChannel;
  onChange: (channel: OutreachChannel) => void;
}

const CHANNELS: { key: OutreachChannel; label: string; icon: LucideIcon }[] = [
  { key: "email", label: "E-mail", icon: Mail },
  { key: "whatsapp", label: "WhatsApp", icon: MessageCircle },
];

export default function ChannelPicker({ value, onChange }: ChannelPickerProps) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {CHANNELS.map(({ key, label, icon: Icon }) => {
        const selected = value === key;

        return (
          <button
            key={key}
            type="button"
            onClick={() => onChange(key)}
            className={`flex items-center justify-center gap-2 rounded-xl border px-4 py-3 font-semibold transition ${
              selected
                ? "border-cyan-400/60 bg-cyan-400/10 text-cyan-300"
                : "border-slate-700 bg-slate-800/40 text-slate-400 hover:border-slate-500 hover:text-slate-200"
            }`}
          >
            <Icon className="h-5 w-5" />
            {label}
          </button>
        );
      })}
    </div>
  );
}
