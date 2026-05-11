"""
Module de synthèse et génération de rapports — Étape 6 : Génération Synthèses
summarization.py

Trois niveaux de synthèse :
  1. Résumés analytiques (par module : sémantique, dynamique, cognitif)
  2. Synthèse globale (une seule page exécutive)
  3. Rapport JSON structuré (données brutes pour intégration)

Utilise FLAN-T5 (2.3B params) ou Mistral 7B (local, open-source).

Usage:
  from summarization import generate_all_syntheses
  
  syntheses = generate_all_syntheses(
      corpus=corpus,
      semantic_results=results_bertopic,
      temporal_results=results_temporal,
      cognitive_results=results_cognitive,
      model_name="google/flan-t5-base"  # ou "mistralai/Mistral-7B-Instruct-v0.1"
  )
  
  # syntheses = {
  #   "semantic_summary": str,
  #   "temporal_summary": str,
  #   "cognitive_summary": str,
  #   "executive_summary": str,
  #   "full_report_json": dict
  # }
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from collections import Counter
from statistics import mean

import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

import numpy as np


# ────────────────────────────────────────────────────────────
# CONSTANTS & CONFIG
# ────────────────────────────────────────────────────────────

# Modèles disponibles (du plus léger au plus puissant)
AVAILABLE_MODELS = {
    "flan-t5-small": {
        "model_id": "google/flan-t5-small",
        "params": "80M",
        "memory": "1GB",
        "latency": "Fast",
        "quality": "⭐⭐"
    },
    "flan-t5-base": {
        "model_id": "google/flan-t5-base",
        "params": "250M",
        "memory": "2GB",
        "latency": "Medium",
        "quality": "⭐⭐⭐"
    },
    "flan-t5-large": {
        "model_id": "google/flan-t5-large",
        "params": "780M",
        "memory": "4GB",
        "latency": "Slow",
        "quality": "⭐⭐⭐⭐"
    },
    "mistral-7b": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.1",
        "params": "7B",
        "memory": "14GB",
        "latency": "Very slow",
        "quality": "⭐⭐⭐⭐⭐"
    }
}

# Prompts de synthèse
PROMPTS = {
    "semantic": """
Analyze the following BERTopic results and provide a concise executive summary:

Topics discovered: {n_topics}
Total documents: {n_docs}
Coverage: {coverage}%

Top topics:
{top_topics}

Provide a 3-paragraph summary covering:
1. Overall topic landscape (diversity, main themes)
2. Key insights from top topics
3. Implications for reputation/risk management
""",

    "temporal": """
Analyze the following temporal dynamics and provide insights:

Time period: {date_range}
Total mentions: {total_mentions}
Press articles: {press_count}
Twitter mentions: {twitter_count}

Activity peaks (z-score ≥ 2.0):
{peaks}

Provide a 3-paragraph summary covering:
1. Overall activity patterns and volatility
2. Major peaks and their timing
3. Media vs social media differences
""",

    "cognitive": """
Analyze the following linguistic indicators:

Average lexical richness (TTR): {avg_ttr}
Average sentence complexity: {avg_sent_len} tokens/sentence
Information density: {avg_info_dens}
Thematic coherence: {avg_coherence}

Provide a 3-paragraph summary covering:
1. Overall discourse complexity
2. Information density patterns
3. Narrative coherence and implications
""",

    "executive": """
Based on comprehensive analysis of media coverage and social media discourse,
provide a one-page executive summary addressing:

1. REPUTATION LANDSCAPE (2-3 sentences)
   - Key themes emerging
   - Overall sentiment tone
   - Major controversies/strengths

2. TEMPORAL DYNAMICS (2-3 sentences)
   - Activity patterns
   - Crisis peaks
   - Media vs public perception alignment

3. DISCOURSE CHARACTERISTICS (2-3 sentences)
   - Information density
   - Narrative complexity
   - Audience engagement level

4. STRATEGIC IMPLICATIONS (2-3 sentences)
   - Key risks identified
   - Opportunities
   - Recommended actions

Analysis data:
{analysis_data}

