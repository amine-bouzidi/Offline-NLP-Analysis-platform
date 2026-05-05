"""
Module de comparaison des méthodes de Topic Modeling
Compare : LDA (Gensim) vs NMF (sklearn) vs BERTopic (optionnel)

Ce module permet :
  - D'exécuter les 3 méthodes sur le même corpus
  - De comparer les topics extraits
  - De mesurer les métriques de chaque méthode
  - De produire un rapport de comparaison
"""

import warnings
warnings.filterwarnings("ignore")

import time
import json
from typing import List, Dict, Optional

# Nos modules
from lda_topic_modeling import LDATopicModel
from nmf_topic_modeling import NMFTopicModel

# BERTopic (optionnel — Phase 3.1)
try:
    from bertopic import BERTopic
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False

# Sklearn pour métriques supplémentaires
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# ─────────────────────────────────────────────────────────────────
# COMPARATEUR PRINCIPAL
# ─────────────────────────────────────────────────────────────────

class TopicModelComparison:
    """
    Compare LDA, NMF (et optionnellement BERTopic) sur le même corpus.

    Usage :
        comp = TopicModelComparison(num_topics=5)
        comp.fit_all(texts)
        comp.print_comparison()
        comp.export_report("comparison_report.json")
    """

    def __init__(self, num_topics: int = 5):
        self.num_topics = num_topics
        self.texts = None

        # Résultats par méthode
        self.results = {}   # {'lda': {...}, 'nmf': {...}, 'bertopic': {...}}

    # ── Entraînement ───────────────────────────────────────────

    def fit_lda(self, texts: List[str], passes: int = 20) -> Dict:
        """Entraîne LDA et stocke les résultats."""
        print("\n" + "─" * 50)
        print("① LDA (Latent Dirichlet Allocation)")
        print("─" * 50)
        start = time.time()

        lda = LDATopicModel(num_topics=self.num_topics, passes=passes, random_state=42)
        lda.fit(texts)

        elapsed = time.time() - start

        # Métriques
        try:
            coherence = lda.compute_coherence('c_v')
        except Exception:
            coherence = None

        topics = lda.get_topics_dict(num_words=10)
        doc_topics = lda.get_document_topics()
        distribution = lda.corpus_topic_distribution()

        self.results['lda'] = {
            'model': lda,
            'topics': topics,
            'doc_topics': doc_topics,
            'distribution': distribution,
            'metrics': {
                'coherence_cv': round(coherence, 4) if coherence else None,
                'training_time_s': round(elapsed, 2),
                'num_topics': self.num_topics,
                'method': 'Probabilistic (Variational Bayes)',
                'deterministic': False
            }
        }
        print(f"  ⏱ Temps d'entraînement : {elapsed:.1f}s")
        return self.results['lda']

    def fit_nmf(self, texts: List[str]) -> Dict:
        """Entraîne NMF et stocke les résultats."""
        print("\n" + "─" * 50)
        print("② NMF (Non-negative Matrix Factorization)")
        print("─" * 50)
        start = time.time()

        nmf = NMFTopicModel(num_topics=self.num_topics, ngram_range=(1, 2))
        nmf.fit(texts)

        elapsed = time.time() - start

        topics = nmf.get_topics_dict(num_words=10)
        doc_topics = nmf.get_document_topics()
        distribution = nmf.corpus_topic_distribution()
        recon_err = nmf.model.reconstruction_err_
        sparsity = nmf.topic_sparsity()
        diversity = nmf.topic_diversity()

        self.results['nmf'] = {
            'model': nmf,
            'topics': topics,
            'doc_topics': doc_topics,
            'distribution': distribution,
            'metrics': {
                'reconstruction_error': round(recon_err, 4),
                'topic_sparsity': round(sparsity, 4),
                'topic_diversity': round(diversity, 4),
                'training_time_s': round(elapsed, 2),
                'num_topics': self.num_topics,
                'method': 'Algebraic (Matrix Factorization)',
                'deterministic': True
            }
        }
        print(f"  ⏱ Temps d'entraînement : {elapsed:.1f}s")
        return self.results['nmf']

    def fit_bertopic(self, texts: List[str]) -> Optional[Dict]:
        """Entraîne BERTopic si disponible."""
        if not BERTOPIC_AVAILABLE:
            print("\n⚠ BERTopic non disponible. Installez : pip install bertopic sentence-transformers")
            return None

        print("\n" + "─" * 50)
        print("③ BERTopic (Transformer-based)")
        print("─" * 50)
        start = time.time()

        try:
            bt = BERTopic(nr_topics=self.num_topics, language='multilingual',
                          verbose=False)
            doc_labels, probs = bt.fit_transform(texts)
            elapsed = time.time() - start

            # Topics BERTopic
            topic_info = bt.get_topic_info()
            topics = []
            for _, row in topic_info.iterrows():
                if row['Topic'] == -1:   # topic "bruit" dans BERTopic
                    continue
                words = bt.get_topic(row['Topic'])
                if words:
                    topics.append({
                        'id': row['Topic'],
                        'label': " / ".join([w for w, _ in words[:3]]),
                        'words': [(w, round(p, 4)) for w, p in words[:10]],
                        'count': row['Count']
                    })

            doc_topics = [
                {'doc_id': i, 'dominant_topic': label,
                 'topic_label': bt.get_topic_info(label)['Name'].values[0]
                 if label != -1 else 'noise'}
                for i, label in enumerate(doc_labels)
            ]

            self.results['bertopic'] = {
                'model': bt,
                'topics': topics,
                'doc_topics': doc_topics,
                'distribution': {},
                'metrics': {
                    'num_topics_found': len(topics),
                    'noise_docs': sum(1 for l in doc_labels if l == -1),
                    'training_time_s': round(elapsed, 2),
                    'method': 'Transformer + HDBSCAN',
                    'deterministic': False
                }
            }
            print(f"  ⏱ Temps d'entraînement : {elapsed:.1f}s")
            return self.results['bertopic']

        except Exception as e:
            print(f"  ✗ Erreur BERTopic : {e}")
            return None

    def fit_all(self, texts: List[str],
                include_bertopic: bool = False) -> "TopicModelComparison":
        """
        Entraîne toutes les méthodes disponibles.

        Args:
            texts            : liste de textes bruts
            include_bertopic : True pour inclure BERTopic (plus lent)

        Returns:
            self
        """
        self.texts = texts
        print(f"\n{'='*55}")
        print(f"COMPARAISON DE MÉTHODES DE TOPIC MODELING")
        print(f"Corpus : {len(texts)} documents | {self.num_topics} topics")
        print(f"{'='*55}")

        self.fit_lda(texts)
        self.fit_nmf(texts)

        if include_bertopic:
            self.fit_bertopic(texts)

        return self

    # ── Affichage comparatif ────────────────────────────────────

    def print_comparison(self) -> None:
        """Affiche une comparaison côte-à-côte des topics."""
        print("\n" + "=" * 70)
        print("COMPARAISON DES TOPICS — LDA vs NMF")
        print("=" * 70)

        lda_topics = self.results.get('lda', {}).get('topics', [])
        nmf_topics = self.results.get('nmf', {}).get('topics', [])

        n = min(len(lda_topics), len(nmf_topics), self.num_topics)

        for i in range(n):
            print(f"\n{'─'*70}")
            print(f"  TOPIC {i+1}")
            print(f"{'─'*70}")

            if lda_topics:
                t = lda_topics[i]
                top5 = ", ".join([w for w, _ in t['words'][:5]])
                print(f"  LDA [{t['label']:<28}] → {top5}")

            if nmf_topics:
                t = nmf_topics[i]
                top5 = ", ".join([w for w, _ in t['words'][:5]])
                print(f"  NMF [{t['label']:<28}] → {top5}")

        # Chevauchement lexical
        self._print_overlap_analysis(lda_topics, nmf_topics)

    def _print_overlap_analysis(self, lda_topics: List[Dict],
                                 nmf_topics: List[Dict]) -> None:
        """Analyse le chevauchement de vocabulaire entre LDA et NMF."""
        if not lda_topics or not nmf_topics:
            return

        print(f"\n{'─'*70}")
        print("  ANALYSE DU CHEVAUCHEMENT LEXICAL (LDA ∩ NMF)")
        print(f"{'─'*70}")

        lda_sets = [set(w for w, _ in t['words']) for t in lda_topics]
        nmf_sets = [set(w for w, _ in t['words']) for t in nmf_topics]

        all_overlaps = []
        for i, lda_set in enumerate(lda_sets):
            for j, nmf_set in enumerate(nmf_sets):
                overlap = lda_set & nmf_set
                jaccard = len(overlap) / len(lda_set | nmf_set) if (lda_set | nmf_set) else 0
                if overlap:
                    all_overlaps.append((i, j, overlap, jaccard))

        if all_overlaps:
            # Afficher les paires avec le plus de chevauchement
            all_overlaps.sort(key=lambda x: x[3], reverse=True)
            for lda_i, nmf_j, overlap, jaccard in all_overlaps[:5]:
                print(f"  LDA Topic {lda_i+1} ↔ NMF Topic {nmf_j+1} "
                      f"| Jaccard={jaccard:.2f} | Communs: {', '.join(list(overlap)[:5])}")
        else:
            print("  Pas de chevauchement significatif détecté.")

    def print_metrics_table(self) -> None:
        """Affiche un tableau de comparaison des métriques."""
        print("\n" + "=" * 70)
        print("TABLEAU COMPARATIF DES MÉTRIQUES")
        print("=" * 70)

        methods = ['lda', 'nmf', 'bertopic']
        available = [m for m in methods if m in self.results]

        # En-tête
        header = f"{'Critère':<30}"
        for m in available:
            header += f"{'  ' + m.upper():<15}"
        print(f"\n{header}")
        print("─" * 70)

        # Lignes de métriques
        comparisons = [
            ("Méthode", 'method'),
            ("Déterministe ?", 'deterministic'),
            ("Temps (s)", 'training_time_s'),
            ("Cohérence C_V", 'coherence_cv'),
            ("Erreur reconstruction", 'reconstruction_error'),
            ("Diversité topics", 'topic_diversity'),
            ("Sparsité", 'topic_sparsity'),
        ]

        for label, key in comparisons:
            row = f"  {label:<28}"
            has_value = False
            for m in available:
                val = self.results[m]['metrics'].get(key, '—')
                if val is None:
                    val = '—'
                if isinstance(val, bool):
                    val = 'Oui' if val else 'Non'
                elif isinstance(val, float):
                    val = f"{val:.4f}"
                row += f"  {str(val):<13}"
                if val != '—':
                    has_value = True
            if has_value:
                print(row)

        print("\n")

    def print_distribution_comparison(self) -> None:
        """Compare la distribution des topics dans le corpus par méthode."""
        print("\n" + "=" * 70)
        print("DISTRIBUTION DES TOPICS PAR MÉTHODE")
        print("=" * 70)

        for method_name in ['lda', 'nmf']:
            if method_name not in self.results:
                continue
            print(f"\n  {method_name.upper()} :")
            dist = self.results[method_name]['distribution']
            for t_id, info in dist.items():
                bar = "█" * int(info['percentage'] / 3)
                print(f"    Topic {t_id+1} [{info['label']:<25}] "
                      f"{info['percentage']:5.1f}% {bar}")

    # ── Analyse de cohérence des affectations ─────────────────

    def agreement_rate(self) -> Optional[float]:
        """
        Calcule le taux d'accord entre LDA et NMF sur les topics dominants.
        Note : les indices de topics peuvent être différents entre les méthodes,
        donc on compare par rang de probabilité.

        Returns:
            Taux d'accord (0-1) ou None si données insuffisantes
        """
        if 'lda' not in self.results or 'nmf' not in self.results:
            return None

        lda_dt = self.results['lda']['doc_topics']
        nmf_dt = self.results['nmf']['doc_topics']
        n = min(len(lda_dt), len(nmf_dt))

        # Construire des vecteurs de distribution et mesurer la corrélation
        lda_dominant = [d['dominant_topic'] for d in lda_dt[:n]]
        nmf_dominant = [d['dominant_topic'] for d in nmf_dt[:n]]

        # Simple accord direct (les topics peuvent avoir des IDs différents)
        # → on utilise plutôt la corrélation de Spearman sur les rangs
        agreements = sum(1 for a, b in zip(lda_dominant, nmf_dominant) if a == b)
        rate = agreements / n
        return rate

    # ── Visualisation Bubble Chart ──────────────────────────────

    def plot_bubble_comparison(self,
                                filepath: str = "topic_comparison_bubbles.html") -> None:
        """
        Génère un bubble chart interactif (Plotly) comparant la distribution
        des documents entre LDA et NMF.

        Lecture du graphique :
          - Axe X  : Topic LDA dominant (1 → N)
          - Axe Y  : Topic NMF dominant (1 → N)
          - Taille : Nombre de documents à l'intersection (X, Y)
          - Couleur: Proportion de documents à cette intersection
          - Tooltip: Détail des labels LDA + NMF + nombre de docs

        Les bulles sur la diagonale = documents où LDA et NMF sont d'accord.
        Les bulles hors diagonale   = désaccords entre les deux méthodes.

        Args:
            filepath : chemin du fichier HTML de sortie
        """
        if 'lda' not in self.results or 'nmf' not in self.results:
            raise RuntimeError("Appelez fit_all() avant plot_bubble_comparison()")

        try:
            import plotly.graph_objects as go
            import plotly.express as px
        except ImportError:
            print("[Comparaison] ⚠ Installez plotly : pip install plotly")
            return

        print("[Comparaison] Génération du bubble chart LDA vs NMF...")

        # ── Récupération des données ────────────────────────────
        lda_dt   = self.results['lda']['doc_topics']
        nmf_dt   = self.results['nmf']['doc_topics']
        lda_info = self.results['lda']['topics']
        nmf_info = self.results['nmf']['topics']
        n_docs   = min(len(lda_dt), len(nmf_dt))

        # Comptage des intersections (lda_topic, nmf_topic) → nombre de docs
        from collections import defaultdict
        counts = defaultdict(int)
        for i in range(n_docs):
            lda_t = lda_dt[i]['dominant_topic']
            nmf_t = nmf_dt[i]['dominant_topic']
            counts[(lda_t, nmf_t)] += 1

        # Construction des listes pour Plotly
        x_vals, y_vals, sizes, colors, texts = [], [], [], [], []

        for (lda_t, nmf_t), count in counts.items():
            lda_label = lda_info[lda_t]['label'] if lda_t < len(lda_info) else f"Topic {lda_t+1}"
            nmf_label = nmf_info[nmf_t]['label'] if nmf_t < len(nmf_info) else f"Topic {nmf_t+1}"
            pct = round(count / n_docs * 100, 1)

            x_vals.append(lda_t + 1)       # 1-based pour affichage
            y_vals.append(nmf_t + 1)
            sizes.append(count)
            colors.append(pct)
            texts.append(
                f"<b>{count} document{'s' if count > 1 else ''}</b> ({pct}%)<br>"
                f"<br>"
                f"<b>LDA Topic {lda_t+1}</b><br>{lda_label}<br>"
                f"<b>NMF Topic {nmf_t+1}</b><br>{nmf_label}"
            )

        # ── Diagonale d'accord (fond) ───────────────────────────
        diag_max = max(self.num_topics + 1, 2)
        diag_x = list(range(1, diag_max))
        diag_y = list(range(1, diag_max))

        # ── Figure principale ───────────────────────────────────
        fig = go.Figure()

        # Zone diagonale (accord LDA = NMF) en fond
        fig.add_trace(go.Scatter(
            x=diag_x, y=diag_y,
            mode='lines',
            line=dict(color='rgba(100,180,100,0.25)', width=18),
            name='Zone d\'accord LDA = NMF',
            hoverinfo='skip',
            showlegend=True
        ))

        # Bulles principales
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='markers+text',
            marker=dict(
                size=[max(18, s * 7) for s in sizes],   # taille min 18px
                color=colors,
                colorscale='RdYlGn',
                cmin=0,
                cmax=max(colors) if colors else 10,
                colorbar=dict(
                    title=dict(text='% du corpus', side='right'),
                    thickness=15,
                    len=0.6
                ),
                line=dict(color='white', width=1.5),
                opacity=0.88,
                sizemode='diameter',
            ),
            text=[str(s) for s in sizes],
            textposition='middle center',
            textfont=dict(color='white', size=11, family='Arial Black'),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=texts,
            name='Documents',
            showlegend=False
        ))

        # ── Annotations des labels sur les axes ─────────────────
        # Labels axe X (LDA)
        lda_axis_labels = {}
        for t in lda_info:
            top3 = " / ".join(w for w, _ in t['words'][:2])
            lda_axis_labels[t['id'] + 1] = f"T{t['id']+1}<br><sub>{top3}</sub>"

        # Labels axe Y (NMF)
        nmf_axis_labels = {}
        for t in nmf_info:
            top3 = " / ".join(w for w, _ in t['words'][:2])
            nmf_axis_labels[t['id'] + 1] = f"T{t['id']+1}<br><sub>{top3}</sub>"

        tick_vals = list(range(1, self.num_topics + 1))

        # ── Layout ──────────────────────────────────────────────
        fig.update_layout(
            title=dict(
                text=(
                    "<b>Comparaison LDA vs NMF — Distribution des documents par topic</b><br>"
                    "<sup>Taille des bulles = nombre de documents | "
                    "Couleur = % du corpus | "
                    "Diagonale verte = accord entre les deux méthodes</sup>"
                ),
                x=0.5, xanchor='center',
                font=dict(size=16)
            ),
            xaxis=dict(
                title=dict(text='<b>Topic LDA</b>', font=dict(size=14)),
                tickmode='array',
                tickvals=tick_vals,
                ticktext=[lda_axis_labels.get(v, str(v)) for v in tick_vals],
                tickfont=dict(size=10),
                gridcolor='rgba(200,200,200,0.4)',
                range=[0.3, self.num_topics + 0.7],
                showgrid=True,
            ),
            yaxis=dict(
                title=dict(text='<b>Topic NMF</b>', font=dict(size=14)),
                tickmode='array',
                tickvals=tick_vals,
                ticktext=[nmf_axis_labels.get(v, str(v)) for v in tick_vals],
                tickfont=dict(size=10),
                gridcolor='rgba(200,200,200,0.4)',
                range=[0.3, self.num_topics + 0.7],
                showgrid=True,
            ),
            plot_bgcolor='#fafafa',
            paper_bgcolor='white',
            height=680,
            width=900,
            legend=dict(
                orientation='h',
                yanchor='bottom', y=-0.18,
                xanchor='center', x=0.5,
                font=dict(size=11)
            ),
            margin=dict(t=110, b=120, l=130, r=80),
            hoverlabel=dict(
                bgcolor='white',
                bordercolor='#444',
                font=dict(size=12)
            )
        )

        # Sauvegarde HTML
        fig.write_html(
            filepath,
            include_plotlyjs='cdn',
            full_html=True,
            config={'displayModeBar': True, 'scrollZoom': True}
        )
        print(f"[Comparaison] ✓ Bubble chart sauvegardé → {filepath}")
        print(f"               Ouvrez ce fichier dans votre navigateur.")

    # ── Export du rapport ───────────────────────────────────────

    def export_report(self, filepath: str = "topic_comparison_report.json") -> None:
        """
        Exporte le rapport de comparaison en JSON.
        (Les objets modèles sont exclus — seulement les résultats sérialisables)
        """
        report = {
            'corpus_size': len(self.texts) if self.texts else 0,
            'num_topics_requested': self.num_topics,
            'methods': {}
        }

        for method, data in self.results.items():
            report['methods'][method] = {
                'metrics': data['metrics'],
                'topics': [
                    {
                        'id': t['id'],
                        'label': t['label'],
                        'top_words': [w for w, _ in t['words'][:8]]
                    }
                    for t in data['topics']
                ],
                'corpus_distribution': {
                    str(k): v for k, v in data['distribution'].items()
                }
            }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[Comparaison] Rapport exporté → {filepath}")

    # ── Rapport complet ─────────────────────────────────────────

    def full_report(self) -> None:
        """Lance tous les affichages comparatifs."""
        self.print_comparison()
        self.print_metrics_table()
        self.print_distribution_comparison()

        rate = self.agreement_rate()
        if rate is not None:
            print(f"\n  Taux d'accord LDA ↔ NMF (topic dominant) : {rate:.1%}")
            print("  (Note : un désaccord peut indiquer des perspectives complémentaires)")

        self.plot_bubble_comparison("topic_comparison_bubbles.html")


