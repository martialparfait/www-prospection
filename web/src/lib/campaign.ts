import "server-only";
import { cookies } from "next/headers";
import { ACTIVE_CAMPAIGN, CAMPAIGNS, CAMPAIGN_COOKIE } from "./constants";

const VALID_KEYS = new Set<string>(CAMPAIGNS.map((c) => c.key));

/** Lit la campagne active depuis le cookie (avec validation), fallback sur la campagne par défaut. */
export async function getActiveCampaign(): Promise<string> {
  const store = await cookies();
  const v = store.get(CAMPAIGN_COOKIE)?.value;
  return v && VALID_KEYS.has(v) ? v : ACTIVE_CAMPAIGN;
}

export function campaignLabel(key: string): string {
  return CAMPAIGNS.find((c) => c.key === key)?.label ?? key;
}
