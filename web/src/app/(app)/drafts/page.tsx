import Link from "next/link";
import { ChevronLeft, ChevronRight, ChevronRight as ArrowRight, Mail, Search, Shuffle } from "lucide-react";
import {
  DRAFTS_PAGE_SIZE,
  getDrafts,
  getDraftsCountByStatus,
} from "@/lib/queries";
import { getActiveCampaign, campaignLabel } from "@/lib/campaign";
import { fmtInt } from "@/lib/labels";
import { viewRandomDraftAction } from "@/lib/actions";
import { Badge, PageHeader } from "@/components/ui";
import { BulkApproveButton } from "@/components/bulk-approve-button";

export const dynamic = "force-dynamic";

type SP = {
  status?: string;
  country?: string;
  segment?: string;
  q?: string;
  page?: string;
};

const STATUS_LABEL: Record<string, string> = {
  draft: "Brouillon",
  approved: "Approuvé",
  rejected: "Rejeté",
  sent: "Envoyé",
  bounced: "Bounce",
};

const STATUS_TONE: Record<
  string,
  "slate" | "green" | "amber" | "red" | "blue" | "violet"
> = {
  draft: "slate",
  approved: "green",
  rejected: "red",
  sent: "blue",
  bounced: "amber",
};

const SEGMENT_LABEL: Record<string, string> = {
  A_decision_maker: "Décideur",
  B_generic_inbox: "Générique",
};

