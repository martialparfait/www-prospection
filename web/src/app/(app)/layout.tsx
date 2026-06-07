import Link from "next/link";
import { redirect } from "next/navigation";
import { LogOut } from "lucide-react";
import { isAuthenticated } from "@/lib/auth";
import { logoutAction } from "@/lib/actions";
import { getActiveCampaign } from "@/lib/campaign";
import { CampaignSelector } from "@/components/campaign-selector";
import { Nav } from "./nav";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Vérification cryptographique réelle (le proxy ne fait qu'un check optimiste).
  if (!(await isAuthenticated())) redirect("/login");

  const activeCampaign = await getActiveCampaign();

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2.5">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/brand.svg"
                alt="World Wellness Weekend"
                className="h-9 w-auto"
              />
              <span className="hidden border-l border-slate-200 pl-2.5 text-sm font-semibold text-slate-700 sm:block">
                Prospection
              </span>
            </Link>
            <Nav />
          </div>
          <div className="flex items-center gap-2">
            <CampaignSelector active={activeCampaign} />
            <form action={logoutAction}>
              <button
                type="submit"
                className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Déconnexion</span>
              </button>
            </form>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</main>
      <footer className="mx-auto max-w-7xl px-4 pb-8 text-xs text-slate-400 sm:px-6">
        Données collectées pour World Wellness Weekend · usage interne et client ·
        consultation seule.
      </footer>
    </div>
  );
}
