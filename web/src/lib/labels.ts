// Libellés FR, couleurs de badges et helpers de formatage.

export const CATEGORY_LABELS: Record<string, string> = {
  yoga: "Yoga",
  pilates: "Pilates",
  fitness: "Fitness",
  martial_arts: "Arts martiaux",
  running: "Running",
  hotel: "Hôtel",
};

export const ENRICHMENT_LABELS: Record<string, string> = {
  pending: "À traiter",
  crawled: "Crawlé",
  enriched: "Enrichi",
  no_email: "Sans email perso",
  no_website: "Sans site web",
  failed: "Échec",
};

export const EMAIL_STATUS_LABELS: Record<string, string> = {
  valid: "Valide",
  catch_all: "Catch-all",
  risky: "À risque",
  invalid: "Invalide",
  unknown: "Inconnu",
};

export const SOURCE_LABELS: Record<string, string> = {
  website_crawl: "Site web",
  apollo: "Apollo",
  dropcontact: "Dropcontact",
  hunter: "Hunter",
};

export const SEGMENT_LABELS: Record<string, string> = {
  A_decision_maker: "décideurs nominatifs",
  B_generic_inbox: "boîtes génériques",
};

export function segmentLabel(s: string): string {
  return SEGMENT_LABELS[s] ?? s;
}

type Tone = "green" | "amber" | "red" | "slate" | "blue" | "violet";

const TONE_CLASS: Record<Tone, string> = {
  green: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  amber: "bg-amber-50 text-amber-700 ring-amber-600/20",
  red: "bg-rose-50 text-rose-700 ring-rose-600/20",
  slate: "bg-slate-100 text-slate-600 ring-slate-500/20",
  blue: "bg-sky-50 text-sky-700 ring-sky-600/20",
  violet: "bg-violet-50 text-violet-700 ring-violet-600/20",
};

export function toneClass(tone: Tone): string {
  return TONE_CLASS[tone];
}

export const ENRICHMENT_TONE: Record<string, Tone> = {
  enriched: "green",
  crawled: "blue",
  pending: "slate",
  no_email: "amber",
  no_website: "slate",
  failed: "red",
};

export const EMAIL_STATUS_TONE: Record<string, Tone> = {
  valid: "green",
  catch_all: "amber",
  risky: "amber",
  invalid: "red",
  unknown: "slate",
};

export const CATEGORY_TONE: Record<string, Tone> = {
  yoga: "violet",
  pilates: "blue",
  fitness: "amber",
  martial_arts: "red",
  running: "green",
  hotel: "slate",
};

export function categoryLabel(c: string): string {
  return CATEGORY_LABELS[c] ?? c;
}
export function enrichmentLabel(s: string): string {
  return ENRICHMENT_LABELS[s] ?? s;
}
export function emailStatusLabel(s: string): string {
  return EMAIL_STATUS_LABELS[s] ?? s;
}
export function sourceLabel(s: string | null): string {
  if (!s) return "—";
  return SOURCE_LABELS[s] ?? s;
}

export function fmtInt(n: number | null | undefined): string {
  if (n == null) return "—";
  return new Intl.NumberFormat("fr-FR").format(n);
}

export function fmtPct(num: number, denom: number): string {
  if (!denom) return "0 %";
  return `${Math.round((num / denom) * 100)} %`;
}

export function cleanUrl(url: string | null): string {
  if (!url) return "";
  return url.replace(/^https?:\/\//, "").replace(/\/$/, "");
}

/** Email "génériquement personnel" : un nominative_email présent. */
export function isUsableEmail(status: string): boolean {
  return status === "valid" || status === "catch_all";
}