# ─────────────────────────────────────────────────────────────────
# GUIDE COMPARATIF RAPIDE
# ─────────────────────────────────────────────────────────────────

def print_method_guide() -> None:
    """Affiche un guide de sélection des méthodes."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         GUIDE DE SÉLECTION DE LA MÉTHODE DE TOPIC MODELING         ║
╠══════════════════════════════════════════════════════════════════════╣
║  Critère              │  LDA            │  NMF            │ BERTopic ║
║  ─────────────────────┼─────────────────┼─────────────────┼──────── ║
║  Type                 │  Probabiliste   │  Algébrique     │ Deep ML  ║
║  Résultats            │  Stochastiques  │  Déterministes  │ Varie    ║
║  Interprétabilité     │  Bonne          │  Très bonne     │ Bonne    ║
║  Vitesse              │  Moyenne        │  Rapide         │ Lent     ║
║  Petit corpus (<500)  │  OK             │  Recommandé ✓   │ Limité   ║
║  Grand corpus (>5000) │  OK             │  OK             │ Meilleur ║
║  Textes courts        │  Difficile      │  OK             │ Bon      ║
║  Multilingue          │  Selon preproc  │  Selon preproc  │ Natif ✓  ║
║  Num topics fixe ?    │  Oui            │  Oui            │ Non      ║
╠══════════════════════════════════════════════════════════════════════╣
║  RECOMMANDATION : Utilisez les 3 et comparez ! Les topics           ║
║  concordants entre méthodes sont les plus fiables.                  ║
╚══════════════════════════════════════════════════════════════════════╝
""")


