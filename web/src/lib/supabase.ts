import "server-only";
import { createClient } from "@supabase/supabase-js";

/**
 * Client Supabase côté SERVEUR uniquement.
 * Utilise la clé secrète (service role) qui bypass le RLS.
 * Ne JAMAIS importer ce module dans un composant client.
 */
const url = process.env.SUPABASE_URL;
const secretKey =
  process.env.SUPABASE_SECRET_KEY ?? process.env.SUPABASE_KEY;

if (!url || !secretKey) {
  throw new Error(
    "Variables manquantes : SUPABASE_URL et SUPABASE_SECRET_KEY doivent être définies."
  );
}

export const supabase = createClient(url, secretKey, {
  auth: { persistSession: false, autoRefreshToken: false },
});
