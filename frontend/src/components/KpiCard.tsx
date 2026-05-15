import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface KpiCardProps {
  label: string;
  value: string | number;
  delta?: string;
  deltaTone?: "up" | "down" | "neutral";
  icon: LucideIcon;
  hint?: string;
  accent?: "primary" | "low" | "medium" | "high";
}

export function KpiCard({ label, value, delta, deltaTone = "neutral", icon: Icon, hint, accent = "primary" }: KpiCardProps) {
  const accentMap = {
    primary: "text-primary bg-primary/10 ring-primary/20",
    low: "text-risk-low bg-[var(--risk-low-bg)] ring-risk-low/20",
    medium: "text-risk-medium bg-[var(--risk-medium-bg)] ring-risk-medium/20",
    high: "text-risk-high bg-[var(--risk-high-bg)] ring-risk-high/20",
  };
  const deltaCls = {
    up: "text-risk-low",
    down: "text-risk-high",
    neutral: "text-muted-foreground",
  }[deltaTone];

  return (
    <div className="group relative overflow-hidden rounded-lg border border-border/70 bg-card p-5 shadow-[var(--shadow-card)] transition hover:border-primary/40">
      <div className="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent opacity-0 transition group-hover:opacity-100" />
      <div className="flex items-start justify-between">
        <div className="space-y-1.5">
          <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">{label}</div>
          <div className="text-3xl font-bold tracking-tight tabular-nums">{value}</div>
          {hint && <div className="text-xs text-muted-foreground">{hint}</div>}
        </div>
        <div className={cn("rounded-md p-2 ring-1", accentMap[accent])}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      {delta && (
        <div className="mt-4 flex items-center gap-2 border-t border-border/50 pt-3">
          <span className={cn("font-mono text-xs font-semibold", deltaCls)}>{delta}</span>
          <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">vs 30j</span>
        </div>
      )}
    </div>
  );
}
