import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, MessageSquare, Hash, TrendingUp, ShieldCheck } from "lucide-react";
import { AppLayout } from "@/components/AppLayout";
import { KpiCard } from "@/components/KpiCard";
import { ClassificationBadge, RiskBadge, ScoreBar } from "@/components/RiskBadge";
import { TOPICS, getClient, riskFromScore } from "@/lib/mock-data";
import type { Client, MentionBreakdown, TopicDetail } from "@/lib/types";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";

export const Route = createFileRoute("/clients/$clientId")({
  loader: ({ params }) => {
    const client = getClient(params.clientId);
    if (!client) throw notFound();
    return { client };
  },
  head: ({ loaderData }) => ({
    meta: [
      { title: `${loaderData?.client.client ?? "Client"} — InsightGuard` },
      {
        name: "description",
        content: `Analyse de réputation détaillée pour ${loaderData?.client.client}: score, sentiment, topics et mentions.`,
      },
    ],
  }),
  notFoundComponent: () => (
    <AppLayout>
      <div className="p-12 text-center">
        <h2 className="text-xl font-semibold">Entité introuvable</h2>
        <Link to="/clients" className="mt-4 inline-block text-primary hover:underline">
          ← Retour aux clients
        </Link>
      </div>
    </AppLayout>
  ),
  component: ClientDetail,
});

function ClientDetail() {
  const { client } = Route.useLoaderData() as { client: Client };
  const risk = riskFromScore(client.reliability_score);
  const topics: TopicDetail[] = client.topic_ids
    .map((id) => TOPICS.find((t) => t.topic_id === id))
    .filter((t): t is TopicDetail => Boolean(t));
  const sentimentData = client.timeline.map((p) => ({ date: p.date.slice(5), score: p.score }));

  return (
    <AppLayout>
      <div className="border-b border-border/60 bg-gradient-to-b from-primary/[0.04] to-transparent">
        <div className="mx-auto max-w-[1600px] px-6 py-6">
          <Link
            to="/clients"
            className="mb-3 inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider text-muted-foreground hover:text-primary"
          >
            <ArrowLeft className="h-3 w-3" /> Tous les clients
          </Link>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-primary">
                Fiche entité · {client.sector}
              </div>
              <h1 className="text-3xl font-bold tracking-tight">{client.client}</h1>
            </div>
            <div className="flex items-center gap-2">
              <ClassificationBadge value={client.classification} />
              <RiskBadge level={risk} />
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-[1600px] space-y-6 p-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard label="Score de fiabilité" value={client.reliability_score} icon={ShieldCheck} accent={risk === "low" ? "low" : risk === "high" ? "high" : "medium"} hint="échelle 0-100" />
          <KpiCard label="Confiance analyse" value={`${client.confidence}%`} icon={TrendingUp} hint="qualité du signal" />
          <KpiCard label="Mentions analysées" value={client.mentions_count.toLocaleString("fr-FR")} icon={MessageSquare} hint="presse + social" />
          <KpiCard label="Topics liés" value={topics.length} icon={Hash} hint="clusters BERTopic" />
        </div>

        {/* Timeline */}
        <div className="rounded-lg border border-border/70 bg-card p-5 shadow-[var(--shadow-card)]">
          <div className="mb-4">
            <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Foulescopie · 30 jours
            </div>
            <h3 className="text-base font-semibold">Évolution du score de réputation</h3>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={sentimentData} margin={{ left: -20, right: 8, top: 8 }}>
                <CartesianGrid stroke="oklch(0.28 0.02 240)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" stroke="oklch(0.55 0.02 240)" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="oklch(0.55 0.02 240)" fontSize={10} tickLine={false} axisLine={false} domain={[0, 100]} />
                <ReferenceLine y={70} stroke="oklch(0.72 0.18 150)" strokeDasharray="4 4" label={{ value: "ENGAGER", fill: "oklch(0.72 0.18 150)", fontSize: 10, position: "right" }} />
                <ReferenceLine y={45} stroke="oklch(0.65 0.22 25)" strokeDasharray="4 4" label={{ value: "EVITER", fill: "oklch(0.65 0.22 25)", fontSize: 10, position: "right" }} />
                <Tooltip
                  contentStyle={{
                    background: "oklch(0.20 0.018 240)",
                    border: "1px solid oklch(0.28 0.02 240)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Line type="monotone" dataKey="score" stroke="oklch(0.78 0.15 200)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Topics */}
          <div className="rounded-lg border border-border/70 bg-card p-5 shadow-[var(--shadow-card)]">
            <div className="mb-4">
              <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                Clusters BERTopic
              </div>
              <h3 className="text-base font-semibold">Thèmes associés</h3>
            </div>
            <div className="space-y-3">
              {topics.map((t) => (
                <Link
                  key={t.topic_id}
                  to="/topics"
                  className="block rounded-md border border-border/50 bg-muted/30 p-3 transition hover:border-primary/40 hover:bg-muted/50"
                >
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium">{t.label}</div>
                    <span className="font-mono text-[10px] text-muted-foreground">{t.count} docs</span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {t.keywords.slice(0, 4).map((k) => (
                      <span key={k} className="rounded bg-background/60 px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
                        {k}
                      </span>
                    ))}
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Mentions */}
          <div className="lg:col-span-2 rounded-lg border border-border/70 bg-card p-5 shadow-[var(--shadow-card)]">
            <div className="mb-4">
              <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                Breakdown · presse & social
              </div>
              <h3 className="text-base font-semibold">Mentions récentes analysées</h3>
            </div>
            <div className="space-y-2">
              {client.breakdown.map((m: MentionBreakdown, i: number) => {
                const sentColor =
                  m.sentiment > 0.2 ? "text-risk-low" : m.sentiment < -0.2 ? "text-risk-high" : "text-risk-medium";
                return (
                  <div key={i} className="rounded-md border border-border/50 bg-muted/20 p-3">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="rounded bg-background/60 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                          {m.source}
                        </span>
                        <span className="font-mono text-[10px] text-muted-foreground">
                          {new Date(m.date).toLocaleDateString("fr-FR")}
                        </span>
                      </div>
                      <span className={`font-mono text-xs tabular-nums ${sentColor}`}>
                        {m.sentiment > 0 ? "+" : ""}
                        {m.sentiment.toFixed(2)}
                      </span>
                    </div>
                    <p className="mt-1.5 text-sm">{m.text}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Score bar bottom */}
        <div className="rounded-lg border border-border/70 bg-card p-5">
          <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Score de fiabilité global
          </div>
          <ScoreBar score={client.reliability_score} />
        </div>
      </div>
    </AppLayout>
  );
}

