"use client";

import { Check } from "lucide-react";
import { useState, useTransition } from "react";
import { bulkApproveDraftsAction } from "@/lib/actions";

type Props = {
  campaign: string;
  country: string;
  segment: string;
  count: number;
};

/**
 * Bouton bulk-approve avec confirmation native (window.confirm) — empêche
 * l'approbation accidentelle de milliers de drafts d'un clic.
 */
export function BulkApproveButton({ campaign, country, segment, count }: Props) {
  const [isPending, startTransition] = useTransition();
  const [confirming, setConfirming] = useState(false);

  function handleClick() {
    if (!confirming) {
      setConfirming(true);
      // Auto-reset après 4s — si l'utilisateur ne re-clique pas, on annule
      setTimeout(() => setConfirming(false), 4000);
      return;
    }
    const fd = new FormData();
    fd.set("campaign", campaign);
    fd.set("country", country);
    fd.set("segment", segment);
    startTransition(async () => {
      await bulkApproveDraftsAction(fd);
      setConfirming(false);
    });
  }

  const label = confirming
    ? `Confirmer : approuver ${count} drafts ?`
    : `Approuver les ${count} drafts filtrés`;

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isPending}
      className={`inline-flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm font-medium text-white shadow-sm transition disabled:cursor-wait disabled:opacity-60 ${
        confirming
          ? "bg-rose-600 ring-2 ring-rose-600/30 hover:bg-rose-700"
          : "bg-emerald-600 hover:bg-emerald-700"
      }`}
    >
      <Check className="h-4 w-4" />
      {isPending ? "Approbation en cours…" : label}
    </button>
  );
}
