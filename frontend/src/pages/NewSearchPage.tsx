import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { ArrowRight, Building2, Loader2, MapPin, Search, Sparkles } from "lucide-react";
import { useSearch } from "../hooks/useSearch";
import { ApiError } from "../services/client";

const searchSchema = z.object({
  query: z.string().min(3, "Descreva o que você procura (mínimo de 3 caracteres)."),
  segment: z.string().optional(),
  city: z.string().optional(),
  max_leads: z.preprocess(
    (value) => (value === "" || value === undefined || value === null ? undefined : value),
    z.coerce
      .number()
      .int("Informe um número inteiro.")
      .min(1, "Mínimo de 1 lead.")
      .max(50, "Máximo de 50 leads.")
      .optional(),
  ),
});

type SearchFormValues = z.infer<typeof searchSchema>;

const EXAMPLES = [
  "restaurantes em Curitiba",
  "advogados em Florianópolis",
  "lojas de roupa em Porto Alegre",
];

const inputClass =
  "w-full rounded-xl border border-slate-700 bg-slate-950 p-4 text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-cyan-400";

export default function NewSearchPage() {
  const search = useSearch();

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<SearchFormValues>({
    resolver: zodResolver(searchSchema),
    defaultValues: { query: "", segment: "", city: "", max_leads: 10 },
  });

  const onSubmit = (values: SearchFormValues) => {
    search.mutate({
      query: values.query.trim(),
      segment: values.segment?.trim() || undefined,
      city: values.city?.trim() || undefined,
      max_leads: values.max_leads,
    });
  };

  const applyExample = (example: string) => {
    const match = example.match(/^(.*?)\s+em\s+(.+)$/);
    if (match) {
      setValue("query", match[1].trim(), { shouldValidate: true });
      setValue("city", match[2].trim(), { shouldValidate: true });
    } else {
      setValue("query", example, { shouldValidate: true });
    }
  };

  const errorMessage =
    search.error instanceof ApiError ? search.error.detail : search.error?.message ?? null;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="text-center">
        <span className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1.5 text-sm font-semibold text-cyan-300">
          <Sparkles className="h-4 w-4" />
          Busca inteligente de leads
        </span>
        <h1 className="mt-6 text-4xl font-black leading-tight md:text-5xl">
          Encontre leads qualificados <span className="text-cyan-400">automaticamente</span>
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-slate-400">
          Descreva seu público-alvo e a scrapAI pesquisa, coleta e valida contatos de empresas em
          segundos.
        </p>
      </div>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="mt-10 rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl"
      >
        <label className="block">
          <span className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-300">
            <Search className="h-4 w-4 text-cyan-400" />
            O que você procura?
          </span>
          <input
            type="text"
            placeholder="ex.: restaurantes em Curitiba"
            {...register("query")}
            className={inputClass}
          />
          {errors.query && (
            <span className="mt-1.5 block text-sm text-rose-400">{errors.query.message}</span>
          )}
        </label>

        <div className="mt-6 grid gap-6 md:grid-cols-2">
          <label className="block">
            <span className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-300">
              <Building2 className="h-4 w-4 text-cyan-400" />
              Segmento (opcional)
            </span>
            <input
              type="text"
              placeholder="ex.: restaurantes, clínicas, e-commerce"
              {...register("segment")}
              className={inputClass}
            />
            {errors.segment && (
              <span className="mt-1.5 block text-sm text-rose-400">{errors.segment.message}</span>
            )}
          </label>

          <label className="block">
            <span className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-300">
              <MapPin className="h-4 w-4 text-cyan-400" />
              Cidade (opcional)
            </span>
            <input
              type="text"
              placeholder="ex.: Curitiba"
              {...register("city")}
              className={inputClass}
            />
            {errors.city && (
              <span className="mt-1.5 block text-sm text-rose-400">{errors.city.message}</span>
            )}
          </label>
        </div>

        <div className="mt-6">
          <label className="block">
            <span className="mb-2 block text-sm font-semibold text-slate-300">
              Quantidade máxima de leads
            </span>
            <input
              type="number"
              min={1}
              max={50}
              placeholder="Entre 1 e 50"
              {...register("max_leads")}
              className={`${inputClass} md:max-w-xs`}
            />
            {errors.max_leads && (
              <span className="mt-1.5 block text-sm text-rose-400">
                {errors.max_leads.message}
              </span>
            )}
          </label>
        </div>

        {errorMessage && (
          <div className="mt-6 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300">
            {errorMessage}
          </div>
        )}

        <button
          type="submit"
          disabled={search.isPending}
          className="mt-8 flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-500 px-8 py-4 text-base font-bold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {search.isPending ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Iniciando busca...
            </>
          ) : (
            <>
              Iniciar busca
              <ArrowRight className="h-5 w-5" />
            </>
          )}
        </button>
      </form>

      <div className="mt-8">
        <p className="mb-3 text-center text-sm text-slate-500">Ou experimente um exemplo:</p>
        <div className="flex flex-wrap justify-center gap-3">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => applyExample(example)}
              className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-400/60 hover:text-cyan-300"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
