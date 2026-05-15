import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { CLIENTS, TOPICS } from "@/lib/mock-data";

export const Route = createFileRoute("/topics")({
  head: () => ({
    meta: [
      { title: "Topics BERTopic — InsightGuard" },
      { name: "description", content: "Carte des thèmes détectés par BERTopic et exploration croisée des entités liées." },
    ],
  }),
  component: TopicsPage,
});

function TopicsPage() {
  const [selected, setSelected] = useState<number | null>(null);
  const max = Math.max(...TOPICS.map((t) => t.count));

  const linkedClients = selected !== null
    ? CLIENTS.filter((c) => c.topic_ids.includes(selected))
    : [];
  const linkedMentions = selected !== null
    ? CLIENTS.flatMap((c) => c.breakdown.filter((m) => m.topic_id === selected).map((m) => ({ ...m, client: c.client })))
        .slice(0, 12)
    : [];

  return (
    <AppLayout>
      <div className="border-b border-border/60 bg-gradient-to-b from-primary/[0.04] to-transparent">
        <div className="mx-auto max-w-[1600px] px-6 py-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-primary">
            Clustering thématique
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Carte des Thèmes (BERTopic)</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Cliquez sur un thème pour filtrer les entités et mentions associées
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-[1600px] space-y-6 p-6">
        {/* Intertopic map placeholder (BERTopic HTML export) */}
        <div className="rounded-lg border border-dashed border-primary/30 bg-card shadow-[var(--shadow-card)]">
          <div className="flex items-center justify-between border-b border-border/40 px-5 py-3">
            <div>
              <div className="font-mono text-[10px] uppercase tracking-widest text-primary">
                Carte intertopic interactive
              </div>
              <div className="text-sm font-medium">Visualisation BERTopic — projection UMAP</div>
            </div>
            <span className="rounded-md border border-border/60 bg-muted/40 px-2 py-1 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              iframe
            </span>
          </div>
          <div className="relative aspect-[16/7] w-full overflow-hidden rounded-b-lg bg-[radial-gradient(ellipse_at_center,_oklch(0.25_0.04_240)_0%,_transparent_70%)]">
            {/* Replace src with your exported BERTopic visualization HTML (e.g. /bertopic.html) */}
            <iframe
              title="BERTopic intertopic map"
              src="about:blank"
              className="absolute inset-0 h-full w-full"
            />
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <div className="rounded-md border border-border/60 bg-card/80 px-4 py-3 text-center backdrop-blur">
                <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  Emplacement réservé
                </div>
                <div className="mt-1 text-sm">
                  Branchez ici l'export HTML de <code className="font-mono text-primary">topic_model.visualize_topics()</code>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bubble cloud */}
        <div className="rounded-lg border border-border/70 bg-card p-6 shadow-[var(--shadow-card)]">
          <div className="mb-5 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            {TOPICS.length} clusters détectés · taille = volume
          </div>
          <div className="flex flex-wrap items-center gap-3">
            {TOPICS.map((t) => {
              const ratio = t.count / max;
              const size = 0.85 + ratio * 1.4;
              const isSelected = selected === t.topic_id;
              const sentColor =
                t.sentiment > 0.2 ? "ring-risk-low/40 text-risk-low"
                  : t.sentiment < -0.2 ? "ring-risk-high/40 text-risk-high"
                  : "ring-risk-medium/40 text-risk-medium";
              return (
                <button
                  key={t.topic_id}
                  onClick={() => setSelected(isSelected ? null : t.topic_id)}
                  style={{ fontSize: `${size}rem` }}
                  className={`group rounded-full border bg-muted/30 px-5 py-2.5 font-semibold ring-1 transition hover:scale-105 ${sentColor} ${
                    isSelected ? "border-primary bg-primary/10 ring-2 ring-primary" : "border-border/60"
                  }`}
                >
                  {t.label}
                  <span className="ml-2 font-mono text-[10px] font-normal text-muted-foreground">
                    {t.count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Topic detail */}
        {selected !== null && (() => {
          const t = TOPICS.find((x) => x.topic_id === selected)!;
          return (
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="rounded-lg border border-primary/40 bg-card p-5 shadow-[var(--shadow-glow)]">
                <div className="font-mono text-[10px] uppercase tracking-widest text-primary">
                  Topic #{t.topic_id}
                </div>
                <h3 className="mt-1 text-xl font-bold">{t.label}</h3>
                <div className="mt-4 grid grid-cols-2 gap-3">
                  <div className="rounded-md border border-border/50 bg-muted/20 p-3">
                    <div className="font-mono text-[10px] uppercase text-muted-foreground">Volume</div>
                    <div className="text-2xl font-bold tabular-nums">{t.count}</div>
                  </div>
                  <div className="rounded-md border border-border/50 bg-muted/20 p-3">
                    <div className="font-mono text-[10px] uppercase text-muted-foreground">Sentiment</div>
                    <div className={`text-2xl font-bold tabular-nums ${
                      t.sentiment > 0.2 ? "text-risk-low" : t.sentiment < -0.2 ? "text-risk-high" : "text-risk-medium"
                    }`}>
                      {t.sentiment > 0 ? "+" : ""}{t.sentiment.toFixed(2)}
                    </div>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                    Mots-clés
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {t.keywords.map((k) => (
                      <span key={k} className="rounded bg-primary/10 px-2 py-0.5 font-mono text-xs text-primary ring-1 ring-primary/20">
                        {k}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="lg:col-span-2 rounded-lg border border-border/70 bg-card p-5">
                <h4 className="mb-3 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  {linkedClients.length} entité{linkedClients.length > 1 ? "s" : ""} liée{linkedClients.length > 1 ? "s" : ""}
                </h4>
                <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
                  {linkedClients.map((c) => (
                    <Link
                      key={c.id}
                      to="/clients/$clientId"
                      params={{ clientId: c.id }}
                      className="rounded-md border border-border/50 bg-muted/20 p-2.5 transition hover:border-primary/40 hover:bg-muted/40"
                    >
                      <div className="text-sm font-medium">{c.client}</div>
                      <div className="font-mono text-[10px] text-muted-foreground">
                        score {c.reliability_score} · {c.sector}
                      </div>
                    </Link>
                  ))}
                </div>

                <h4 className="mt-6 mb-3 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                  Mentions associées
                </h4>
                <div className="space-y-2">
                  {linkedMentions.map((m, i) => (
                    <div key={i} className="rounded-md border border-border/50 bg-muted/20 p-2.5 text-sm">
                      <div className="font-mono text-[10px] uppercase text-muted-foreground">
                        {m.source} · {m.client}
                      </div>
                      <p className="mt-1">{m.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })()}
      </div>
    </AppLayout>
  );
}
