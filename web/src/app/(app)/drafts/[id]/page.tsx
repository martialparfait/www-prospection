import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Check, ExternalLink, Sparkles, X } from "lucide-react";
import { getDraft } from "@/lib/queries";
import { approveDraftAction, rejectDraftAction } from "@/lib/actions";
import { Badge, Card } from "@/components/ui";

export const dynamic = "force-dynamic";

const STATUS_LABEL: Record<string, string> = {
  draft: "Brouillon",
  approved: "Approuvé",
  rejected: "Rejeté",
  sent: "Envoyé",
  bounced: "Bounce",
};
const STATUS_TONE: Record<string, "slate" | "green" | "amber" | "red" | "blue"> = {
  draft: "slate",
  approved: "green",
  rejected: "red",
  sent: "blue",
  bounced: "amber",
};
const FLAG: Record<string, string> = { US: "🇺🇸", GB: "🇬🇧", AU: "🇦🇺" };

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </div>
      <div className="mt-1 text-sm text-slate-800">{children}</div>
    </div>
  );
}

export default async function DraftDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const d = await getDraft(id);
  if (!d) notFound();

  const e = (d as unknown as { establishments?: { name: string; city: string | null; country: string; category: string; website: string | null; rating: number | null; review_count: number | null } }).establishments;
  const country = e?.country ?? "??";
  const haikuInput = (d.haiku_input ?? {}) as Record<string, unknown>;

  return (
    <div className="space-y-6">
      <Link
        href="/drafts"
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Retour aux emails
      </Link>

      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            {d.subject}
          </h1>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-500">
            <span className="text-base">{FLAG[country] ?? country}</span>
            <Badge tone={d.segment === "A_decision_maker" ? "violet" : "blue"}>
              {d.segment === "A_decision_maker" ? "Décideur nominatif" : "Boîte générique"}
            </Badge>
            <Badge tone={STATUS_TONE[d.status]}>{STATUS_LABEL[d.status]}</Badge>
            <span>→ {d.recipient_email}</span>
          </div>
        </div>

        {/* Approve / Reject — visible uniquement quand status=draft */}
        {d.status === "draft" && (
          <div className="flex items-center gap-2">
            <form action={approveDraftAction}>
              <input type="hidden" name="id" value={d.id} />
              <button
                type="submit"
                className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-emerald-700"
              >
                <Check className="h-4 w-4" />
                Approuver
              </button>
            </form>
            <form action={rejectDraftAction} className="flex items-center gap-2">
              <input type="hidden" name="id" value={d.id} />
              <input
                type="text"
                name="notes"
                placeholder="Raison (optionnel)…"
                className="w-48 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm outline-none focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20"
              />
              <button
                type="submit"
                className="inline-flex items-center gap-1.5 rounded-lg border border-rose-300 bg-white px-4 py-2 text-sm font-medium text-rose-700 shadow-sm transition hover:bg-rose-50"
              >
                <X className="h-4 w-4" />
                Rejeter
              </button>
            </form>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_2fr]">
        {/* Metadata */}
        <Card className="space-y-4 p-5">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Destinataire</h2>
            <div className="mt-3 space-y-3">
              <Field label="Établissement">
                {e?.name ?? "—"}
                {e?.city && (
                  <div className="text-xs text-slate-500">
                    {e.city}, {country}
                  </div>
                )}
              </Field>
              <Field label="Email destinataire">
                <span className="break-all">{d.recipient_email}</span>
              </Field>
              {e?.website && (
                <Field label="Site web">
                  <a
                    href={e.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 break-all text-brand-700 hover:underline"
                  >
                    {e.website.replace(/^https?:\/\//, "").replace(/\/$/, "")}
                    <ExternalLink className="h-3 w-3 shrink-0" />
                  </a>
                </Field>
              )}
              {d.contact_id && (
                <Field label="Contact lié">
                  <Link
                    href={`/establishments/${d.establishment_id}`}
                    className="text-brand-700 hover:underline"
                  >
                    Voir la fiche →
                  </Link>
                </Field>
              )}
            </div>
          </div>

          <div className="border-t border-slate-100 pt-4">
            <h2 className="text-sm font-semibold text-slate-900">
              Personnalisation Haiku
            </h2>
            <div className="mt-3 space-y-3">
              <Field label="Modèle">
                <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs">
                  {d.haiku_model ?? "—"}
                </code>
              </Field>
              <Field label="Sujet — pattern A/B">
                <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs">
                  {d.haiku_subject_variant ?? "—"}
                </code>
              </Field>
              <Field label="Catégorie inférée">
                <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs">
                  {String(haikuInput.establishment_category_enum ?? "—")}
                </code>
              </Field>
              <Field label="Peer chain utilisée">
                <span className="text-xs text-slate-600">
                  {String(haikuInput.peer_chain_hint ?? "—")}
                </span>
              </Field>
              {Boolean(haikuInput.decision_maker_role) && (
                <Field label="Rôle (input)">
                  <span className="text-xs text-slate-600">
                    {String(haikuInput.decision_maker_role)}
                  </span>
                </Field>
              )}
            </div>
          </div>

          <div className="border-t border-slate-100 pt-4">
            <h2 className="text-sm font-semibold text-slate-900">Méta</h2>
            <div className="mt-3 space-y-3">
              <Field label="Généré le">{fmtDate(d.generated_at)}</Field>
              {d.reviewed_at && (
                <Field label="Revu le">
                  {fmtDate(d.reviewed_at)} par {d.reviewed_by ?? "—"}
                </Field>
              )}
              {d.notes && (
                <Field label="Notes">
                  <p className="text-xs text-slate-600">{d.notes}</p>
                </Field>
              )}
            </div>
          </div>
        </Card>

        {/* Preview HTML */}
        <Card className="overflow-hidden p-0">
          <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-5 py-3">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
              <Sparkles className="h-3.5 w-3.5" />
              Aperçu HTML
            </div>
            <div className="text-xs text-slate-400">
              Subject : <span className="font-medium text-slate-700">{d.subject}</span>
            </div>
          </div>
          <iframe
            srcDoc={d.body_html}
            title="Aperçu email"
            sandbox=""
            className="block h-[900px] w-full border-0 bg-white"
          />
        </Card>
      </div>

      {/* Body plain (debug / accessibility) */}
      <details className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <summary className="cursor-pointer text-sm font-medium text-slate-700">
          Version texte brut (plain)
        </summary>
        <pre className="mt-3 whitespace-pre-wrap text-xs text-slate-600">
{d.body_plain}
        </pre>
      </details>
    </div>
  );
}
