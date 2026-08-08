import { FlaskConical, List, Search } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { useNavigation } from "../store/navigation";
import type { View } from "../store/navigation";

interface AppLayoutProps {
  children: ReactNode;
}

const NAV_ITEMS: { view: View; label: string; icon: LucideIcon }[] = [
  { view: "new", label: "Nova busca", icon: Search },
  { view: "leads", label: "Resultados", icon: List },
];

export default function AppLayout({ children }: AppLayoutProps) {
  const view = useNavigation((state) => state.view);
  const navigate = useNavigation((state) => state.navigate);

  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-20 border-b border-slate-800 bg-slate-900/70 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4">
          <button
            type="button"
            onClick={() => navigate("new")}
            className="flex items-center gap-2 text-xl font-black tracking-wide"
          >
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-400">
              <FlaskConical className="h-5 w-5" />
            </span>
            scrap<span className="text-cyan-400">AI</span>
          </button>

          <nav className="flex items-center gap-1 rounded-2xl border border-slate-800 bg-slate-950/60 p-1">
            {NAV_ITEMS.map(({ view: itemView, label, icon: Icon }) => {
              const active = view === itemView;

              return (
                <button
                  key={itemView}
                  type="button"
                  onClick={() => navigate(itemView)}
                  className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition ${
                    active
                      ? "bg-cyan-400/10 text-cyan-300"
                      : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-10">{children}</main>

      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-600">
        scrapAI — busca e enriquecimento automático de leads
      </footer>
    </div>
  );
}
