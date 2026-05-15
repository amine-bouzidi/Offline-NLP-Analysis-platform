import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AppLayout } from "@/components/AppLayout";
import { CLIENTS } from "@/lib/mock-data";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

export const Route = createFileRoute("/foulescopie")({
  head: () => ({
    meta: [
      { title: "Foulescopie — InsightGuard" },
      { name: "description", content: "Analyse temporelle de l'évolution de la réputation par client." },
    ],
  }),
  component: FoulescopiePage,
});

const PALETTE = [
  "oklch(0.78 0.15 200)",
  "oklch(0.72 0.18 150)",
  "oklch(0.80 0.16 85)",
  "oklch(0.65 0.22 25)",
  "oklch(0.70 0.16 290)",
];

function FoulescopiePage() {
  const [selected, setSelected] = useState<string[]>(CLIENTS.slice(0, 3).map((c) => c.id));

  const data = CLIENTS[0].timeline.map((p, i) => {
    const point: Record<string, string | number> = { date: p.date.slice(5) };
    selected.forEach((cid) => {
      const c = CLIENTS.find((x) => x.id === cid);
      if (c) point[c.client] = c.timeline[i].score;
    });
    return point;
  });

  function toggle(id: string) {
    setSelected((s) =>
      s.includes(id) ? s.filter((x) => x !== id) : s.length >= 5 ? s : [...s, id],
    );
  }

  return (
    <AppLayout>
      <div className="border-b border-border/60 bg-gradient-to-b from-primary/[0.04] to-transparent">
        <div className="mx-auto max-w-[1600px] px-6 py-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-primary">
            Trend Analysis
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Foulescopie</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Évolution comparée du score de réputation · sélectionnez jusqu'à 5 entités
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-[1600px] grid gap-6 p-6 lg:grid-cols-[280px_1fr]">
        <aside className="space-y-1.5">
          <div className="mb-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Entités ({selected.length}/5)
          </div>
          {CLIENTS.map((c) => {
            const active = selected.includes(c.id);
            const idx = selected.indexOf(c.id);
            return (
              <button
                key={c.id}
                onClick={() => toggle(c.id)}
                className={`flex w-full items-center justify-between rounded-md border px-3 py-2 text-left text-sm transition ${
                  active
                    ? "border-primary/40 bg-primary/5"
                    : "border-border/50 bg-card hover:border-border"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{ background: active ? PALETTE[idx % PALETTE.length] : "oklch(0.35 0.02 240)" }}
                  />
                  <span className={active ? "font-medium" : "text-muted-foreground"}>{c.client}</span>
                </div>
                <span className="font-mono text-[10px] tabular-nums text-muted-foreground">
                  {c.reliability_score}
                </span>
              </button>
            );
          })}
        </aside>

        <div className="rounded-lg border border-border/70 bg-card p-5 shadow-[var(--shadow-card)]">
          <div className="mb-4">
            <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              30 jours · score 0-100
            </div>
            <h3 className="text-base font-semibold">Comparaison temporelle</h3>
          </div>
          <div className="h-[480px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ left: -20, right: 12, top: 8 }}>
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
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                {selected.map((cid, i) => {
                  const c = CLIENTS.find((x) => x.id === cid)!;
                  return (
                    <Line
                      key={cid}
                      type="monotone"
                      dataKey={c.client}
                      stroke={PALETTE[i % PALETTE.length]}
                      strokeWidth={2}
                      dot={false}
                    />
                  );
                })}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
