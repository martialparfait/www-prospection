import "server-only";
import { supabase } from "./supabase";
import { ACTIVE_CAMPAIGN } from "./constants";
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

/** Pagination Supabase : PostgREST plafonne à 1000 lignes/requête → on boucle. */
async function fetchAllPaginated<T>(
  build: () => ReturnType<typeof supabase.from>,
  select: string,
  applyFilters: (q: ReturnType<ReturnType<typeof supabase.from>["select"]>) => ReturnType<ReturnType<typeof supabase.from>["select"]>
): Promise<T[]> {
  const PAGE = 1000;
  const out: T[] = [];
  let offset = 0;
  // We rebuild the query each iteration to ensure clean range.
  while (true) {
    const base = build().select(select) as unknown as ReturnType<ReturnType<typeof supabase.from>["select"]>;
    const filtered = applyFilters(base);
    const { data, error } = await (filtered as unknown as { range: (a: number, b: number) => unknown })
      .range(offset, offset + PAGE - 1) as unknown as { data: T[] | null; error: unknown };
    if (error) throw error;
    const rows = (data ?? []) as T[];
    out.push(...rows);
    if (rows.length < PAGE) return out;
    offset += PAGE;
  }
}

export async function getDashboardStats(
  batch: string = ACTIVE_CAMPAIGN
): Promise<DashboardStats> {
  const [estab, contacts, mailableA, mailableB] = await Promise.all([
    // Tous les établissements de la campagne (paginé)
    fetchAllPaginated<{
      category: string;
      enrichment_status: string;
      state: string | null;
      website: string | null;
      generic_email: string | null;
      generic_email_status: string | null;
    }>(
      () => supabase.from("establishments"),
      "category,enrichment_status,state,website,generic_email,generic_email_status",
      (q) => (q as unknown as { eq: (c: string, v: string) => typeof q }).eq("batch", batch)
    ),
    // Contacts filtrés via join inner sur établissements de la bonne campagne
    fetchAllPaginated<{
      email_status: string;
      source_provider: string | null;
      full_name: string | null;
    }>(
      () => supabase.from("contacts"),
      "email_status,source_provider,full_name,establishments!inner(batch)",
      (q) => (q as unknown as { eq: (c: string, v: string) => typeof q }).eq("establishments.batch", batch)
    ),
    // Segment A (décideurs nominatifs mailables) — équivalent au champ A de la vue
    // contacts_mailable, mais calculé direct car PostgREST ne joint pas une vue.
    supabase
      .from("contacts")
      .select("id, establishments!inner(batch)", { count: "exact", head: true })
      .eq("establishments.batch", batch)
      .eq("email_status", "valid")
      .not("nominative_email", "is", null)
      .is("opt_out_at", null),
    // Segment B (boîtes génériques mailables)
    supabase
      .from("establishments")
      .select("id", { count: "exact", head: true })
      .eq("batch", batch)
      .eq("enrichment_status", "no_email")
      .not("generic_email", "is", null)
      .eq("generic_email_status", "valid"),
  ]);
  if (mailableA.error) throw mailableA.error;
  if (mailableB.error) throw mailableB.error;
  const segA = mailableA.count ?? 0;
  const segB = mailableB.count ?? 0;

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
    mailableTotal: segA + segB,
    mailableBySegment: [
      { key: "A_decision_maker", count: segA },
      { key: "B_generic_inbox", count: segB },
    ],
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
  f: EstabFilters,
  batch: string = ACTIVE_CAMPAIGN
): Promise<{ rows: EstablishmentWithContacts[]; total: number; page: number }> {
  const page = Math.max(1, f.page ?? 1);
  let query = supabase
    .from("establishments")
    .select(LIST_COLUMNS, { count: "exact" })
    .eq("batch", batch);

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
export async function getStateFacets(
  batch: string = ACTIVE_CAMPAIGN
): Promise<string[]> {
  const { data, error } = await supabase
    .from("establishments")
    .select("state")
    .eq("batch", batch);
  if (error) throw error;
  const counts = new Map<string, number>();
  for (const r of data as { state: string | null }[]) {
    if (r.state) counts.set(r.state, (counts.get(r.state) ?? 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([s]) => s);
}

export async function getCategoryFacets(
  batch: string = ACTIVE_CAMPAIGN
): Promise<string[]> {
  const { data, error } = await supabase
    .from("establishments")
    .select("category")
    .eq("batch", batch);
  if (error) throw error;
  return [...new Set((data as { category: string }[]).map((r) => r.category))].sort();
}

// --------------------------------------------------------------------------
// Email drafts
// --------------------------------------------------------------------------

export type EmailDraftListRow = {
  id: string;
  contact_id: string | null;
  establishment_id: string;
  campaign: string;
  segment: "A_decision_maker" | "B_generic_inbox";
  recipient_email: string;
  subject: string;
  haiku_subject_variant: string | null;
  status: "draft" | "approved" | "rejected" | "sent" | "bounced";
  generated_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  notes: string | null;
  establishments: {
    id: string;
    name: string;
    city: string | null;
    country: string;
    category: string;
  } | null;
};

export type EmailDraft = EmailDraftListRow & {
  body_html: string;
  body_plain: string;
  haiku_model: string | null;
  haiku_input: Record<string, unknown>;
};

export type DraftFilters = {
  status?: string;
  country?: string;
  segment?: string;
  q?: string;
  page?: number;
};

export const DRAFTS_PAGE_SIZE = 30;

export async function getDrafts(
  f: DraftFilters,
  batch: string = ACTIVE_CAMPAIGN
): Promise<{ rows: EmailDraftListRow[]; total: number; page: number }> {
  const page = Math.max(1, f.page ?? 1);
  let query = supabase
    .from("email_drafts")
    .select(
      "id,contact_id,establishment_id,campaign,segment,recipient_email,subject,haiku_subject_variant,status,generated_at,reviewed_at,reviewed_by,notes," +
        "establishments!inner(id,name,city,country,category,batch)",
      { count: "exact" }
    )
    .eq("campaign", batch)
    .eq("establishments.batch", batch);

  if (f.status) query = query.eq("status", f.status);
  if (f.segment) query = query.eq("segment", f.segment);
  if (f.country) query = query.eq("establishments.country", f.country);
  if (f.q) query = query.or(
    `subject.ilike.%${f.q}%,recipient_email.ilike.%${f.q}%`
  );

  const from = (page - 1) * DRAFTS_PAGE_SIZE;
  query = query
    .order("generated_at", { ascending: false })
    .range(from, from + DRAFTS_PAGE_SIZE - 1);

  const { data, error, count } = await query;
  if (error) throw error;
  return {
    rows: (data ?? []) as unknown as EmailDraftListRow[],
    total: count ?? 0,
    page,
  };
}

export async function getDraft(id: string): Promise<EmailDraft | null> {
  const { data, error } = await supabase
    .from("email_drafts")
    .select(
      "*,establishments(id,name,city,country,category,website,batch,rating,review_count)"
    )
    .eq("id", id)
    .maybeSingle();
  if (error) throw error;
  return (data as unknown as EmailDraft | null) ?? null;
}

export async function getDraftsCountByStatus(
  batch: string = ACTIVE_CAMPAIGN
): Promise<Record<string, number>> {
  const { data, error } = await supabase
    .from("email_drafts")
    .select("status,establishments!inner(batch)")
    .eq("campaign", batch)
    .eq("establishments.batch", batch);
  if (error) throw error;
  const out: Record<string, number> = {};
  for (const r of (data ?? []) as { status: string }[]) {
    out[r.status] = (out[r.status] ?? 0) + 1;
  }
  return out;
}

// --------------------------------------------------------------------------
// Email stats (envois + tracking)
// --------------------------------------------------------------------------

export type EmailStats = {
  totals: {
    sent: number;
    clicked: number;
    bounced: number;
    complained: number;
    unsubscribed: number;
    replied: number;
    registered: number;
  };
  rates: {
    clickRate: number; // clicked / sent
    bounceRate: number;
    unsubRate: number;
    registerRate: number; // registered / sent
    clickToRegisterRate: number; // registered / clicked
  };
  byCountry: { key: string; sent: number; clicked: number; registered: number }[];
  bySegment: { key: string; sent: number; clicked: number; registered: number }[];
  bySubjectVariant: { key: string; sent: number; clicked: number; registered: number }[];
  daily: { day: string; sent: number; clicked: number; registered: number }[];
};

export async function getEmailStats(
  batch: string = ACTIVE_CAMPAIGN
): Promise<EmailStats> {
  const sends = await fetchAllPaginated<{
    sent_at: string | null;
    clicked_at: string | null;
    replied_at: string | null;
    bounced: boolean | null;
    complained: boolean | null;
    unsubscribed_at: string | null;
    registered_at: string | null;
    country: string | null;
    segment: string | null;
    subject_variant: string | null;
  }>(
    () => supabase.from("email_sends"),
    "sent_at,clicked_at,replied_at,bounced,complained,unsubscribed_at,registered_at,country,segment,subject_variant",
    (q) =>
      (q as unknown as { eq: (c: string, v: string) => typeof q }).eq(
        "campaign",
        batch
      )
  );

  const totals = {
    sent: 0,
    clicked: 0,
    bounced: 0,
    complained: 0,
    unsubscribed: 0,
    replied: 0,
    registered: 0,
  };
  type Bucket = { sent: number; clicked: number; registered: number };
  const newBucket = (): Bucket => ({ sent: 0, clicked: 0, registered: 0 });
  const country = new Map<string, Bucket>();
  const segment = new Map<string, Bucket>();
  const variant = new Map<string, Bucket>();
  const daily = new Map<string, Bucket>();

  for (const s of sends) {
    if (s.sent_at) totals.sent += 1;
    if (s.clicked_at) totals.clicked += 1;
    if (s.bounced) totals.bounced += 1;
    if (s.complained) totals.complained += 1;
    if (s.unsubscribed_at) totals.unsubscribed += 1;
    if (s.replied_at) totals.replied += 1;
    if (s.registered_at) totals.registered += 1;

    const c = s.country ?? "—";
    const cBucket = country.get(c) ?? newBucket();
    if (s.sent_at) cBucket.sent += 1;
    if (s.clicked_at) cBucket.clicked += 1;
    if (s.registered_at) cBucket.registered += 1;
    country.set(c, cBucket);

    const sg = s.segment ?? "—";
    const sBucket = segment.get(sg) ?? newBucket();
    if (s.sent_at) sBucket.sent += 1;
    if (s.clicked_at) sBucket.clicked += 1;
    if (s.registered_at) sBucket.registered += 1;
    segment.set(sg, sBucket);

    const v = s.subject_variant ?? "—";
    const vBucket = variant.get(v) ?? newBucket();
    if (s.sent_at) vBucket.sent += 1;
    if (s.clicked_at) vBucket.clicked += 1;
    if (s.registered_at) vBucket.registered += 1;
    variant.set(v, vBucket);

    if (s.sent_at) {
      const day = s.sent_at.slice(0, 10);
      const dBucket = daily.get(day) ?? newBucket();
      dBucket.sent += 1;
      if (s.clicked_at) dBucket.clicked += 1;
      if (s.registered_at) dBucket.registered += 1;
      daily.set(day, dBucket);
    }
  }

  const rate = (a: number, b: number) => (b === 0 ? 0 : a / b);

  return {
    totals,
    rates: {
      clickRate: rate(totals.clicked, totals.sent),
      bounceRate: rate(totals.bounced, totals.sent),
      unsubRate: rate(totals.unsubscribed, totals.sent),
      registerRate: rate(totals.registered, totals.sent),
      clickToRegisterRate: rate(totals.registered, totals.clicked),
    },
    byCountry: [...country.entries()]
      .map(([key, v]) => ({ key, ...v }))
      .sort((a, b) => b.sent - a.sent),
    bySegment: [...segment.entries()]
      .map(([key, v]) => ({ key, ...v }))
      .sort((a, b) => b.sent - a.sent),
    bySubjectVariant: [...variant.entries()]
      .map(([key, v]) => ({ key, ...v }))
      .sort((a, b) => rate(b.clicked, b.sent) - rate(a.clicked, a.sent)),
    daily: [...daily.entries()]
      .map(([day, v]) => ({ day, ...v }))
      .sort((a, b) => a.day.localeCompare(b.day)),
  };
}

// --------------------------------------------------------------------------
// Cron status — sending pipeline (Mon-Fri 400/day)
// --------------------------------------------------------------------------

export type CronStatus = {
  sentToday: number;
  dailyTarget: number;
  approvedRemaining: number;
  draftRemaining: number;
  sentTotal: number;
  /** ETA fin (date ISO YYYY-MM-DD) en supposant `dailyTarget` jours ouvrés */
  etaFinishDate: string | null;
  /** Prochaine exécution (date ISO + heure) */
  nextRunIso: string | null;
  /** True après la date de démarrage configurée */
  campaignStarted: boolean;
  /** Date de démarrage configurée (ISO YYYY-MM-DD) */
  campaignStartDate: string;
};

const CAMPAIGN_START_DATE = "2026-06-09";
const DAILY_TARGET = 400;

function nextWeekday(date: Date, hourUtc: number = 8): Date {
  // Renvoie la prochaine date Mon-Fri à hourUtc:00 UTC à partir de `date`
  const d = new Date(date);
  d.setUTCHours(hourUtc, 0, 0, 0);
  if (d.getTime() <= date.getTime()) {
    d.setUTCDate(d.getUTCDate() + 1);
  }
  // Skip weekends (0 = Sun, 6 = Sat)
  while (d.getUTCDay() === 0 || d.getUTCDay() === 6) {
    d.setUTCDate(d.getUTCDate() + 1);
  }
  return d;
}

function addWeekdays(date: Date, count: number): Date {
  const d = new Date(date);
  let added = 0;
  while (added < count) {
    d.setUTCDate(d.getUTCDate() + 1);
    const dow = d.getUTCDay();
    if (dow !== 0 && dow !== 6) added += 1;
  }
  return d;
}

export async function getCronStatus(
  batch: string = ACTIVE_CAMPAIGN,
  now: Date = new Date()
): Promise<CronStatus> {
  const todayIso = now.toISOString().slice(0, 10);
  const startOfDayIso = todayIso + "T00:00:00.000Z";

  const [draftCounts, sentTodayQ, sentTotalQ] = await Promise.all([
    // counts par statut (draft/approved/sent…) pour cette campagne
    supabase
      .from("email_drafts")
      .select("status")
      .eq("campaign", batch),
    // # envoyés aujourd'hui (sent_at >= début de jour UTC)
    supabase
      .from("email_sends")
      .select("id", { count: "exact", head: true })
      .eq("campaign", batch)
      .gte("sent_at", startOfDayIso),
    // # envoyés total
    supabase
      .from("email_sends")
      .select("id", { count: "exact", head: true })
      .eq("campaign", batch)
      .not("sent_at", "is", null),
  ]);
  if (draftCounts.error) throw draftCounts.error;
  if (sentTodayQ.error) throw sentTodayQ.error;
  if (sentTotalQ.error) throw sentTotalQ.error;

  const tally: Record<string, number> = {};
  for (const r of (draftCounts.data ?? []) as { status: string }[]) {
    tally[r.status] = (tally[r.status] ?? 0) + 1;
  }
  const approvedRemaining = tally["approved"] ?? 0;
  const draftRemaining = tally["draft"] ?? 0;

  const campaignStarted = todayIso >= CAMPAIGN_START_DATE;
  const sentToday = sentTodayQ.count ?? 0;
  const sentTotal = sentTotalQ.count ?? 0;

  // ETA — combien de jours ouvrés à raison de DAILY_TARGET/j
  let etaFinishDate: string | null = null;
  if (approvedRemaining > 0) {
    const daysNeeded = Math.ceil(approvedRemaining / DAILY_TARGET);
    const referenceDay = campaignStarted ? now : new Date(CAMPAIGN_START_DATE + "T08:00:00Z");
    const eta = addWeekdays(referenceDay, daysNeeded - 1);
    etaFinishDate = eta.toISOString().slice(0, 10);
  }

  // Prochaine exécution — next Mon-Fri 08:00 UTC ≥ max(now, CAMPAIGN_START)
  let nextRunIso: string | null = null;
  if (approvedRemaining > 0) {
    const startBase = campaignStarted
      ? now
      : new Date(CAMPAIGN_START_DATE + "T07:59:59Z");
    nextRunIso = nextWeekday(startBase).toISOString();
  }

  return {
    sentToday,
    dailyTarget: DAILY_TARGET,
    approvedRemaining,
    draftRemaining,
    sentTotal,
    etaFinishDate,
    nextRunIso,
    campaignStarted,
    campaignStartDate: CAMPAIGN_START_DATE,
  };
}

// --------------------------------------------------------------------------
// Détail établissement (pas filtré par batch : on récupère par id direct)
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
