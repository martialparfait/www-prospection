import "server-only";
import { supabase } from "./supabase";
import type {
  Contact,
  Establishment,
  EstablishmentWithContacts,
} from "./types";

// --------------------------------------------------------------------------
// Dashboard
// --------------------------------------------------------------------------

export type DashboardStats = {
  estabTotal: number;
  estabWithWebsite: number;
  estabWithGenericEmail: number;
  /** Établissements sans email perso mais avec un email générique. */
  genericOnlyTotal: number;
  /** Idem, dont email générique vérifié `valid`. */
  genericOnlyValid: number;
  byCategory: { key: string; count: number }[];
  byEnrichment: { key: string; count: number }[];
  matrix: { category: string; counts: Record<string, number>; total: number }[];
  topStates: { key: string; count: number }[];
  contactsTotal: number;
  byEmailStatus: { key: string; count: number }[];
  bySource: { key: string; count: number }[];
  contactsWithName: number;
  mailableTotal: number;
  mailableBySegment: { key: string; count: number }[];
};

const ENRICHMENT_ORDER = [
  "enriched",
  "crawled",
  "pending",
  "no_email",
  "no_website",
  "failed",
];
const EMAIL_ORDER = ["valid", "catch_all", "risky", "invalid", "unknown"];

function tally(rows: { key: string | null }[]): { key: string; count: number }[] {
  const m = new Map<string, number>();
  for (const r of rows) {
    const k = r.key ?? "—";
    m.set(k, (m.get(k) ?? 0) + 1);
  }
  return [...m.entries()].map(([key, count]) => ({ key, count }));
}

function ordered(
  arr: { key: string; count: number }[],
  order: string[]
): { key: string; count: number }[] {
  return [...arr].sort((a, b) => {
    const ia = order.indexOf(a.key);
    const ib = order.indexOf(b.key);
    if (ia === -1 && ib === -1) return b.count - a.count;
    if (ia === -1) return 1;
    if (ib === -1) return -1;
    return ia - ib;
  });
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const [estabRes, contactsRes, mailableRes] = await Promise.all([
    supabase
      .from("establishments")
      .select(
        "category,enrichment_status,state,website,generic_email,generic_email_status"
      ),
    supabase
      .from("contacts")
      .select("email_status,source_provider,full_name"),
    // La vue contacts_mailable expose une colonne `segment`
    // (A_decision_maker = décideurs nominatifs, B_generic_inbox = boîtes génériques de secours).
    supabase.from("contacts_mailable").select("segment"),
  ]);

  if (estabRes.error) throw estabRes.error;
  if (contactsRes.error) throw contactsRes.error;
  if (mailableRes.error) throw mailableRes.error;

  const estab = estabRes.data as {
    category: string;
    enrichment_status: string;
    state: string | null;
    website: string | null;
    generic_email: string | null;
    generic_email_status: string | null;
  }[];
  const contacts = contactsRes.data as {
    email_status: string;
    source_provider: string | null;
    full_name: string | null;
  }[];

  // Matrice catégorie × statut d'enrichissement
  const matrixMap = new Map<string, Record<string, number>>();
  for (const e of estab) {
    const row = matrixMap.get(e.category) ?? {};
    row[e.enrichment_status] = (row[e.enrichment_status] ?? 0) + 1;
    matrixMap.set(e.category, row);
  }
  const matrix = [...matrixMap.entries()]
    .map(([category, counts]) => ({
      category,
      counts,
      total: Object.values(counts).reduce((a, b) => a + b, 0),
    }))
    .sort((a, b) => b.total - a.total);

  const topStates = tally(
    estab.filter((e) => e.state).map((e) => ({ key: e.state }))
  )
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  return {
    estabTotal: estab.length,
    estabWithWebsite: estab.filter((e) => e.website).length,
    estabWithGenericEmail: estab.filter((e) => e.generic_email).length,
    genericOnlyTotal: estab.filter(
      (e) => e.enrichment_status === "no_email" && e.generic_email
    ).length,
    genericOnlyValid: estab.filter(
      (e) =>
        e.enrichment_status === "no_email" &&
        e.generic_email_status === "valid"
    ).length,
    byCategory: tally(estab.map((e) => ({ key: e.category }))).sort(
      (a, b) => b.count - a.count
    ),
    byEnrichment: ordered(
      tally(estab.map((e) => ({ key: e.enrichment_status }))),
      ENRICHMENT_ORDER
    ),
    matrix,
    topStates,
    contactsTotal: contacts.length,
    byEmailStatus: ordered(
      tally(contacts.map((c) => ({ key: c.email_status }))),
      EMAIL_ORDER
    ),
    bySource: tally(contacts.map((c) => ({ key: c.source_provider }))).sort(
      (a, b) => b.count - a.count
    ),
    contactsWithName: contacts.filter((c) => c.full_name).length,
    mailableTotal: mailableRes.data?.length ?? 0,
    mailableBySegment: tally(
      (mailableRes.data ?? []).map((r) => ({ key: (r as { segment: string }).segment }))
    ).sort((a, b) => a.key.localeCompare(b.key)),
  };
}

