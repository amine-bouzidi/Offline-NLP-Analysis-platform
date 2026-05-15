export type Classification = "ENGAGER" | "NEUTRE" | "EVITER";
export type RiskLevel = "low" | "medium" | "high";

export interface MentionBreakdown {
  source: string;
  text: string;
  sentiment: number; // -1..1
  date: string; // ISO
  topic_id?: number;
}

export interface Client {
  id: string;
  client: string;
  reliability_score: number; // 0..100
  classification: Classification;
  confidence: number; // 0..100
  mentions_count: number;
  top_keywords: string[];
  breakdown: MentionBreakdown[];
  timeline: { date: string; score: number }[];
  topic_ids: number[];
  sector: string;
}

export interface TopicDetail {
  topic_id: number;
  label: string;
  keywords: string[];
  count: number;
  sentiment: number;
}
