import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { getDashboardStats } from "@/lib/queries";
import { getActiveCampaign, campaignLabel } from "@/lib/campaign";
import {
  categoryLabel,
  emailStatusLabel,
  enrichmentLabel,
  fmtInt,
  fmtPct,
  sourceLabel,
} from "@/lib/labels";
import { Card, PageHeader, StackedBar, StatCard } from "@/components/ui";

export const dynamic = "force-dynamic";

const ENRICH_SEG: Record<string, string> = {
  enriched: "bg-emerald-500",
  crawled: "bg-sky-500",
  pending: "bg-slate-300",
  no_email: "bg-amber-400",
  no_website: "bg-slate-500",
  failed: "bg-rose-500",
};
const EMAIL_SEG: Record<string, string> = {
  valid: "bg-emerald-500",
  catch_all: "bg-amber-400",
  risky: "bg-amber-400",
  invalid: "bg-rose-500",
  unknown: "bg-slate-300",
};

function Legend({
  items,
}: {
  items: { label: string; value: number; className: string }[];
}) {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1.5">
      {items.map((it) => (
        <div key={it.label} className="flex items-center gap-1.5 text-xs">
          <span className={`h-2.5 w-2.5 rounded-sm ${it.className}`} />
          <span className="text-slate-600">{it.label}</span>
          <span className="font-semibold text-slate-900 tnum">{it.value}</span>
        </div>
      ))}
    </div>
  );
}

