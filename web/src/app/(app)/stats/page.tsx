import Link from "next/link";
import { BarChart3, CalendarClock, Mail, MousePointerClick, ShieldAlert, UserMinus, Clock, UserPlus } from "lucide-react";
import { getEmailStats, getCronStatus } from "@/lib/queries";
import { getActiveCampaign, campaignLabel } from "@/lib/campaign";
import { fmtInt, fmtPct } from "@/lib/labels";
import { Card, PageHeader, StatCard } from "@/components/ui";

export const dynamic = "force-dynamic";

const FLAG: Record<string, string> = { US: "🇺🇸", GB: "🇬🇧", AU: "🇦🇺" };

const SUBJECT_PATTERN_LABEL: Record<string, string> = {
  A: "A — Free September weekend",
  B: "B — Idea for {name}",
  C: "C — Peer joined",
  D: "D — City fitness map",
  E: "E — A small ask",
};

const SEGMENT_LABEL: Record<string, string> = {
  A_decision_maker: "Décideur nominatif",
  B_generic_inbox: "Boîte générique",
};

function fmtRate(n: number): string {
  if (!Number.isFinite(n) || n === 0) return "—";
  return `${(n * 100).toFixed(1)} %`;
}

function Bar({
  current,
  max,
  className = "bg-brand-500",
}: {
  current: number;
  max: number;
  className?: string;
}) {
  const pct = max > 0 ? Math.min(100, (current / max) * 100) : 0;
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
      <div className={`h-full rounded-full ${className}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

function fmtDateShort(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("fr-FR", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Europe/Brussels",
  });
}

function fmtDateOnly(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso + "T00:00:00Z").toLocaleDateString("fr-FR", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export default async function StatsPage() {
  const activeCampaign = await getActiveCampaign();
  const [stats, cron] = await Promise.all([
    getEmailStats(activeCampaign),
    getCronStatus(activeCampaign),
  ]);

  const noData = stats.totals.sent === 0;
  const dailyProgress = Math.min(100, (cron.sentToday / cron.dailyTarget) * 100);
  const totalEnvelope = cron.sentTotal + cron.approvedRemaining + cron.draftRemaining;
  const totalProgress =
    totalEnvelope > 0 ? Math.min(100, (cron.sentTotal / totalEnvelope) * 100) : 0;

  return (
    <div className="space-y-8">
      <PageHeader
        title="Stats d'envoi"
        subtitle={`Campagne : ${campaignLabel(activeCampaign)} — mesures live alimentées par les webhooks SendGrid (clics, bounces, désabonnements, replies).`}
      />

      {/* Cron status — pipeline d'envoi */}
      <Card className="p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <CalendarClock className="h-4 w-4 text-slate-400" />
              Pipeline d'envoi — GitHub Actions cron
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              {cron.campaignStarted
                ? `${cron.dailyTarget} emails/jour ouvré, 10h CET. Tourne tant qu'il reste des drafts approuvés.`
                : `Démarrage planifié pour ${fmtDateOnly(cron.campaignStartDate)}. Le cron tourne déjà mais skip tant que la date n'est pas atteinte.`}
            </p>
          </div>
          {cron.nextRunIso && (
            <div className="rounded-lg border border-brand-200 bg-brand-50 px-3 py-2 text-xs">
              <div className="font-medium text-brand-900">Prochaine exécution</div>
              <div className="mt-0.5 text-slate-600 tnum">
                {fmtDateShort(cron.nextRunIso)}
              </div>
            </div>
          )}
        </div>

        <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-4">
          {/* Aujourd'hui */}
          <div className="rounded-lg border border-slate-200 p-3">
            <div className="text-xs text-slate-500">Aujourd'hui</div>
            <div className="mt-1 text-xl font-semibold tnum text-slate-900">
              {fmtInt(cron.sentToday)} / {fmtInt(cron.dailyTarget)}
            </div>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-brand-500"
                style={{ width: `${dailyProgress}%` }}
              />
            </div>
          </div>

          {/* Total envoyés / restants */}
          <div className="rounded-lg border border-slate-200 p-3">
            <div className="text-xs text-slate-500">Total envoyés</div>
            <div className="mt-1 text-xl font-semibold tnum text-slate-900">
              {fmtInt(cron.sentTotal)}{" "}
              <span className="text-sm font-normal text-slate-400">
                / {fmtInt(totalEnvelope)}
              </span>
            </div>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-emerald-500"
                style={{ width: `${totalProgress}%` }}
              />
            </div>
          </div>

          {/* Approuvés restants */}
          <div className="rounded-lg border border-slate-200 p-3">
            <div className="text-xs text-slate-500">Approuvés restants</div>
            <div className="mt-1 text-xl font-semibold tnum text-emerald-700">
              {fmtInt(cron.approvedRemaining)}
            </div>
            <div className="mt-1 text-xs text-slate-400">
              prêts pour le prochain run
            </div>
          </div>

          {/* ETA fin */}
          <div className="rounded-lg border border-slate-200 p-3">
            <div className="text-xs text-slate-500">ETA fin de campagne</div>
            <div className="mt-1 text-xl font-semibold tnum text-slate-900">
              {fmtDateOnly(cron.etaFinishDate)}
            </div>
            <div className="mt-1 text-xs text-slate-400">
              à {cron.dailyTarget}/j ouvré
            </div>
          </div>
        </div>

        {cron.draftRemaining > 0 && (
          <div className="mt-4 flex items-center justify-between rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs">
            <span className="text-amber-900">
              <strong>{fmtInt(cron.draftRemaining)} drafts</strong> encore en
              status <code className="rounded bg-amber-100 px-1 py-0.5">draft</code>{" "}
              — non envoyés tant qu'ils ne sont pas approuvés.
            </span>
            <Link
              href="/drafts?status=draft"
              className="font-medium text-amber-900 underline hover:text-amber-700"
            >
              Approuver →
            </Link>
          </div>
        )}
      </Card>

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <StatCard
          label="Envoyés"
          value={fmtInt(stats.totals.sent)}
          hint="emails délivrés par SendGrid"
        />
        <StatCard
          label="Clics"
          value={fmtInt(stats.totals.clicked)}
          hint={`Taux de clic : ${fmtRate(stats.rates.clickRate)}`}
          accent="text-brand-700"
        />
        <StatCard
          label="Inscriptions"
          value={fmtInt(stats.totals.registered)}
          hint={`Clic → signup : ${fmtRate(stats.rates.clickToRegisterRate)}`}
          accent="text-emerald-700"
        />
        <StatCard
          label="Bounces"
          value={fmtInt(stats.totals.bounced)}
          hint={`Taux : ${fmtRate(stats.rates.bounceRate)}`}
          accent={stats.rates.bounceRate > 0.02 ? "text-rose-700" : "text-slate-900"}
        />
        <StatCard
          label="Désabonnements"
          value={fmtInt(stats.totals.unsubscribed)}
          hint={`Taux : ${fmtRate(stats.rates.unsubRate)}`}
          accent="text-amber-700"
        />
        <StatCard
          label="Réponses"
          value={fmtInt(stats.totals.replied)}
          hint="webhook ou Reply STOP"
          accent="text-emerald-700"
        />
      </div>

      {noData ? (
        <Card className="p-10 text-center">
          <Mail className="mx-auto h-10 w-10 text-slate-300" />
          <h2 className="mt-4 text-lg font-semibold text-slate-900">
            Aucun envoi pour l'instant
          </h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">
            Cette page se peuplera automatiquement dès que tu lanceras{" "}
            <code className="rounded bg-slate-100 px-1.5 py-0.5">
              python3 send_drafts.py
            </code>{" "}
            avec un compte SendGrid configuré. Voir{" "}
            <code className="rounded bg-slate-100 px-1.5 py-0.5">
              docs/sendgrid_setup.md
            </code>{" "}
            pour la procédure.
          </p>
          <Link
            href="/drafts"
            className="mt-6 inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            <Mail className="h-4 w-4" />
            Voir les drafts prêts à envoyer
          </Link>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* By country */}
          <Card className="p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <BarChart3 className="h-4 w-4 text-slate-400" />
              Performance par pays
            </h2>
            <div className="mt-4 space-y-3">
              {stats.byCountry.map((c) => {
                const max = stats.byCountry[0]?.sent || 1;
                const rate = c.sent === 0 ? 0 : c.clicked / c.sent;
                return (
                  <div key={c.key}>
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-base">{FLAG[c.key] ?? c.key}</span>
                        <span className="text-slate-700">{c.key}</span>
                      </div>
                      <div className="text-xs text-slate-500 tnum">
                        {fmtInt(c.clicked)} clics / {fmtInt(c.sent)} envois ·{" "}
                        <span className="font-semibold text-slate-800">
                          {fmtRate(rate)}
                        </span>
                      </div>
                    </div>
                    <div className="mt-1.5">
                      <Bar current={c.sent} max={max} />
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* By segment */}
          <Card className="p-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <BarChart3 className="h-4 w-4 text-slate-400" />
              Performance par segment
            </h2>
            <div className="mt-4 space-y-3">
              {stats.bySegment.map((s) => {
                const max = stats.bySegment[0]?.sent || 1;
                const rate = s.sent === 0 ? 0 : s.clicked / s.sent;
                return (
                  <div key={s.key}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-700">
                        {SEGMENT_LABEL[s.key] ?? s.key}
                      </span>
                      <div className="text-xs text-slate-500 tnum">
                        {fmtInt(s.clicked)} clics / {fmtInt(s.sent)} envois ·{" "}
                        <span className="font-semibold text-slate-800">
                          {fmtRate(rate)}
                        </span>
                      </div>
                    </div>
                    <div className="mt-1.5">
                      <Bar
                        current={s.sent}
                        max={max}
                        className={s.key === "A_decision_maker" ? "bg-violet-500" : "bg-sky-500"}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* By subject variant — A/B test */}
          <Card className="p-5 lg:col-span-2">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <MousePointerClick className="h-4 w-4 text-slate-400" />
              A/B test — performance des subject lines
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Classement par taux de clic décroissant. Le pattern gagnant indique
              quel angle convertit le mieux.
            </p>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <th className="px-2 py-2">Pattern</th>
                    <th className="px-2 py-2">Envois</th>
                    <th className="px-2 py-2">Clics</th>
                    <th className="px-2 py-2">Taux clic</th>
                    <th className="px-2 py-2"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {stats.bySubjectVariant.map((v) => {
                    const rate = v.sent === 0 ? 0 : v.clicked / v.sent;
                    const max =
                      stats.bySubjectVariant[0]?.sent > 0
                        ? stats.bySubjectVariant[0].clicked /
                          stats.bySubjectVariant[0].sent
                        : 0;
                    return (
                      <tr key={v.key}>
                        <td className="px-2 py-2 font-medium text-slate-900">
                          {SUBJECT_PATTERN_LABEL[v.key] ?? v.key}
                        </td>
                        <td className="px-2 py-2 text-slate-700 tnum">
                          {fmtInt(v.sent)}
                        </td>
                        <td className="px-2 py-2 text-slate-700 tnum">
                          {fmtInt(v.clicked)}
                        </td>
                        <td className="px-2 py-2 font-semibold tnum text-brand-700">
                          {fmtRate(rate)}
                        </td>
                        <td className="w-1/3 px-2 py-2">
                          <Bar current={rate} max={Math.max(max, 0.01)} />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Time series */}
          {stats.daily.length > 0 && (
            <Card className="p-5 lg:col-span-2">
              <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                <Clock className="h-4 w-4 text-slate-400" />
                Activité par jour
              </h2>
              <div className="mt-4 space-y-2">
                {stats.daily.map((d) => {
                  const max = Math.max(...stats.daily.map((x) => x.sent), 1);
                  return (
                    <div key={d.day} className="flex items-center gap-3">
                      <div className="w-24 shrink-0 text-xs text-slate-500 tnum">
                        {d.day}
                      </div>
                      <div className="flex-1">
                        <Bar current={d.sent} max={max} />
                      </div>
                      <div className="w-32 shrink-0 text-right text-xs text-slate-500 tnum">
                        {fmtInt(d.sent)} envois · {fmtInt(d.clicked)} clics
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {/* Funnel conversion (clic → signup) */}
          <Card className="p-5 lg:col-span-2">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <UserPlus className="h-4 w-4 text-slate-400" />
              Funnel — clic → inscription sur wellmap.org
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Mesure les signups effectivement complétés via le bouton CTA (matching{" "}
              <code className="rounded bg-slate-100 px-1 py-0.5">utm_content=draft_id</code>{" "}
              remonté par wellmap.org sur <code className="rounded bg-slate-100 px-1 py-0.5">/api/conversions</code>).
            </p>
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-4">
              <div className="rounded-lg border border-slate-200 p-3">
                <div className="text-xs text-slate-500">Envoyés</div>
                <div className="mt-1 text-xl font-semibold tnum text-slate-900">
                  {fmtInt(stats.totals.sent)}
                </div>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <div className="text-xs text-slate-500">Clics</div>
                <div className="mt-1 text-xl font-semibold tnum text-brand-700">
                  {fmtInt(stats.totals.clicked)}
                </div>
                <div className="mt-1 text-xs text-slate-400">
                  Envoi → clic : {fmtRate(stats.rates.clickRate)}
                </div>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <div className="text-xs text-slate-500">Inscriptions</div>
                <div className="mt-1 text-xl font-semibold tnum text-emerald-700">
                  {fmtInt(stats.totals.registered)}
                </div>
                <div className="mt-1 text-xs text-slate-400">
                  Clic → signup : {fmtRate(stats.rates.clickToRegisterRate)}
                </div>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <div className="text-xs text-slate-500">Taux global</div>
                <div className="mt-1 text-xl font-semibold tnum text-emerald-700">
                  {fmtRate(stats.rates.registerRate)}
                </div>
                <div className="mt-1 text-xs text-slate-400">Envoi → signup</div>
              </div>
            </div>

            {stats.totals.registered > 0 && (
              <div className="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Par pays
                  </div>
                  <table className="mt-2 w-full text-sm">
                    <tbody className="divide-y divide-slate-100">
                      {stats.byCountry.map((c) => (
                        <tr key={c.key}>
                          <td className="py-1.5">
                            <span className="text-base">{FLAG[c.key] ?? c.key}</span>{" "}
                            <span className="text-slate-700">{c.key}</span>
                          </td>
                          <td className="py-1.5 text-right tnum text-slate-600">
                            {fmtInt(c.registered)} / {fmtInt(c.clicked)} clics
                          </td>
                          <td className="py-1.5 pl-3 text-right font-semibold tnum text-emerald-700">
                            {c.clicked === 0
                              ? "—"
                              : fmtRate(c.registered / c.clicked)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Par variant A/B
                  </div>
                  <table className="mt-2 w-full text-sm">
                    <tbody className="divide-y divide-slate-100">
                      {stats.bySubjectVariant.map((v) => (
                        <tr key={v.key}>
                          <td className="py-1.5 text-slate-700">
                            {SUBJECT_PATTERN_LABEL[v.key] ?? v.key}
                          </td>
                          <td className="py-1.5 text-right tnum text-slate-600">
                            {fmtInt(v.registered)} / {fmtInt(v.clicked)} clics
                          </td>
                          <td className="py-1.5 pl-3 text-right font-semibold tnum text-emerald-700">
                            {v.clicked === 0
                              ? "—"
                              : fmtRate(v.registered / v.clicked)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {stats.totals.registered === 0 && stats.totals.clicked > 0 && (
              <p className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                <strong>Aucune inscription remontée par wellmap.org.</strong>{" "}
                Vérifier que le hook <code>user_register</code> côté wellmap POST bien sur{" "}
                <code className="rounded bg-amber-100 px-1 py-0.5">
                  /api/conversions
                </code>{" "}
                avec le header <code>X-WWW-Token</code>. Voir{" "}
                <code className="rounded bg-amber-100 px-1 py-0.5">
                  docs/wellmap_conversions.md
                </code>
                .
              </p>
            )}
          </Card>

          {/* Health */}
          <Card className="p-5 lg:col-span-2">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <ShieldAlert className="h-4 w-4 text-slate-400" />
              Santé deliverability
            </h2>
            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-slate-200 p-3">
                <div className="text-xs text-slate-500">Taux de bounce</div>
                <div
                  className={`mt-1 text-xl font-semibold tnum ${
                    stats.rates.bounceRate > 0.02
                      ? "text-rose-700"
                      : "text-emerald-700"
                  }`}
                >
                  {fmtRate(stats.rates.bounceRate)}
                </div>
                <div className="mt-1 text-xs text-slate-400">
                  Cible Gmail/Outlook : &lt; 2 %
                </div>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <div className="text-xs text-slate-500">
                  Taux de plaintes (spam)
                </div>
                <div
                  className={`mt-1 text-xl font-semibold tnum ${
                    stats.totals.complained > 0 &&
                    stats.totals.complained / Math.max(1, stats.totals.sent) >
                      0.001
                      ? "text-rose-700"
                      : "text-emerald-700"
                  }`}
                >
                  {fmtRate(
                    stats.totals.complained / Math.max(1, stats.totals.sent)
                  )}
                </div>
                <div className="mt-1 text-xs text-slate-400">
                  Cible : &lt; 0.1 % (sinon blacklist)
                </div>
              </div>
              <div className="rounded-lg border border-slate-200 p-3">
                <div className="text-xs text-slate-500">
                  Taux de désabonnement
                </div>
                <div className="mt-1 text-xl font-semibold tnum text-amber-700">
                  {fmtRate(stats.rates.unsubRate)}
                </div>
                <div className="mt-1 text-xs text-slate-400 inline-flex items-center gap-1">
                  <UserMinus className="h-3 w-3" />
                  ajoutés à opt_out automatiquement
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