Generate a professional, concise executive summary suitable for C-level presentation.
""",
}

# Templates JSON
REPORT_TEMPLATE = {
    "metadata": {
        "generated_at": "",
        "model_used": "",
        "corpus_stats": {}
    },
    "semantic_analysis": {
        "summary": "",
        "topics": [],
        "top_keywords": [],
        "key_insights": []
    },
    "temporal_analysis": {
        "summary": "",
        "peaks": [],
        "activity_trends": {},
        "key_dates": []
    },
    "cognitive_analysis": {
        "summary": "",
        "metrics": {},
        "complexity_score": 0,
        "coherence_score": 0
    },
    "executive_summary": "",
    "strategic_recommendations": []
}


# ────────────────────────────────────────────────────────────
# 1. CHARGEMENT DES MODÈLES
# ────────────────────────────────────────────────────────────

class SummarizerPipeline:
    """Pipeline de synthèse avec modèles locaux."""
    
    def __init__(self, model_name: str = "flan-t5-base", device: str = "cpu"):
        """
        Initialise le pipeline.
        
        model_name : clé du dico AVAILABLE_MODELS ou model_id direct
        device : 'cpu' ou 'cuda' (GPU)
        """
        self.model_name = model_name
        self.device = device
        
        # Résoudre le model_id
        if model_name in AVAILABLE_MODELS:
            self.model_id = AVAILABLE_MODELS[model_name]["model_id"]
        else:
            self.model_id = model_name  # Supposé être un model_id direct
        
        print(f"[Loading] {self.model_id} → device={device}")
        
        # Pipeline de résumé/génération
        try:
            self.summarizer = pipeline(
                "summarization",
                model=self.model_id,
                device=0 if device == "cuda" else -1
            )
            print(f"  ✓ Summarizer loaded")
        except Exception as e:
            print(f"  ⚠️  Summarizer failed: {e}")
            self.summarizer = None
        
        # Pipeline de text2text (pour synthèses libres)
        try:
            self.generator = pipeline(
                "text2text-generation",
                model=self.model_id,
                device=0 if device == "cuda" else -1
            )
            print(f"  ✓ Text generator loaded")
        except Exception as e:
            print(f"  ⚠️  Generator failed: {e}")
            self.generator = None
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
    
    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 50,
    ) -> str:
        """Résume un texte (utilise pipeline summarization)."""
        if not self.summarizer:
            return "(Summarizer not available)"
        
        # Truncate si trop long
        tokens = self.tokenizer.encode(text)
        if len(tokens) > 1024:
            text = self.tokenizer.decode(tokens[:1024])
        
        try:
            result = self.summarizer(text, max_length=max_length, min_length=min_length)
            return result[0]["summary_text"]
        except Exception as e:
            print(f"Summarization error: {e}")
            return text[:max_length]
    
    def generate(
        self,
        prompt: str,
        max_length: int = 300,
        min_length: int = 50,
    ) -> str:
        """Génère du texte libre (utilise text2text-generation)."""
        if not self.generator:
            return "(Generator not available)"
        
        # Truncate prompt si trop long
        tokens = self.tokenizer.encode(prompt)
        if len(tokens) > 512:
            prompt = self.tokenizer.decode(tokens[:512])
        
        try:
            result = self.generator(
                prompt,
                max_length=max_length,
                min_length=min_length,
                num_beams=4,
                early_stopping=True
            )
            return result[0]["generated_text"]
        except Exception as e:
            print(f"Generation error: {e}")
            return "(Generation failed)"


# ────────────────────────────────────────────────────────────
# 2. EXTRACTEURS DE DONNÉES (Parsing résultats analyses)
# ────────────────────────────────────────────────────────────

def extract_semantic_context(
    bertopic_results: Dict,
    top_topics_count: int = 5
) -> str:
    """Extrait contexte sémantique pour le prompt."""
    n_topics = bertopic_results.get("n_topics", 0)
    n_docs = bertopic_results.get("n_docs", 0)
    coverage = bertopic_results.get("coverage", 0)
    topics = bertopic_results.get("topics", [])
    
    # Top topics
    top_topics_list = topics[:top_topics_count]
    top_topics_str = "\n".join([
        f"  - Topic {t.get('id', '?')}: {t.get('label', 'Unknown')} "
        f"({t.get('doc_count', 0)} docs, keywords: {', '.join(t.get('keywords', [])[:5])})"
        for t in top_topics_list
    ])
    
    return PROMPTS["semantic"].format(
        n_topics=n_topics,
        n_docs=n_docs,
        coverage=coverage,
        top_topics=top_topics_str
    )


def extract_temporal_context(
    temporal_results: Dict
) -> str:
    """Extrait contexte temporel pour le prompt."""
    date_range = temporal_results.get("date_range", "Unknown")
    total_mentions = temporal_results.get("total_mentions", 0)
    press_count = temporal_results.get("press_count", 0)
    twitter_count = temporal_results.get("twitter_count", 0)
    peaks = temporal_results.get("peaks", {})
    
    # Format peaks
    peaks_str = "\n".join([
        f"  - {month}: {info.get('count', 0)} mentions (z-score: {info.get('z_score', '?')})"
        for month, info in list(peaks.items())[:5]
    ])
    
    return PROMPTS["temporal"].format(
        date_range=date_range,
        total_mentions=total_mentions,
        press_count=press_count,
        twitter_count=twitter_count,
        peaks=peaks_str or "(No significant peaks)"
    )


def extract_cognitive_context(
    cognitive_results: Dict
) -> str:
    """Extrait contexte cognitif pour le prompt."""
    avg_ttr = cognitive_results.get("avg_ttr", 0)
    avg_sent_len = cognitive_results.get("avg_sentence_length", 0)
    avg_info_dens = cognitive_results.get("avg_information_density", 0)
    avg_coherence = cognitive_results.get("avg_coherence", 0)
    
    return PROMPTS["cognitive"].format(
        avg_ttr=f"{avg_ttr:.3f}",
        avg_sent_len=f"{avg_sent_len:.1f}",
        avg_info_dens=f"{avg_info_dens:.3f}",
        avg_coherence=f"{avg_coherence:.3f}"
    )


# ────────────────────────────────────────────────────────────
# 3. GÉNÉRATION DES SYNTHÈSES
# ────────────────────────────────────────────────────────────

def generate_semantic_summary(
    summarizer: SummarizerPipeline,
    bertopic_results: Dict
) -> str:
    """Génère résumé analyse sémantique."""
    prompt = extract_semantic_context(bertopic_results)
    summary = summarizer.generate(prompt, max_length=400, min_length=100)
    return summary


def generate_temporal_summary(
    summarizer: SummarizerPipeline,
    temporal_results: Dict
) -> str:
    """Génère résumé analyse temporelle."""
    prompt = extract_temporal_context(temporal_results)
    summary = summarizer.generate(prompt, max_length=400, min_length=100)
    return summary


def generate_cognitive_summary(
    summarizer: SummarizerPipeline,
    cognitive_results: Dict
) -> str:
    """Génère résumé analyse cognitive."""
    prompt = extract_cognitive_context(cognitive_results)
    summary = summarizer.generate(prompt, max_length=400, min_length=100)
    return summary


def generate_executive_summary(
    summarizer: SummarizerPipeline,
    semantic_summary: str,
    temporal_summary: str,
    cognitive_summary: str,
    corpus_stats: Dict
) -> str:
    """Génère résumé exécutif (une page)."""
    analysis_data = f"""
