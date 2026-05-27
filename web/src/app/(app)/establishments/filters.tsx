"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useTransition } from "react";
import { Search, X } from "lucide-react";
import { categoryLabel, enrichmentLabel } from "@/lib/labels";

const SORTS = [
  { value: "name", label: "Nom (A→Z)" },
  { value: "rating", label: "Note (haute→basse)" },
  { value: "reviews", label: "Avis (nombreux→peu)" },
  { value: "recent", label: "Ajout récent" },
];

const STATUSES = [
  "enriched",
  "crawled",
  "pending",
  "no_email",
  "no_website",
  "failed",
];

export function Filters({
  categories,
  states,
}: {
  categories: string[];
  states: string[];
}) {
  const router = useRouter();
  const sp = useSearchParams();
  const [pending, startTransition] = useTransition();
  const [q, setQ] = useState(sp.get("q") ?? "");

  function apply(next: Record<string, string | undefined>) {
    const params = new URLSearchParams(sp.toString());
    for (const [k, v] of Object.entries(next)) {
      if (v) params.set(k, v);
      else params.delete(k);
    }
    params.delete("page"); // tout changement de filtre revient page 1
    startTransition(() => router.push(`/establishments?${params.toString()}`));
  }

  const selectClass =
    "rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20";

  const hasFilters =
    sp.get("q") || sp.get("category") || sp.get("state") || sp.get("status");

  return (
    <div className="flex flex-wrap items-center gap-2">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          apply({ q });
        }}
        className="relative"
      >
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Rechercher un nom…"
          className="w-56 rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm shadow-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
        />
      </form>

      <select
        value={sp.get("category") ?? ""}
        onChange={(e) => apply({ category: e.target.value })}
        className={selectClass}
      >
        <option value="">Toutes catégories</option>
        {categories.map((c) => (
          <option key={c} value={c}>
            {categoryLabel(c)}
          </option>
        ))}
      </select>

      <select
        value={sp.get("state") ?? ""}
        onChange={(e) => apply({ state: e.target.value })}
        className={selectClass}
      >
        <option value="">Tous les États</option>
        {states.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>

      <select
        value={sp.get("status") ?? ""}
        onChange={(e) => apply({ status: e.target.value })}
        className={selectClass}
      >
        <option value="">Tous statuts</option>
        {STATUSES.map((s) => (
          <option key={s} value={s}>
            {enrichmentLabel(s)}
          </option>
        ))}
      </select>

      <select
        value={sp.get("sort") ?? "name"}
        onChange={(e) => apply({ sort: e.target.value })}
        className={selectClass}
      >
        {SORTS.map((s) => (
          <option key={s.value} value={s.value}>
            {s.label}
          </option>
        ))}
      </select>

      {hasFilters && (
        <button
          onClick={() => {
            setQ("");
            startTransition(() => router.push("/establishments"));
          }}
          className="flex items-center gap-1 rounded-lg px-2.5 py-2 text-sm text-slate-500 hover:bg-slate-100 hover:text-slate-900"
        >
          <X className="h-4 w-4" />
          Réinitialiser
        </button>
      )}

      {pending && <span className="text-xs text-slate-400">…</span>}
    </div>
  );
}