export default async function DashboardPage() {
  const activeCampaign = await getActiveCampaign();
  const s = await getDashboardStats(activeCampaign);

  const enrichSegments = s.byEnrichment.map((e) => ({
    label: enrichmentLabel(e.key),
    value: e.count,
    className: ENRICH_SEG[e.key] ?? "bg-slate-300",
  }));
  const emailSegments = s.byEmailStatus.map((e) => ({
    label: emailStatusLabel(e.key),
    value: e.count,
    className: EMAIL_SEG[e.key] ?? "bg-slate-300",
  }));

  const enrichedCount =
    s.byEnrichment.find((e) => e.key === "enriched")?.count ?? 0;
  const processed = s.byEnrichment
    .filter((e) => e.key !== "pending")
    .reduce((a, e) => a + e.count, 0);

  return (
    <div className="space-y-8">
      <PageHeader
        title="Tableau de bord"
        subtitle={`Campagne : ${campaignLabel(activeCampaign)} — vue d'ensemble des données collectées et de l'enrichissement.`}
      />

      {/* KPIs */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Établissements collectés"
          value={fmtInt(s.estabTotal)}
          hint={`${fmtInt(s.estabWithWebsite)} avec site web (${fmtPct(
            s.estabWithWebsite,
            s.estabTotal
          )})`}
        />
        <StatCard
          label="Enrichissement traité"
          value={fmtPct(processed, s.estabTotal)}
          hint={`${fmtInt(processed)} / ${fmtInt(s.estabTotal)} établissements`}
          accent="text-sky-700"
        />
        <Card className="p-5">
          <div className="text-sm font-medium text-slate-500">
            Contacts identifiés
          </div>
          <div className="mt-2 grid grid-cols-2 gap-3">
            <div>
              <div className="text-2xl font-semibold tnum text-violet-700">
                {fmtInt(s.contactsTotal)}
              </div>
              <div className="mt-1 text-[11px] leading-tight text-slate-500">
                Décideurs<br />nominatifs
              </div>
            </div>
            <div className="border-l border-slate-200 pl-3">
              <div className="text-2xl font-semibold tnum text-slate-700">
                {fmtInt(s.genericOnlyTotal)}
              </div>
              <div className="mt-1 text-[11px] leading-tight text-slate-500">
                Boîtes<br />génériques
              </div>
            </div>
          </div>
        </Card>
        <Card className="p-5">
          <div className="text-sm font-medium text-slate-500">
            Cibles atteignables
          </div>
          <div className="mt-2 grid grid-cols-2 gap-3">
            <div>
              <div className="text-2xl font-semibold tnum text-emerald-700">
                {fmtInt(
                  s.mailableBySegment.find((x) => x.key === "A_decision_maker")
                    ?.count ?? 0
                )}
              </div>
              <div className="mt-1 text-[11px] leading-tight text-slate-500">
                Décideurs<br />nominatifs
              </div>
            </div>
            <div className="border-l border-slate-200 pl-3">
              <div className="text-2xl font-semibold tnum text-slate-700">
                {fmtInt(
                  s.mailableBySegment.find((x) => x.key === "B_generic_inbox")
                    ?.count ?? 0
                )}
              </div>
              <div className="mt-1 text-[11px] leading-tight text-slate-500">
                Boîtes<br />génériques
              </div>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Avancement enrichissement */}
        <Card className="p-5">
          <h2 className="text-sm font-semibold text-slate-900">
            Avancement de l'enrichissement
          </h2>
          <p className="mt-0.5 text-xs text-slate-500">
            Statut des {fmtInt(s.estabTotal)} établissements.
          </p>
          <div className="mt-4">
            <StackedBar segments={enrichSegments} />
          </div>
          <div className="mt-3">
            <Legend items={enrichSegments} />
          </div>
        </Card>

        {/* Qualité des emails */}
        <Card className="p-5">
          <h2 className="text-sm font-semibold text-slate-900">
            Qualité des emails de contacts
          </h2>
          <p className="mt-0.5 text-xs text-slate-500">
            Sur {fmtInt(s.contactsTotal)} contacts identifiés.
          </p>
          {s.contactsTotal > 0 ? (
            <>
              <div className="mt-4">
                <StackedBar segments={emailSegments} />
              </div>
              <div className="mt-3">
                <Legend items={emailSegments} />
              </div>
            </>
          ) : (
            <p className="mt-6 text-sm text-slate-400">
              Aucun contact pour l'instant.
            </p>
          )}
        </Card>
      </div>

      {/* Matrice catégorie × statut */}
      <Card className="overflow-hidden">
        <div className="border-b border-slate-200 px-5 py-4">
          <h2 className="text-sm font-semibold text-slate-900">
            Répartition par catégorie
          </h2>
          <p className="mt-0.5 text-xs text-slate-500">
            Volume et avancement de l'enrichissement par vertical.
          </p>
        </div>
        <div className="divide-y divide-slate-100">
          {s.matrix.map((row) => {
            const segs = [
              "enriched",
              "crawled",
              "pending",
              "no_email",
              "no_website",
              "failed",
            ]
              .filter((k) => (row.counts[k] ?? 0) > 0)
              .map((k) => ({
                label: enrichmentLabel(k),
                value: row.counts[k] ?? 0,
                className: ENRICH_SEG[k] ?? "bg-slate-300",
              }));
            const done =
              row.total - (row.counts["pending"] ?? 0);
            return (
              <div
                key={row.category}
                className="grid grid-cols-1 items-center gap-3 px-5 py-4 sm:grid-cols-[160px_1fr_90px]"
              >
                <div className="flex items-center gap-2">
                  <Link
                    href={`/establishments?category=${row.category}`}
                    className="text-sm font-medium text-slate-900 hover:text-brand-700"
                  >
                    {categoryLabel(row.category)}
                  </Link>
                  <span className="text-xs text-slate-400 tnum">
                    {fmtInt(row.total)}
                  </span>
                </div>
                <StackedBar segments={segs} />
                <div className="text-right text-xs text-slate-500 tnum">
                  {fmtPct(done, row.total)} traité
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top états */}
        <Card className="p-5">
          <h2 className="text-sm font-semibold text-slate-900">
            Top États (USA)
          </h2>
          <div className="mt-4 space-y-2.5">
            {s.topStates.map((st) => {
              const max = s.topStates[0]?.count || 1;
              return (
                <div key={st.key} className="flex items-center gap-3">
                  <div className="w-28 shrink-0 truncate text-sm text-slate-700">
                    {st.key}
                  </div>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-brand-500"
                      style={{ width: `${(st.count / max) * 100}%` }}
                    />
                  </div>
                  <div className="w-10 shrink-0 text-right text-sm font-medium text-slate-900 tnum">
                    {st.count}
                  </div>
                </div>
              );
            })}
          </div>
        </Card>

        {/* Sources des contacts */}
        <Card className="p-5">
          <h2 className="text-sm font-semibold text-slate-900">
            Source des contacts
          </h2>
          {s.bySource.length > 0 ? (
            <div className="mt-4 space-y-2.5">
              {s.bySource.map((src) => {
                const max = s.bySource[0]?.count || 1;
                return (
                  <div key={src.key} className="flex items-center gap-3">
                    <div className="w-28 shrink-0 truncate text-sm text-slate-700">
                      {sourceLabel(src.key)}
                    </div>
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-violet-500"
                        style={{ width: `${(src.count / max) * 100}%` }}
                      />
                    </div>
                    <div className="w-10 shrink-0 text-right text-sm font-medium text-slate-900 tnum">
                      {src.count}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="mt-6 text-sm text-slate-400">
              Aucun contact pour l'instant.
            </p>
          )}
          <Link
            href="/establishments?status=enriched"
            className="mt-5 inline-flex items-center gap-1 text-sm font-medium text-brand-700 hover:text-brand-800"
          >
            Voir les établissements enrichis
            <ArrowRight className="h-4 w-4" />
          </Link>
        </Card>
      </div>

      <p className="text-xs text-slate-400">
        {enrichedCount > 0
          ? `${fmtInt(enrichedCount)} établissements entièrement enrichis.`
          : null}
      </p>
    </div>
  );
}