// --------------------------------------------------------------------------
// Liste établissements (filtres serveur + pagination)
// --------------------------------------------------------------------------

export const PAGE_SIZE = 25;

export type EstabFilters = {
  q?: string;
  category?: string;
  state?: string;
  status?: string; // enrichment_status
  sort?: string; // name | rating | reviews | recent
  page?: number;
};

const LIST_COLUMNS =
  "id,name,category,city,state,rating,review_count,website,phone,generic_email,generic_email_status,enrichment_status,contacts(email_status,nominative_email,full_name,role,source_provider)";

export async function getEstablishments(
  f: EstabFilters
): Promise<{ rows: EstablishmentWithContacts[]; total: number; page: number }> {
  const page = Math.max(1, f.page ?? 1);
  let query = supabase
    .from("establishments")
    .select(LIST_COLUMNS, { count: "exact" });

  if (f.q) query = query.ilike("name", `%${f.q}%`);
  if (f.category) query = query.eq("category", f.category);
  if (f.state) query = query.eq("state", f.state);
  if (f.status) query = query.eq("enrichment_status", f.status);

  switch (f.sort) {
    case "rating":
      query = query.order("rating", { ascending: false, nullsFirst: false });
      break;
    case "reviews":
      query = query.order("review_count", {
        ascending: false,
        nullsFirst: false,
      });
      break;
    case "recent":
      query = query.order("created_at", { ascending: false });
      break;
    default:
      query = query.order("name", { ascending: true });
  }

  const from = (page - 1) * PAGE_SIZE;
  query = query.range(from, from + PAGE_SIZE - 1);

  const { data, error, count } = await query;
  if (error) throw error;

  return {
    rows: (data ?? []) as unknown as EstablishmentWithContacts[],
    total: count ?? 0,
    page,
  };
}

/** Liste distincte des états (pour le filtre), triée par fréquence. */
export async function getStateFacets(): Promise<string[]> {
  const { data, error } = await supabase
    .from("establishments")
    .select("state");
  if (error) throw error;
  const counts = new Map<string, number>();
  for (const r of data as { state: string | null }[]) {
    if (r.state) counts.set(r.state, (counts.get(r.state) ?? 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([s]) => s);
}

export async function getCategoryFacets(): Promise<string[]> {
  const { data, error } = await supabase
    .from("establishments")
    .select("category");
  if (error) throw error;
  return [...new Set((data as { category: string }[]).map((r) => r.category))].sort();
}

// --------------------------------------------------------------------------
// Détail établissement
// --------------------------------------------------------------------------

export async function getEstablishment(
  id: string
): Promise<{ estab: Establishment; contacts: Contact[] } | null> {
  const [estabRes, contactsRes] = await Promise.all([
    supabase.from("establishments").select("*").eq("id", id).maybeSingle(),
    supabase
      .from("contacts")
      .select("*")
      .eq("establishment_id", id)
      .order("created_at"),
  ]);
  if (estabRes.error) throw estabRes.error;
  if (!estabRes.data) return null;
  if (contactsRes.error) throw contactsRes.error;
  return {
    estab: estabRes.data as Establishment,
    contacts: (contactsRes.data ?? []) as Contact[],
  };
}
