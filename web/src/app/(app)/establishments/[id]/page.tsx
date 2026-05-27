import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  Globe,
  Phone,
  MapPin,
  Mail,
  User,
  BadgeCheck,
} from "lucide-react";
import { getEstablishment } from "@/lib/queries";
import { cleanUrl, fmtInt, sourceLabel } from "@/lib/labels";
import {
  Card,
  CategoryBadge,
  EmailStatusBadge,
  EnrichmentBadge,
  Rating,
} from "@/components/ui";

export const dynamic = "force-dynamic";

function fmtDate(s: string | null): string {
  if (!s) return "—";
  return new Date(s).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function Field({
  icon: Icon,
  label,
  children,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-start gap-3">
      <Icon className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
      <div className="min-w-0">
        <div className="text-xs font-medium text-slate-400">{label}</div>
        <div className="text-sm text-slate-800">{children}</div>
      </div>
    </div>
  );
}

export default async function EstablishmentDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const data = await getEstablishment(id);
  if (!data) notFound();
  const { estab, contacts } = data;

  return (
    <div className="space-y-6">
      <Link
        href="/establishments"
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Retour aux établissements
      </Link>

      {/* En-tête */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            {estab.name}
          </h1>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <CategoryBadge value={estab.category} />
            <EnrichmentBadge value={estab.enrichment_status} />
            <Rating value={estab.rating} count={estab.review_count} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Coordonnées de l'établissement */}
        <Card className="space-y-4 p-5 lg:col-span-1">
          <h2 className="text-sm font-semibold text-slate-900">
            Informations
          </h2>
          <Field icon={MapPin} label="Adresse">
            {estab.address || "—"}
            {(estab.city || estab.state) && (
              <div className="text-slate-500">
                {[estab.city, estab.state, estab.postal_code]
                  .filter(Boolean)
                  .join(", ")}
              </div>
            )}
          </Field>
          <Field icon={Phone} label="Téléphone">
            {estab.phone ? (
              <a href={`tel:${estab.phone}`} className="hover:text-brand-700">
                {estab.phone}
              </a>
            ) : (
              "—"
            )}
          </Field>
          <Field icon={Globe} label="Site web">
            {estab.website ? (
              <a
                href={estab.website}
                target="_blank"
                rel="noopener noreferrer"
                className="break-all text-brand-700 hover:underline"
              >
                {cleanUrl(estab.website)}
              </a>
            ) : (
              "—"
            )}
          </Field>
          <Field icon={Mail} label="Email générique">
            {estab.generic_email ? (
              <div className="flex flex-wrap items-center gap-2">
                <a
                  href={`mailto:${estab.generic_email}`}
                  className="break-all hover:text-brand-700"
                >
                  {estab.generic_email}
                </a>
                {estab.generic_email_status && (
                  <EmailStatusBadge value={estab.generic_email_status} />
                )}
              </div>
            ) : (
              "—"
            )}
          </Field>
        </Card>

        {/* Contacts */}
        <div className="space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-900">
              Contacts identifiés
            </h2>
            <span className="text-xs text-slate-400 tnum">
              {fmtInt(contacts.length)} contact{contacts.length > 1 ? "s" : ""}
            </span>
          </div>

          {contacts.length === 0 ? (
            <Card className="p-8 text-center text-sm text-slate-400">
              Aucun contact nominatif identifié pour cet établissement.
            </Card>
          ) : (
            <div className="space-y-3">
              {contacts.map((c) => (
                <Card key={c.id} className="p-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-400">
                        <User className="h-4 w-4" />
                      </span>
                      <div>
                        <div className="font-medium text-slate-900">
                          {c.full_name || (
                            <span className="text-slate-400">
                              Nom non identifié
                            </span>
                          )}
                        </div>
                        {c.role && (
                          <div className="text-xs text-slate-500">{c.role}</div>
                        )}
                      </div>
                    </div>
                    <EmailStatusBadge value={c.email_status} />
                  </div>

                  <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <Field icon={Mail} label="Email">
                      {c.nominative_email ? (
                        <a
                          href={`mailto:${c.nominative_email}`}
                          className="break-all text-brand-700 hover:underline"
                        >
                          {c.nominative_email}
                        </a>
                      ) : (
                        "—"
                      )}
                    </Field>
                    <Field icon={BadgeCheck} label="Source / vérification">
                      {sourceLabel(c.source_provider)}
                      {c.email_verified_at && (
                        <span className="text-slate-400">
                          {" "}
                          · vérifié le {fmtDate(c.email_verified_at)}
                        </span>
                      )}
                    </Field>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
