import { redirect } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import { LoginForm } from "./login-form";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ from?: string }>;
}) {
  // Déjà connecté → on renvoie vers l'app.
  if (await isAuthenticated()) redirect("/");

  const { from } = await searchParams;
  const target = from && from.startsWith("/") ? from : "/";

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 text-center">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand.svg"
            alt="World Wellness Weekend"
            className="mx-auto h-16 w-auto"
          />
          <h1 className="mt-5 text-2xl font-semibold text-slate-900">
            Prospection — Données
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Espace de consultation réservé.
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <LoginForm from={target} />
        </div>
        <p className="mt-4 text-center text-xs text-slate-400">
          Accès protégé · données confidentielles
        </p>
      </div>
    </main>
  );
}
