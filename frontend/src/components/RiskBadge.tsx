import { cn } from "@/lib/utils";
import type { Classification, RiskLevel } from "@/lib/types";

export function RiskBadge({ level, className }: { level: RiskLevel; className?: string }) {
  const map = {
    low: { label: "Faible", cls: "text-risk-low bg-[var(--risk-low-bg)] ring-risk-low/30" },
    medium: { label: "Modéré", cls: "text-risk-medium bg-[var(--risk-medium-bg)] ring-risk-medium/30" },
    high: { label: "Élevé", cls: "text-risk-high bg-[var(--risk-high-bg)] ring-risk-high/30" },
  }[level];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider ring-1",
        map.cls,
        className,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {map.label}
    </span>
  );
}

export function ClassificationBadge({ value }: { value: Classification }) {
  const map: Record<Classification, string> = {
    ENGAGER: "text-risk-low bg-[var(--risk-low-bg)] ring-risk-low/30",
    NEUTRE: "text-risk-medium bg-[var(--risk-medium-bg)] ring-risk-medium/30",
    EVITER: "text-risk-high bg-[var(--risk-high-bg)] ring-risk-high/30",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-widest ring-1",
        map[value],
      )}
    >
      {value}
    </span>
  );
}

export function ScoreBar({ score }: { score: number }) {
  const color =
    score >= 70 ? "bg-risk-low" : score >= 45 ? "bg-risk-medium" : "bg-risk-high";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 overflow-hidden rounded-full bg-muted">
        <div className={cn("h-full rounded-full transition-all", color)} style={{ width: `${score}%` }} />
      </div>
      <span className="font-mono text-xs tabular-nums">{score}</span>
    </div>
  );
}
