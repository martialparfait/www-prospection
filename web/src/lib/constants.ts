// Edge-safe constants (importable from proxy.ts without pulling Node-only deps).
export const COOKIE_NAME = "www_auth";

// Campagnes connues — l'ordre détermine le défaut (1ère = active).
export const CAMPAIGNS = [
  { key: "metro_fitness_2026", label: "Metro Fitness 2026 (USA/UK/AU)" },
  { key: "pilot_us_2026", label: "Pilote US Yoga/Pilates (archivé)" },
] as const;

export const ACTIVE_CAMPAIGN = CAMPAIGNS[0].key;
export const CAMPAIGN_COOKIE = "www_campaign";