const FLAG: Record<string, string> = {
  US: "🇺🇸",
  GB: "🇬🇧",
  AU: "🇦🇺",
};

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function DraftsListPage({
  searchParams,
}: {
  searchParams: Promise<SP>;
}) {
  const sp = await searchParams;
  const page = Math.max(1, Number(sp.page) || 1);
  const activeCampaign = await getActiveCampaign();

  const [{ rows, total }, byStatus] = await Promise.all([
    getDrafts(
      {
        status: sp.status,
        country: sp.country,
        segment: sp.segment,
        q: sp.q,
        page,
      },
      activeCampaign
    ),
    getDraftsCountByStatus(activeCampaign),
  ]);

  const totalPages = Math.max(1, Math.ceil(total / DRAFTS_PAGE_SIZE));
  const from = total === 0 ? 0 : (page - 1) * DRAFTS_PAGE_SIZE + 1;
  const to = Math.min(page * DRAFTS_PAGE_SIZE, total);

  function pageHref(p: number) {
    const params = new URLSearchParams();
    for (const [k, v] of Object.entries(sp))
      if (v && k !== "page") params.set(k, v);
    params.set("page", String(p));
    return `/drafts?${params.toString()}`;
  }

  function filterHref(key: string, value: string) {
    const params = new URLSearchParams();
    for (const [k, v] of Object.entries(sp))
      if (v && k !== "page" && k !== key) params.set(k, v);
    if (value) params.set(key, value);
    return `/drafts?${params.toString()}`;
  }

  const grandTotal = Object.values(byStatus).reduce((a, b) => a + b, 0);
  const draftFilterActive = sp.status === "draft";
  const draftsMatchingFilters = total; // total renvoyé par getDrafts pour les filtres courants

  return (
    <div className="space-y-6">
      <PageHeader
        title="Emails personnalisés"
        subtitle={`Campagne : ${campaignLabel(activeCampaign)} — ${fmtInt(grandTotal)} drafts générés via Claude Haiku 4.5.`}
      />

      {/* Stats par statut */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        {["draft", "approved", "rejected", "sent", "bounced"].map((s) => (
          <Link
            key={s}
            href={filterHref("status", sp.status === s ? "" : s)}
            className={`rounded-xl border bg-white px-4 py-3 shadow-sm transition hover:bg-slate-50 ${
              sp.status === s ? "border-brand-500 ring-2 ring-brand-500/20" : "border-slate-200"
            }`}
          >
            <div className="text-xs font-medium text-slate-500">
              {STATUS_LABEL[s]}
            </div>
            <div className="mt-1 text-2xl font-semibold tnum text-slate-900">
              {fmtInt(byStatus[s] ?? 0)}
            </div>
          </Link>
        ))}
      </div>

      {/* Panneau QA + Bulk Approve — visible uniquement quand status=draft est filtré */}
      {draftFilterActive && draftsMatchingFilters > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h2 className="text-sm font-semibold text-amber-900">
                Validation par échantillonnage
              </h2>
              <p className="mt-1 text-xs text-amber-800 max-w-2xl">
                Avant d'approuver en masse, ouvre une vingtaine de drafts au
                hasard pour vérifier la qualité (catégorie cohérente, ton OK,
                aucun nom inventé). Si moins de 2 % sont à rejeter, le
                bulk-approve est sûr — la validation Haiku post-génération a
                déjà filtré les hallucinations.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <form action={viewRandomDraftAction}>
                <input type="hidden" name="campaign" value={activeCampaign} />
                <input type="hidden" name="status" value="draft" />
                <input type="hidden" name="country" value={sp.country ?? ""} />
                <input type="hidden" name="segment" value={sp.segment ?? ""} />
                <button
                  type="submit"
                  className="inline-flex items-center gap-1.5 rounded-lg border border-amber-300 bg-white px-3 py-2 text-sm font-medium text-amber-900 shadow-sm hover:bg-amber-100"
                >
                  <Shuffle className="h-4 w-4" />
                  Ouvrir 1 draft au hasard
                </button>
              </form>
              <BulkApproveButton
                campaign={activeCampaign}
                country={sp.country ?? ""}
                segment={sp.segment ?? ""}
                count={draftsMatchingFilters}
              />
            </div>
          </div>
        </div>
      )}

      {/* Filtres rapides */}
      <div className="flex flex-wrap items-center gap-2">
        <form
          action="/drafts"
          className="relative"
        >
          <input type="hidden" name="status" value={sp.status ?? ""} />
          <input type="hidden" name="country" value={sp.country ?? ""} />
          <input type="hidden" name="segment" value={sp.segment ?? ""} />
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            name="q"
            defaultValue={sp.q ?? ""}
            placeholder="Sujet ou email…"
            className="w-64 rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm shadow-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
          />
        </form>

        {/* Country pills */}
        <div className="flex items-center gap-1">
          {["", "US", "GB", "AU"].map((c) => (
            <Link
              key={c || "all"}
              href={filterHref("country", c)}
              className={`rounded-md px-2.5 py-1.5 text-xs font-medium transition ${
                (sp.country ?? "") === c
                  ? "bg-brand-100 text-brand-800"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {c ? `${FLAG[c]} ${c}` : "Tous pays"}
            </Link>
          ))}
        </div>

        {/* Segment pills */}
        <div className="flex items-center gap-1">
          {[
            { key: "", label: "Tous segments" },
            { key: "A_decision_maker", label: "Décideurs" },
            { key: "B_generic_inbox", label: "Génériques" },
          ].map((s) => (
            <Link
              key={s.key || "all-seg"}
              href={filterHref("segment", s.key)}
              className={`rounded-md px-2.5 py-1.5 text-xs font-medium transition ${
                (sp.segment ?? "") === s.key
                  ? "bg-brand-100 text-brand-800"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {s.label}
            </Link>
          ))}
        </div>

        {(sp.status || sp.country || sp.segment || sp.q) && (
          <Link
            href="/drafts"
            className="rounded-md px-2.5 py-1.5 text-xs font-medium text-slate-500 hover:bg-slate-100 hover:text-slate-900"
          >
            Réinitialiser
          </Link>
        )}
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                <th className="px-4 py-3">Pays</th>
                <th className="px-4 py-3">Segment</th>
                <th className="px-4 py-3">Établissement</th>
                <th className="px-4 py-3">Destinataire</th>
                <th className="px-4 py-3">Sujet</th>
                <th className="px-4 py-3">Statut</th>
                <th className="px-4 py-3">Généré</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((r) => {
                const c = r.establishments?.country ?? "??";
                return (
                  <tr key={r.id} className="hover:bg-slate-50/70">
                    <td className="px-4 py-3 text-base">{FLAG[c] ?? c}</td>
                    <td className="px-4 py-3">
                      <Badge tone={r.segment === "A_decision_maker" ? "violet" : "blue"}>
                        {SEGMENT_LABEL[r.segment]}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-900">
                        {r.establishments?.name ?? "—"}
                      </div>
                      {r.establishments?.city && (
                        <div className="text-xs text-slate-400">
                          {r.establishments.city}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="break-all text-xs text-slate-500">
                        {r.recipient_email}
                      </span>
                    </td>
                    <td className="max-w-md px-4 py-3">
                      <span className="text-slate-700">{r.subject}</span>
                    </td>
                    <td className="px-4 py-3">
                      <Badge tone={STATUS_TONE[r.status]}>
                        {STATUS_LABEL[r.status]}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500 tnum">
                      {fmtDate(r.generated_at)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        href={`/drafts/${r.id}`}
                        className="inline-flex items-center gap-1 rounded-md bg-brand-50 px-2.5 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-100"
                      >
                        Voir
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Link>
                    </td>
                  </tr>
                );
              })}
              {rows.length === 0 && (
                <tr>
                  <td
                    colSpan={8}
                    className="px-4 py-12 text-center text-slate-400"
                  >
                    <Mail className="mx-auto mb-3 h-8 w-8 text-slate-300" />
                    Aucun draft ne correspond à ces filtres.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {total > DRAFTS_PAGE_SIZE && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-500 tnum">
            {from}–{to} sur {fmtInt(total)}
          </p>
          <div className="flex items-center gap-1">
            {page > 1 ? (
              <Link
                href={pageHref(page - 1)}
                className="flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm hover:bg-slate-50"
              >
                <ChevronLeft className="h-4 w-4" />
                Précédent
              </Link>
            ) : (
              <span className="flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-300">
                <ChevronLeft className="h-4 w-4" />
                Précédent
              </span>
            )}
            <span className="px-2 text-sm text-slate-500 tnum">
              Page {page} / {totalPages}
            </span>
            {page < totalPages ? (
              <Link
                href={pageHref(page + 1)}
                className="flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm hover:bg-slate-50"
              >
                Suivant
                <ChevronRight className="h-4 w-4" />
              </Link>
            ) : (
              <span className="flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-300">
                Suivant
                <ChevronRight className="h-4 w-4" />
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
