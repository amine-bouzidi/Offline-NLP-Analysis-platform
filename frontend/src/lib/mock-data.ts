import type { Client, TopicDetail, Classification, RiskLevel } from "./types";

export const TOPICS: TopicDetail[] = [
  { topic_id: 0, label: "Service Client", keywords: ["support", "réponse", "attente", "qualité"], count: 142, sentiment: -0.2 },
  { topic_id: 1, label: "Scandale Financier", keywords: ["fraude", "enquête", "amf", "sanction"], count: 87, sentiment: -0.78 },
  { topic_id: 2, label: "Innovation Produit", keywords: ["lancement", "ia", "innovation", "tech"], count: 213, sentiment: 0.65 },
  { topic_id: 3, label: "Supply Chain", keywords: ["logistique", "retard", "fournisseur", "rupture"], count: 96, sentiment: -0.35 },
  { topic_id: 4, label: "Problèmes Techniques", keywords: ["bug", "panne", "incident", "downtime"], count: 121, sentiment: -0.55 },
  { topic_id: 5, label: "Gouvernance", keywords: ["ceo", "conseil", "stratégie", "direction"], count: 78, sentiment: 0.15 },
  { topic_id: 6, label: "ESG & Durabilité", keywords: ["climat", "carbone", "rse", "durable"], count: 154, sentiment: 0.42 },
  { topic_id: 7, label: "Résultats Financiers", keywords: ["revenus", "ebitda", "trimestre", "guidance"], count: 189, sentiment: 0.31 },
];

const SECTORS = ["Banque", "Tech", "Énergie", "Retail", "Santé", "Industrie"];
const NAMES = [
  "Apex Capital", "Helios Energy", "NovaTech Industries", "Meridian Bank",
  "Vertex Pharma", "Lumen Retail", "Atlas Logistics", "Solstice Media",
  "Polaris Insurance", "Quantum Systems", "Orion Telecom", "Verdant Foods",
];

function seedRand(seed: number) {
  return () => {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  };
}

function classify(score: number): Classification {
  if (score >= 70) return "ENGAGER";
  if (score >= 45) return "NEUTRE";
  return "EVITER";
}

export function riskFromScore(score: number): RiskLevel {
  if (score >= 70) return "low";
  if (score >= 45) return "medium";
  return "high";
}

export const CLIENTS: Client[] = NAMES.map((name, i) => {
  const rand = seedRand(i + 7);
  const score = Math.round(25 + rand() * 70);
  const sentiment = (score - 50) / 50;
  const topicCount = 2 + Math.floor(rand() * 3);
  const topic_ids = Array.from({ length: topicCount }, () => Math.floor(rand() * TOPICS.length));
  const keywords = Array.from(new Set(topic_ids.flatMap((id) => TOPICS[id].keywords))).slice(0, 6);
  const mentions_count = 50 + Math.floor(rand() * 450);

  const timeline = Array.from({ length: 30 }, (_, d) => {
    const noise = (rand() - 0.5) * 18;
    const trend = Math.sin(d / 5 + i) * 8;
    return {
      date: new Date(Date.now() - (29 - d) * 24 * 3600 * 1000).toISOString().slice(0, 10),
      score: Math.max(5, Math.min(95, Math.round(score + noise + trend))),
    };
  });

  const breakdown = Array.from({ length: 8 }, (_, k) => {
    const tid = topic_ids[k % topic_ids.length];
    const samples = [
      `Forte couverture presse autour de ${TOPICS[tid].label.toLowerCase()} chez ${name}.`,
      `Signal négatif détecté concernant ${TOPICS[tid].keywords[0]} — à surveiller.`,
      `Communication officielle de ${name} sur ${TOPICS[tid].keywords[1] ?? "la stratégie"}.`,
      `Analystes divisés sur ${name} : ${TOPICS[tid].keywords[2] ?? "perspectives"}.`,
    ];
    return {
      source: ["Reuters", "Bloomberg", "Twitter", "Les Échos", "FT"][k % 5],
      text: samples[k % samples.length],
      sentiment: Math.max(-1, Math.min(1, sentiment + (rand() - 0.5) * 0.6)),
      date: new Date(Date.now() - k * 36 * 3600 * 1000).toISOString(),
      topic_id: tid,
    };
  });

  return {
    id: `cli_${i + 1}`,
    client: name,
    reliability_score: score,
    classification: classify(score),
    confidence: 60 + Math.round(rand() * 35),
    mentions_count,
    top_keywords: keywords,
    breakdown,
    timeline,
    topic_ids,
    sector: SECTORS[i % SECTORS.length],
  };
});

export function getClient(id: string) {
  return CLIENTS.find((c) => c.id === id);
}
