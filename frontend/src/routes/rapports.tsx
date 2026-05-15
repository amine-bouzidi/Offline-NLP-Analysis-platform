import { createFileRoute } from "@tanstack/react-router";
import { Download, FileText, Calendar } from "lucide-react";
import { AppLayout } from "@/components/AppLayout";
import { CLIENTS } from "@/lib/mock-data";

export const Route = createFileRoute("/rapports")({
  head: () => ({
    meta: [
      { title: "Rapports — InsightGuard" },
      { name: "description", content: "Rapports de due diligence générés et exports." },
    ],
  }),
  component: RapportsPage,
});

function RapportsPage() {
  const reports = CLIENTS.slice(0, 8).map((c, i) => ({
    id: `RPT-${String(2024100 + i)}`,
    client: c.client,
    date: new Date(Date.now() - i * 4 * 24 * 3600 * 1000).toISOString().slice(0, 10),
    type: i % 2 === 0 ? "Due Diligence complète" : "Veille de réputation",
    pages: 12 + (i % 6),
  }));

  return (
    <AppLayout>
      <div className="border-b border-border/60 bg-gradient-to-b from-primary/[0.04] to-transparent">
        <div className="mx-auto max-w-[1600px] px-6 py-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-primary">
            Exports & livrables
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Rapports</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Rapports générés à partir du pipeline NLP (NLTK + BERTopic)
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-[1600px] p-6">
        <div className="rounded-lg border border-border/70 bg-card shadow-[var(--shadow-card)]">
          {reports.map((r, i) => (
            <div
              key={r.id}
              className={`flex items-center gap-4 p-4 transition hover:bg-muted/30 ${
                i !== reports.length - 1 ? "border-b border-border/40" : ""
              }`}
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 ring-1 ring-primary/20">
                <FileText className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{r.client}</span>
                  <span className="rounded bg-muted/60 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    {r.id}
                  </span>
                </div>
                <div className="mt-0.5 flex items-center gap-3 font-mono text-[11px] text-muted-foreground">
                  <span>{r.type}</span>
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {r.date}
                  </span>
                  <span>{r.pages} pages</span>
                </div>
              </div>
              <button className="inline-flex items-center gap-1.5 rounded-md border border-border/60 bg-muted/40 px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider text-muted-foreground transition hover:border-primary/40 hover:text-primary">
                <Download className="h-3 w-3" />
                PDF
              </button>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
