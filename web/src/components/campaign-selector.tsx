"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";
import { CAMPAIGNS } from "@/lib/constants";
import { setCampaignAction } from "@/lib/actions";

export function CampaignSelector({ active }: { active: string }) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  return (
    <form
      action={async (formData) => {
        await setCampaignAction(formData);
        startTransition(() => router.refresh());
      }}
    >
      <select
        name="campaign"
        defaultValue={active}
        onChange={(e) => e.currentTarget.form?.requestSubmit()}
        disabled={pending}
        className="rounded-lg border border-slate-300 bg-white py-1.5 pl-2.5 pr-7 text-xs font-medium text-slate-700 shadow-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
        aria-label="Campagne active"
      >
        {CAMPAIGNS.map((c) => (
          <option key={c.key} value={c.key}>
            {c.label}
          </option>
        ))}
      </select>
    </form>
  );
}
