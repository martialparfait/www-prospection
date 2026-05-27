import { Star } from "lucide-react";
import {
  categoryLabel,
  emailStatusLabel,
  enrichmentLabel,
  toneClass,
  CATEGORY_TONE,
  EMAIL_STATUS_TONE,
  ENRICHMENT_TONE,
} from "@/lib/labels";

export function Badge({
  children,
  tone = "slate",
}: {
  children: React.ReactNode;
  tone?: Parameters<typeof toneClass>[0];
}) {
  return (
    <span
      className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset whitespace-nowrap ${toneClass(
        tone
      )}`}
    >
      {children}
    </span>
  );
}

export function CategoryBadge({ value }: { value: string }) {
  return <Badge tone={CATEGORY_TONE[value] ?? "slate"}>{categoryLabel(value)}</Badge>;
}

export function EnrichmentBadge({ value }: { value: string }) {
  return <Badge tone={ENRICHMENT_TONE[value] ?? "slate"}>{enrichmentLabel(value)}</Badge>;
}

export function EmailStatusBadge({ value }: { value: string }) {
  return <Badge tone={EMAIL_STATUS_TONE[value] ?? "slate"}>{emailStatusLabel(value)}</Badge>;
}

export function Card({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}
    >
      {children}
    </div>
  );
}

export function StatCard({
  label,
  value,
  hint,
  accent = "text-slate-900",
}: {
  label: string;
  value: React.ReactNode;
  hint?: React.ReactNode;
  accent?: string;
}) {
  return (
    <Card className="p-5">
      <div className="text-sm font-medium text-slate-500">{label}</div>
      <div className={`mt-2 text-3xl font-semibold tnum ${accent}`}>{value}</div>
      {hint != null && (
        <div className="mt-1 text-xs text-slate-500">{hint}</div>
      )}
    </Card>
  );
}

export function Rating({
  value,
  count,
}: {
  value: number | null;
  count: number | null;
}) {
  if (value == null) return <span className="text-slate-400">—</span>;
  return (
    <span className="inline-flex items-center gap-1 text-sm text-slate-700 tnum">
      <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
      {value.toFixed(1)}
      {count != null && (
        <span className="text-slate-400">({count})</span>
      )}
    </span>
  );
}

/** Barre empilée pour visualiser une répartition. */
export function StackedBar({
  segments,
}: {
  segments: { label: string; value: number; className: string }[];
}) {
  const total = segments.reduce((a, s) => a + s.value, 0) || 1;
  return (
    <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
      {segments.map((s, i) =>
        s.value > 0 ? (
          <div
            key={i}
            className={s.className}
            style={{ width: `${(s.value / total) * 100}%` }}
            title={`${s.label} : ${s.value}`}
          />
        ) : null
      )}
    </div>
  );
}

export function PageHeader({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          {title}
        </h1>
        {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}
