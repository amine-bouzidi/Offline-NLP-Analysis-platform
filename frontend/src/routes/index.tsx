import { createFileRoute, Link } from "@tanstack/react-router";
import { Activity, AlertTriangle, ShieldCheck, MessageSquare, ArrowUpRight } from "lucide-react";
import { AppLayout } from "@/components/AppLayout";
import { KpiCard } from "@/components/KpiCard";
import { ClassificationBadge, RiskBadge, ScoreBar } from "@/components/RiskBadge";
import { CLIENTS, TOPICS, riskFromScore } from "@/lib/mock-data";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
} from "recharts";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard — InsightGuard" },
      { name: "description", content: "Vue d'ensemble : scores de fiabilité, mentions, niveaux de risque et thèmes détectés." },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const avgScore = Math.round(CLIENTS.reduce((s, c) => s + c.reliability_score, 0) / CLIENTS.length);
  const totalMentions = CLIENTS.reduce((s, c) => s + c.mentions_count, 0);
  const highRisk = CLIENTS.filter((c) => riskFromScore(c.reliability_score) === "high").length;
  const engageCount = CLIENTS.filter((c) => c.classification === "ENGAGER").length;

  // Aggregate timeline = mean across clients
  const aggTimeline = CLIENTS[0].timeline.map((p, i) => ({
    date: p.date.slice(5),
    score: Math.round(CLIENTS.reduce((s, c) => s + c.timeline[i].score, 0) / CLIENTS.length),
  }));

  const topTopics = [...TOPICS].sort((a, b) => b.count - a.count).slice(0, 6);
  const top5Risk = [...CLIENTS].sort((a, b) => a.reliability_score - b.reliability_score).slice(0, 5);

  return (
    <AppLayout>
      <div className="border-b border-border/60 bg-gradient-to-b from-primary/[0.04] to-transparent">
        <div className="mx-auto flex max-w-[1600px] items-end justify-between px-6 py-6">
          <div>
            <div className="mb-1 font-mono text-[10px] uppercase tracking-[0.2em] text-primary">
              Due Diligence · Tableau de bord
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Vue d'ensemble du portefeuille</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Surveillance temps réel de {CLIENTS.length} entités · {TOPICS.length} thématiques actives
            </p>
          </div>
          <div className="hidden items-center gap-2 font-mono text-xs text-muted-foreground md:flex">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-risk-low" />
            Pipeline NLP · synced {new Date().toLocaleDateString("fr-FR")}
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-[1600px] space-y-6 p-6">
        {/* KPIs */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            label="Score de fiabilité moyen"
            value={avgScore}
            delta="+2.4"
            deltaTone="up"
            icon={ShieldCheck}
            hint={`sur ${CLIENTS.length} entités suivies`}
            accent="primary"
          />
          <KpiCard
            label="Mentions détectées"
            value={totalMentions.toLocaleString("fr-FR")}
            delta="+18.7%"
            deltaTone="up"
            icon={MessageSquare}
            hint="presse + social · 30 derniers jours"
          />
          <KpiCard
            label="Risque global élevé"
            value={highRisk}
            delta={highRisk > 2 ? "+1" : "0"}
            deltaTone={highRisk > 2 ? "down" : "neutral"}
            icon={AlertTriangle}
            hint="entités à éviter"
            accent="high"
          />
          <KpiCard
            label="Recommandations ENGAGER"
            value={engageCount}
            delta="+3"
            deltaTone="up"
            icon={Activity}
            hint="partenaires fiables"
            accent="low"
          />
        </div>

        {/* Charts row */}
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2 rounded-lg border border-border/70 bg-card p-5 shadow-[var(--shadow-card)]">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  Foulescopie · 30 jours
                </div>
                <h3 className="text-base font-semibold">Évolution du score moyen de réputation</h3>
              </div>
              <Link
                to="/foulescopie"
                className="inline-flex items-center gap-1 font-mono text-[11px] uppercase tracking-wider text-primary hover:underline"
              >
                Voir détail <ArrowUpRight className="h-3 w-3" />
              </Link>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={aggTimeline} margin={{ left: -20, right: 8, top: 8 }}>
                  <defs>
                    <linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="oklch(0.78 0.15 200)" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="oklch(0.78 0.15 200)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="oklch(0.28 0.02 240)" strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" stroke="oklch(0.55 0.02 240)" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="oklch(0.55 0.02 240)" fontSize={10} tickLine={false} axisLine={false} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      background: "oklch(0.20 0.018 240)",
                      border: "1px solid oklch(0.28 0.02 240)",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                    labelStyle={{ color: "oklch(0.65 0.025 240)" }}
                  />
                  <Area
                    type="monotone"
                    dataKey="score"
                    stroke="oklch(0.78 0.15 200)"
                    strokeWidth={2}
                    fill="url(#scoreFill)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-lg border border-border/70 bg-card p-5 shadow-[var(--shadow-card)]">
            <div className="mb-4">
              <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                BERTopic · Top thèmes
              </div>
              <h3 className="text-base font-semibold">Volume par cluster</h3>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topTopics} layout="vertical" margin={{ left: 0, right: 8 }}>
                  <CartesianGrid stroke="oklch(0.28 0.02 240)" strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" stroke="oklch(0.55 0.02 240)" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis
                    type="category"
                    dataKey="label"
                    stroke="oklch(0.65 0.025 240)"
                    fontSize={11}
                    tickLine={false}
                    axisLine={false}
                    width={120}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "oklch(0.20 0.018 240)",
                      border: "1px solid oklch(0.28 0.02 240)",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="count" fill="oklch(0.78 0.15 200)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Top risk table */}
        <div className="rounded-lg border border-border/70 bg-card shadow-[var(--shadow-card)]">
          <div className="flex items-center justify-between border-b border-border/60 p-5">
            <div>
              <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                Alertes prioritaires
              </div>
              <h3 className="text-base font-semibold">Top 5 entités à risque</h3>
            </div>
            <Link
              to="/clients"
              className="inline-flex items-center gap-1 font-mono text-[11px] uppercase tracking-wider text-primary hover:underline"
            >
              Tous les clients <ArrowUpRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border/40 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  <th className="px-5 py-2.5 text-left">Entité</th>
                  <th className="px-5 py-2.5 text-left">Secteur</th>
                  <th className="px-5 py-2.5 text-left">Score</th>
                  <th className="px-5 py-2.5 text-left">Classification</th>
                  <th className="px-5 py-2.5 text-left">Risque</th>
                  <th className="px-5 py-2.5 text-left">Confiance</th>
                  <th className="px-5 py-2.5 text-right">Mentions</th>
                </tr>
              </thead>
              <tbody>
                {top5Risk.map((c) => (
                  <tr
                    key={c.id}
                    className="group border-b border-border/30 transition hover:bg-muted/30"
                  >
                    <td className="px-5 py-3">
                      <Link
                        to="/clients/$clientId"
                        params={{ clientId: c.id }}
                        className="font-medium text-foreground transition group-hover:text-primary"
                      >
                        {c.client}
                      </Link>
                    </td>
                    <td className="px-5 py-3 text-xs text-muted-foreground">{c.sector}</td>
                    <td className="px-5 py-3"><ScoreBar score={c.reliability_score} /></td>
                    <td className="px-5 py-3"><ClassificationBadge value={c.classification} /></td>
                    <td className="px-5 py-3"><RiskBadge level={riskFromScore(c.reliability_score)} /></td>
                    <td className="px-5 py-3 font-mono text-xs tabular-nums">{c.confidence}%</td>
                    <td className="px-5 py-3 text-right font-mono text-xs tabular-nums">
                      {c.mentions_count.toLocaleString("fr-FR")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