# ─────────────────────────────────────────────────────────────────
# DÉMONSTRATION COMPLÈTE
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))

    from corpus_new import get_corpus
    from translation_new import build_translated_corpus
    from preprocessing import TextPreprocessor

    # ── 1. Corpus ────────────────────────────────────────────
    corpus = get_corpus()
    print(f"✓ Corpus KPMG chargé : {len(corpus)} textes")

    # ── 2. Traduction → anglais ───────────────────────────────
    translated = build_translated_corpus(
        corpus,
        batch_size=8,
        cache_file='translated_corpus_cache.json'
    )

    # ── 3. Preprocessing ──────────────────────────────────────
    print("\n[Pipeline] Preprocessing...")
    preprocessor = TextPreprocessor()
    texts = []
    for item in translated:
        result = preprocessor.process(
            item['translated_text'],
            clean_options={'remove_punctuation': True, 'remove_numbers': True},
            detect_language=False,
            remove_stopwords=True
        )
        texts.append(result['cleaned_text'])
    print(f"[Pipeline] ✓ {len(texts)} textes EN prêts pour le topic modeling")

    # ── 4. Afficher le guide ──────────────────────────────────
    print_method_guide()

    # ── 5. Comparaison LDA + NMF ──────────────────────────────
    comp = TopicModelComparison(num_topics=8)
    comp.fit_all(texts, include_bertopic=False)
    comp.full_report()

    # ── 6. Export ────────────────────────────────────────────
    comp.export_report("topic_comparison_report.json")
    comp.results['lda']['model'].export_topics("lda_topics.json")
    comp.results['nmf']['model'].export_topics("nmf_topics.json")

    print("\n" + "=" * 55)
    print("✓ Pipeline complet terminé !")
    print("  Corpus → Traduction EN → Preprocessing → LDA + NMF")
    print("  Fichiers : lda_topics.json | nmf_topics.json | topic_comparison_report.json | topic_comparison_bubbles.html")
    print("=" * 55)