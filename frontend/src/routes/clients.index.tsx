import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Filter, ExternalLink, MessageSquare } from "lucide-react";
import { AppLayout } from "@/components/AppLayout";
import { ClassificationBadge, RiskBadge, ScoreBar } from "@/components/RiskBadge";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { CLIENTS, TOPICS, riskFromScore } from "@/lib/mock-data";
import type { Classification, Client } from "@/lib/types";

export const Route = createFileRoute("/clients/")({
  head: () => ({
    meta: [
      { title: "Analyse de Clients — InsightGuard" },
      { name: "description", content: "Liste des entités analysées avec score de fiabilité, classification et niveau de risque." },
    ],
  }),
  component: ClientsPage,
});

const FILTERS: (Classification | "ALL")[] = ["ALL", "ENGAGER", "NEUTRE", "EVITER"];

function ClientsPage() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("ALL");
  const [verbatim, setVerbatim] = useState<Client | null>(null);

  const filtered = CLIENTS.filter((c) => {
    const matchQ = !query || c.client.toLowerCase().includes(query.toLowerCase()) || c.sector.toLowerCase().includes(query.toLowerCase());
    const matchF = filter === "ALL" || c.classification === filter;
    return matchQ && matchF;
  }).sort((a, b) => b.reliability_score - a.reliability_score);

  return (
    <AppLayout>
      <div className="border-b border-border/60 bg-gradient-to-b from-primary/[0.04] to-transparent">
        <div className="mx-auto max-w-[1600px] px-6 py-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-primary">
            Due Diligence · Clients
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Analyse de Clients</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {filtered.length} entité{filtered.length > 1 ? "s" : ""} affichée{filtered.length > 1 ? "s" : ""}
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-[1600px] space-y-4 p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filtrer par nom ou secteur…"
            className="h-9 max-w-sm bg-muted/50 font-mono text-xs"
          />
          <div className="flex items-center gap-2">
            <Filter className="h-3.5 w-3.5 text-muted-foreground" />
            <div className="flex rounded-md border border-border/60 bg-muted/40 p-0.5">
              {FILTERS.map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`rounded-[4px] px-2.5 py-1 font-mono text-[10px] uppercase tracking-widest transition ${
                    filter === f
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {f === "ALL" ? "Tous" : f}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-border/70 bg-card shadow-[var(--shadow-card)]">
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
                  <th className="px-5 py-2.5 text-left">Mots-clés</th>
                  <th className="px-5 py-2.5 text-right">Mentions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => setVerbatim(c)}
                    className="group cursor-pointer border-b border-border/30 transition hover:bg-muted/30"
                  >
                    <td className="px-5 py-3">
                      <span className="font-medium transition group-hover:text-primary">
                        {c.client}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-xs text-muted-foreground">{c.sector}</td>
                    <td className="px-5 py-3"><ScoreBar score={c.reliability_score} /></td>
                    <td className="px-5 py-3"><ClassificationBadge value={c.classification} /></td>
                    <td className="px-5 py-3"><RiskBadge level={riskFromScore(c.reliability_score)} /></td>
                    <td className="px-5 py-3 font-mono text-xs tabular-nums">{c.confidence}%</td>
                    <td className="px-5 py-3">
                      <div className="flex flex-wrap gap-1">
                        {c.top_keywords.slice(0, 3).map((k) => (
                          <span
                            key={k}
                            className="rounded bg-muted/60 px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground"
                          >
                            {k}
                          </span>
                        ))}
                      </div>
                    </td>
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

      <Sheet open={!!verbatim} onOpenChange={(o) => !o && setVerbatim(null)}>
        <SheetContent side="right" className="w-full sm:max-w-xl overflow-y-auto bg-card">
          {verbatim && (
            <>
              <SheetHeader>
                <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-primary">
                  <MessageSquare className="h-3 w-3" /> Verbatim · sources analysées
                </div>
                <SheetTitle className="text-2xl">{verbatim.client}</SheetTitle>
                <SheetDescription className="flex flex-wrap items-center gap-2">
                  <ClassificationBadge value={verbatim.classification} />
                  <RiskBadge level={riskFromScore(verbatim.reliability_score)} />
                  <span className="font-mono text-xs text-muted-foreground">
                    {verbatim.mentions_count.toLocaleString("fr-FR")} mentions · confiance {verbatim.confidence}%
                  </span>
                </SheetDescription>
              </SheetHeader>

              <div className="mt-5 space-y-4">
                <div>
                  <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    Score de fiabilité
                  </div>
                  <ScoreBar score={verbatim.reliability_score} />
                </div>

                <div>
                  <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    Topics liés
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {verbatim.topic_ids.map((id) => {
                      const t = TOPICS.find((x) => x.topic_id === id);
                      if (!t) return null;
                      return (
                        <span key={id} className="rounded bg-primary/10 px-2 py-0.5 font-mono text-xs text-primary ring-1 ring-primary/20">
                          {t.label}
                        </span>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    Extraits source · tweets & articles
                  </div>
                  <div className="space-y-2">
                    {verbatim.breakdown.map((m, i) => {
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
                              {m.sentiment > 0 ? "+" : ""}{m.sentiment.toFixed(2)}
                            </span>
                          </div>
                          <p className="mt-1.5 text-sm">{m.text}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <Button asChild className="w-full" variant="outline">
                  <Link to="/clients/$clientId" params={{ clientId: verbatim.id }}>
                    Voir la fiche complète <ExternalLink className="ml-1 h-3.5 w-3.5" />
                  </Link>
                </Button>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </AppLayout>
  );
}

