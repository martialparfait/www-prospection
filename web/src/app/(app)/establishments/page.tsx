import Link from "next/link";
import { ChevronLeft, ChevronRight, Globe } from "lucide-react";
import {
  getCategoryFacets,
  getEstablishments,
  getStateFacets,
  PAGE_SIZE,
} from "@/lib/queries";
import { getActiveCampaign } from "@/lib/campaign";
import { cleanUrl, fmtInt } from "@/lib/labels";
import {
  CategoryBadge,
  EmailStatusBadge,
  EnrichmentBadge,
  PageHeader,
  Rating,
} from "@/components/ui";
import type { ContactLite } from "@/lib/types";
import { Filters } from "./filters";

export const dynamic = "force-dynamic";

const EMAIL_RANK: Record<string, number> = {
  valid: 5,
  catch_all: 4,
  risky: 3,
  unknown: 2,
  invalid: 1,
};

function bestContact(contacts: ContactLite[]): ContactLite | null {
  if (!contacts?.length) return null;
  return [...contacts].sort(
    (a, b) =>
      (EMAIL_RANK[b.email_status] ?? 0) - (EMAIL_RANK[a.email_status] ?? 0)
  )[0];
}

type SP = {
  q?: string;
  category?: string;
  state?: string;
  status?: string;
  sort?: string;
  page?: string;
};

export default async function EstablishmentsPage({
  searchParams,
}: {
  searchParams: Promise<SP>;
}) {
  const sp = await searchParams;
  const page = Math.max(1, Number(sp.page) || 1);
  const activeCampaign = await getActiveCampaign();

  const [{ rows, total }, categories, states] = await Promise.all([
    getEstablishments(
      {
        q: sp.q,
        category: sp.category,
        state: sp.state,
        status: sp.status,
        sort: sp.sort,
        page,
      },
      activeCampaign
    ),
    getCategoryFacets(activeCampaign),
    getStateFacets(activeCampaign),
  ]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const from = total === 0 ? 0 : (page - 1) * PAGE_SIZE + 1;
  const to = Math.min(page * PAGE_SIZE, total);

  function pageHref(p: number) {
    const params = new URLSearchParams();
    for (const [k, v] of Object.entries(sp)) if (v && k !== "page") params.set(k, v);
    params.set("page", String(p));
    return `/establishments?${params.toString()}`;
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Établissements"
        subtitle={`${fmtInt(total)} résultat${total > 1 ? "s" : ""} — données Google Maps enrichies.`}
      />

      <Filters categories={categories} states={states} />

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                <th className="px-4 py-3">Établissement</th>
                <th className="px-4 py-3">Catégorie</th>
                <th className="px-4 py-3">Localisation</th>
                <th className="px-4 py-3">Note</th>
                <th className="px-4 py-3">Contacts</th>
                <th className="px-4 py-3">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((e) => {
                const best = bestContact(e.contacts);
                return (
                  <tr key={e.id} className="hover:bg-slate-50/70">
                    <td className="px-4 py-3">
                      <Link
                        href={`/establishments/${e.id}`}
                        className="font-medium text-slate-900 hover:text-brand-700"
                      >
                        {e.name}
                      </Link>
                      {e.website && (
                        <a
                          href={e.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-0.5 flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600"
                        >
                          <Globe className="h-3 w-3" />
                          {cleanUrl(e.website)}
                        </a>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <CategoryBadge value={e.category} />
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {e.city ? (
                        <>
                          {e.city}
                          {e.state && (
                            <span className="text-slate-400">, {e.state}</span>
                          )}
                        </>
                      ) : (
                        e.state ?? "—"
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <Rating value={e.rating} count={e.review_count} />
                    </td>
                    <td className="px-4 py-3">
                      {e.contacts.length > 0 ? (
                        <div className="flex items-center gap-2">
                          <span className="text-slate-700 tnum">
                            {e.contacts.length}
                          </span>
                          {best && (
                            <EmailStatusBadge value={best.email_status} />
                          )}
                        </div>
                      ) : e.generic_email ? (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-500">
                            Générique
                          </span>
                          {e.generic_email_status && (
                            <EmailStatusBadge value={e.generic_email_status} />
                          )}
                        </div>
                      ) : (
                        <span className="text-slate-300">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <EnrichmentBadge value={e.enrichment_status} />
                    </td>
                  </tr>
                );
              })}
              {rows.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-12 text-center text-slate-400"
                  >
                    Aucun établissement ne correspond à ces filtres.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
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
    </div>
  );
}