SEMANTIC ANALYSIS:
{semantic_summary}

TEMPORAL ANALYSIS:
{temporal_summary}

COGNITIVE ANALYSIS:
{cognitive_summary}

CORPUS STATISTICS:
{json.dumps(corpus_stats, indent=2)}
"""
    
    prompt = PROMPTS["executive"].format(analysis_data=analysis_data)
    summary = summarizer.generate(prompt, max_length=600, min_length=200)
    return summary


# ────────────────────────────────────────────────────────────
# 4. CONSTRUCTION RAPPORT JSON
# ────────────────────────────────────────────────────────────

def build_json_report(
    semantic_summary: str,
    temporal_summary: str,
    cognitive_summary: str,
    executive_summary: str,
    corpus_stats: Dict,
    model_used: str,
    results: Dict
) -> Dict:
    """Construit rapport JSON structuré."""
    from datetime import datetime
    
    report = REPORT_TEMPLATE.copy()
    
    # Metadata
    report["metadata"] = {
        "generated_at": datetime.now().isoformat(),
        "model_used": model_used,
        "corpus_stats": corpus_stats
    }
    
    # Analyses
    report["semantic_analysis"]["summary"] = semantic_summary
    report["semantic_analysis"]["topics"] = results.get("topics", [])
    report["semantic_analysis"]["top_keywords"] = results.get("top_keywords", [])
    
    report["temporal_analysis"]["summary"] = temporal_summary
    report["temporal_analysis"]["peaks"] = list(results.get("temporal_peaks", {}).items())
    
    report["cognitive_analysis"]["summary"] = cognitive_summary
    report["cognitive_analysis"]["metrics"] = results.get("cognitive_metrics", {})
    
    report["executive_summary"] = executive_summary
    report["strategic_recommendations"] = extract_recommendations(executive_summary)
    
    return report


def extract_recommendations(executive_summary: str) -> List[str]:
    """
    Extrait les recommandations du résumé exécutif.
    (Simple regex, pourrait être amélioré avec NLP)
    """
    # Chercher patterns comme "Recommend", "Should", "Must"
    lines = executive_summary.split("\n")
    recommendations = []
    for line in lines:
        if any(kw in line.lower() for kw in ["recommend", "should", "must", "suggest"]):
            recommendations.append(line.strip())
    return recommendations


# ────────────────────────────────────────────────────────────
# 5. ORCHESTRATION COMPLÈTE
# ────────────────────────────────────────────────────────────

def generate_all_syntheses(
    corpus: List[Dict],
    semantic_results: Dict,
    temporal_results: Dict,
    cognitive_results: Dict,
    model_name: str = "flan-t5-base",
    device: str = "cpu",
    output_dir: Optional[str] = None
) -> Dict:
    """
    Pipeline complète de génération de synthèses.
    
    Entrées:
      - corpus: liste de documents
      - semantic_results: résultats BERTopic
      - temporal_results: résultats analyse temporelle
      - cognitive_results: résultats indicateurs cognitifs
      - model_name: modèle à utiliser
      - device: 'cpu' ou 'cuda'
      - output_dir: dossier pour sauvegarder (optionnel)
    
    Sorties:
      {
        "semantic_summary": str,
        "temporal_summary": str,
        "cognitive_summary": str,
        "executive_summary": str,
        "full_report_json": dict,
        "status": "success" | "partial" | "error"
      }
    """
    
    print(f"\n{'='*70}")
    print(f"SYNTHÈSE & GÉNÉRATION DE RAPPORTS")
    print(f"{'='*70}")
    
    # 1. Initialiser summarizer
    print(f"\n[1/6] Initialisation du modèle {model_name}…")
    try:
        summarizer = SummarizerPipeline(model_name=model_name, device=device)
    except Exception as e:
        print(f"❌ Erreur chargement modèle: {e}")
        return {"status": "error", "error": str(e)}
    
    # 2. Corpus stats
    print(f"\n[2/6] Extraction statistiques corpus…")
    corpus_stats = {
        "total_documents": len(corpus),
        "date_range": f"{min(d['date'] for d in corpus)} to {max(d['date'] for d in corpus)}",
        "press_articles": sum(1 for d in corpus if d.get("origin") == "press"),
        "twitter_mentions": sum(1 for d in corpus if d.get("origin") == "twitter"),
    }
    print(f"  ✓ {corpus_stats['total_documents']} documents ({corpus_stats['press_articles']} press, {corpus_stats['twitter_mentions']} twitter)")
    
    # 3. Synthèses modulaires
    print(f"\n[3/6] Génération synthèse sémantique…")
    try:
        semantic_summary = generate_semantic_summary(summarizer, semantic_results)
        print(f"  ✓ {len(semantic_summary)} caractères")
    except Exception as e:
        semantic_summary = f"(Error: {e})"
        print(f"  ⚠️  {e}")
    
    print(f"\n[4/6] Génération synthèse temporelle…")
    try:
        temporal_summary = generate_temporal_summary(summarizer, temporal_results)
        print(f"  ✓ {len(temporal_summary)} caractères")
    except Exception as e:
        temporal_summary = f"(Error: {e})"
        print(f"  ⚠️  {e}")
    
    print(f"\n[5/6] Génération synthèse cognitive…")
    try:
        cognitive_summary = generate_cognitive_summary(summarizer, cognitive_results)
        print(f"  ✓ {len(cognitive_summary)} caractères")
    except Exception as e:
        cognitive_summary = f"(Error: {e})"
        print(f"  ⚠️  {e}")
    
    # 4. Résumé exécutif
    print(f"\n[6/6] Génération résumé exécutif…")
    try:
        executive_summary = generate_executive_summary(
            summarizer,
            semantic_summary,
            temporal_summary,
            cognitive_summary,
            corpus_stats
        )
        print(f"  ✓ {len(executive_summary)} caractères")
    except Exception as e:
        executive_summary = f"(Error: {e})"
        print(f"  ⚠️  {e}")
    
    # 5. Rapport JSON
    print(f"\n[7/7] Construction rapport JSON…")
    try:
        full_report = build_json_report(
            semantic_summary,
            temporal_summary,
            cognitive_summary,
            executive_summary,
            corpus_stats,
            model_used=model_name,
            results={
                "topics": semantic_results.get("topics", []),
                "top_keywords": semantic_results.get("top_keywords", []),
                "temporal_peaks": temporal_results.get("peaks", {}),
                "cognitive_metrics": cognitive_results.get("metrics", {})
            }
        )
        print(f"  ✓ Rapport généré")
    except Exception as e:
        full_report = {}
        print(f"  ⚠️  {e}")
    
    # 6. Sauvegarder (optionnel)
    if output_dir:
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Synthèses texte
        with open(f"{output_dir}/semantic_summary.txt", "w", encoding="utf-8") as f:
            f.write(semantic_summary)
        with open(f"{output_dir}/temporal_summary.txt", "w", encoding="utf-8") as f:
            f.write(temporal_summary)
        with open(f"{output_dir}/cognitive_summary.txt", "w", encoding="utf-8") as f:
            f.write(cognitive_summary)
        with open(f"{output_dir}/executive_summary.txt", "w", encoding="utf-8") as f:
            f.write(executive_summary)
        
        # Rapport JSON
        with open(f"{output_dir}/full_report.json", "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n  ✓ Fichiers sauvegardés dans {output_dir}/")
    
    # 7. Résumé final
    print(f"\n{'='*70}")
    print(f"✅ SYNTHÈSES GÉNÉRÉES AVEC SUCCÈS")
    print(f"{'='*70}\n")
    
    return {
        "semantic_summary": semantic_summary,
        "temporal_summary": temporal_summary,
        "cognitive_summary": cognitive_summary,
        "executive_summary": executive_summary,
        "full_report_json": full_report,
        "corpus_stats": corpus_stats,
        "status": "success"
    }


# ────────────────────────────────────────────────────────────
# 6. MAIN (EXEMPLE D'UTILISATION)
# ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    # Données de test (simples)
    test_semantic = {
        "n_topics": 6,
        "n_docs": 100,
        "coverage": 95.6,
        "topics": [
            {
                "id": 0,
                "label": "Environment",
                "doc_count": 12,
                "keywords": ["climate", "environment", "sustainability", "green", "carbon"]
            },
            {
                "id": 1,
                "label": "Health",
                "doc_count": 15,
                "keywords": ["health", "disease", "medical", "treatment", "patient"]
            },
        ]
    }
    
    test_temporal = {
        "date_range": "2021-08 to 2025-01",
        "total_mentions": 850,
        "press_count": 350,
        "twitter_count": 500,
        "peaks": {
            "2023-10": {"count": 120, "z_score": 3.2},
            "2024-08": {"count": 95, "z_score": 2.1},
        }
    }
    
    test_cognitive = {
        "avg_ttr": 0.45,
        "avg_sentence_length": 18.5,
        "avg_information_density": 0.62,
        "avg_coherence": 0.48,
        "metrics": {}
    }
    
    test_corpus = [
        {
            "date": datetime.now().date(),
            "text": "Sample article about environmental concerns and climate change impacts.",
            "origin": "press"
        }
    ]
    
    # Générer synthèses
    results = generate_all_syntheses(
        corpus=test_corpus,
        semantic_results=test_semantic,
        temporal_results=test_temporal,
        cognitive_results=test_cognitive,
        model_name="flan-t5-base",  # ou "flan-t5-small" pour plus rapide
        device="cpu",
        output_dir="outputs_syntheses"
    )
    
    # Afficher résultats
    if results["status"] == "success":
        print("\n📋 EXECUTIVE SUMMARY:")
        print("─" * 70)
        print(results["executive_summary"][:500] + "...")
        print("─" * 70)