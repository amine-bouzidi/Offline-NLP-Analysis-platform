"""
Module NMF (Non-negative Matrix Factorization) pour la détection thématique
Utilise scikit-learn - Méthode algébrique déterministe

Principe :
  - NMF décompose la matrice TF-IDF (documents × mots) en deux matrices non-négatives
  - W : (documents × topics) — distribution des topics par document
  - H : (topics × mots)       — distribution des mots par topic
  - Contrainte non-négativité → représentations plus interprétables que LDA
  - Résultats déterministes (pas d'aléatoire comme LDA)
"""

import warnings
warnings.filterwarnings("ignore")

import re
import json
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF


# ─────────────────────────────────────────────────────────────────
# STOPWORDS (même base que lda_topic_modeling.py)
# ─────────────────────────────────────────────────────────────────
STOPWORDS_FR = [
    'le', 'la', 'les', 'de', 'des', 'un', 'une', 'et', 'est', 'en',
    'dans', 'sur', 'pour', 'par', 'avec', 'au', 'aux', 'qui', 'que',
    'quoi', 'dont', 'ou', 'mais', 'donc', 'ni', 'car', 'il', 'elle',
    'ils', 'elles', 'nous', 'vous', 'on', 'je', 'tu', 'se', 'si',
    'même', 'plus', 'très', 'bien', 'tout', 'tous', 'aussi', 'cette',
    'cet', 'son', 'sa', 'ses', 'leur', 'leurs', 'mon', 'ma', 'mes',
    'ton', 'ta', 'tes', 'notre', 'votre', 'du', 'ce', 'à', 'a'
]

STOPWORDS_EN = [
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
    'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
    'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'shall', 'should', 'may', 'might', 'can', 'could', 'it',
    'its', 'this', 'that', 'these', 'those', 'they', 'them', 'their',
    'he', 'she', 'we', 'you', 'i', 'my', 'his', 'her', 'our'
]

ALL_STOPWORDS = STOPWORDS_FR + STOPWORDS_EN


# ─────────────────────────────────────────────────────────────────
# CLASSE PRINCIPALE NMF
# ─────────────────────────────────────────────────────────────────

class NMFTopicModel:
    """
    Modèle NMF complet : entraînement, inférence, évaluation, export.

    Avantage vs LDA :
      - Déterministe (résultats reproductibles sans random_state)
      - Rapide même sur grand corpus
      - Topics souvent plus nets (sparse)

    Inconvénient vs LDA :
      - Pas de modèle probabiliste → pas de perplexité
      - Sensible à la vectorisation TF-IDF

    Usage rapide :
        nmf = NMFTopicModel(num_topics=5)
        nmf.fit(corpus_texts)
        nmf.print_topics()
    """

    def __init__(self,
                 num_topics: int = 5,
                 vectorizer_type: str = 'tfidf',
                 max_features: int = 5000,
                 max_df: float = 0.90,
                 min_df: int = 2,
                 ngram_range: Tuple[int, int] = (1, 2),
                 init: str = 'nndsvda',
                 max_iter: int = 500,
                 random_state: int = 42):
        """
        Args:
            num_topics     : nombre de topics
            vectorizer_type: 'tfidf' (recommandé) ou 'count'
            max_features   : taille max du vocabulaire
            max_df         : ignorer les mots présents dans > max_df des docs
            min_df         : ignorer les mots présents dans < min_df docs
            ngram_range    : (1,1) = unigrammes, (1,2) = uni+bigrammes
            init           : initialisation NMF ('nndsvda' recommandé)
            max_iter       : itérations maximales
            random_state   : graine (pour init aléatoire si nécessaire)
        """
        self.num_topics = num_topics
        self.vectorizer_type = vectorizer_type
        self.max_features = max_features
        self.max_df = max_df
        self.min_df = min_df
        self.ngram_range = ngram_range
        self.init = init
        self.max_iter = max_iter
        self.random_state = random_state

        # Attributs post-fit
        self.model = None
        self.vectorizer = None
        self.dtm = None          # Document-Term Matrix (sparse)
        self.feature_names = None

    # ── Vectorisation ───────────────────────────────────────────

    def _build_vectorizer(self):
        """Construit le vectoriseur TF-IDF ou Count."""
        params = dict(
            max_features=self.max_features,
            max_df=self.max_df,
            min_df=self.min_df,
            stop_words=ALL_STOPWORDS,
            ngram_range=self.ngram_range,
            token_pattern=r'\b[a-zA-ZàâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]{3,}\b'
        )
        if self.vectorizer_type == 'tfidf':
            return TfidfVectorizer(sublinear_tf=True, **params)
        else:
            return CountVectorizer(**params)

    # ── Entraînement ────────────────────────────────────────────

    def fit(self, texts: List[str]) -> "NMFTopicModel":
        """
        Entraîne NMF sur une liste de textes bruts.

        Args:
            texts : liste de chaînes

        Returns:
            self (pour chaînage)
        """
        print(f"[NMF] Vectorisation de {len(texts)} documents "
              f"({self.vectorizer_type.upper()}, ngrams={self.ngram_range})...")

        self.vectorizer = self._build_vectorizer()
        self.dtm = self.vectorizer.fit_transform(texts)
        self.feature_names = np.array(self.vectorizer.get_feature_names_out())

        print(f"  Vocabulaire : {self.dtm.shape[1]} termes")
        print(f"  Matrice DTM : {self.dtm.shape[0]} docs × {self.dtm.shape[1]} termes")

        print(f"[NMF] Décomposition en {self.num_topics} topics "
              f"(init={self.init}, max_iter={self.max_iter})...")

        self.model = NMF(
            n_components=self.num_topics,
            init=self.init,
            max_iter=self.max_iter,
            random_state=self.random_state,
            l1_ratio=0.1          # légère regularisation L1 pour la sparsité
        )
        self.model.fit(self.dtm)

        recon_err = self.model.reconstruction_err_
        print(f"[NMF] ✓ Terminé. Erreur de reconstruction : {recon_err:.4f}")
        return self

    # ── Topics ──────────────────────────────────────────────────

    def get_top_words(self, topic_id: int, num_words: int = 10) -> List[Tuple[str, float]]:
        """
        Retourne les mots-clés d'un topic avec leur poids.

        Args:
            topic_id  : index du topic (0-based)
            num_words : nombre de mots

        Returns:
            [(mot, poids), ...]
        """
        if self.model is None:
            raise RuntimeError("Appelez fit() avant get_top_words()")

        topic_row = self.model.components_[topic_id]
        top_indices = topic_row.argsort()[::-1][:num_words]
        return [(self.feature_names[i], round(float(topic_row[i]), 4))
                for i in top_indices]

    def print_topics(self, num_words: int = 10) -> None:
        """Affiche tous les topics avec leurs mots-clés."""
        if self.model is None:
            raise RuntimeError("Appelez fit() avant print_topics()")

        print("\n" + "=" * 60)
        print(f"TOPICS NMF ({self.num_topics} topics, top {num_words} mots)")
        print("=" * 60)

        for i in range(self.num_topics):
            words = self.get_top_words(i, num_words)
            words_str = " | ".join([f"{w} ({p:.3f})" for w, p in words])
            label = self._label_topic(words)
            print(f"\nTopic {i+1:02d} [{label}]")
            print(f"  {words_str}")

    def get_topics_dict(self, num_words: int = 10) -> List[Dict]:
        """
        Retourne les topics sous forme de liste de dicts.

        Returns:
            [{'id': 0, 'label': '...', 'words': [(mot, poids), ...]}, ...]
        """
        topics = []
        for i in range(self.num_topics):
            words = self.get_top_words(i, num_words)
            topics.append({
                'id': i,
                'label': self._label_topic(words),
                'words': words
            })
        return topics

    def _label_topic(self, words: List[Tuple[str, float]]) -> str:
        """Label court = 3 premiers mots."""
        return " / ".join([w for w, _ in words[:3]])

    # ── Distribution par document ───────────────────────────────

    def get_document_topics(self,
                             texts: Optional[List[str]] = None,
                             normalize: bool = True) -> List[Dict]:
        """
        Retourne la distribution thématique de chaque document.

        Args:
            texts     : si None, utilise le corpus d'entraînement
            normalize : normalise les poids pour sommer à 1

        Returns:
            Liste de dicts : {dominant_topic, dominant_weight, topic_label, full_distribution}
        """
        if self.model is None:
            raise RuntimeError("Appelez fit() avant get_document_topics()")

        if texts is not None:
            dtm = self.vectorizer.transform(texts)
        else:
            dtm = self.dtm

        # Matrice W : documents × topics
        W = self.model.transform(dtm)

        if normalize:
            # Normaliser chaque ligne (document) pour sommer à 1
            row_sums = W.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            W = W / row_sums

        topics_dict = self.get_topics_dict()
        results = []

        for i, row in enumerate(W):
            dominant_id = int(np.argmax(row))
            dominant_weight = float(row[dominant_id])
            label = topics_dict[dominant_id]['label']

            results.append({
                'doc_id': i,
                'dominant_topic': dominant_id,
                'dominant_weight': round(dominant_weight, 4),
                'topic_label': label,
                'full_distribution': {
                    j: round(float(row[j]), 4) for j in range(len(row))
                }
            })

        return results

    # ── Métriques ───────────────────────────────────────────────

    def reconstruction_error(self) -> float:
        """
        Retourne l'erreur de reconstruction de la décomposition.
        Plus bas = meilleure factorisation (mais risque d'overfitting si trop bas).
        """
        if self.model is None:
            raise RuntimeError("Appelez fit() avant reconstruction_error()")
        err = self.model.reconstruction_err_
        print(f"[NMF] Erreur de reconstruction : {err:.4f}")
        return err

    def topic_sparsity(self) -> float:
        """
        Mesure la sparsité des topics (% de poids nuls ou proches de 0).
        Une haute sparsité indique des topics bien définis et distincts.
        """
        if self.model is None:
            raise RuntimeError("Appelez fit() avant topic_sparsity()")
        H = self.model.components_
        sparsity = np.mean(H < 0.001)
        print(f"[NMF] Sparsité des topics : {sparsity:.2%}")
        return float(sparsity)

    def topic_diversity(self) -> float:
        """
        Mesure la diversité des topics (0 = tous identiques, 1 = tous différents).
        Basé sur le ratio de mots uniques dans les top-10 de chaque topic.
        """
        top_words_per_topic = [
            set(w for w, _ in self.get_top_words(i, 10))
            for i in range(self.num_topics)
        ]
        all_words = set().union(*top_words_per_topic)
        diversity = len(all_words) / (self.num_topics * 10)
        print(f"[NMF] Diversité des topics : {diversity:.2%}")
        return diversity

    # ── Recherche du nombre optimal ──────────────────────────────

    @staticmethod
    def find_optimal_topics(texts: List[str],
                             topic_range: range = range(2, 11),
                             verbose: bool = True) -> Dict:
        """
        Cherche le nombre optimal de topics en minimisant l'erreur de reconstruction.

        Returns:
            {'best_num_topics': int, 'errors': {n: error, ...}}
        """
        vectorizer = TfidfVectorizer(
            max_features=3000,
            stop_words=ALL_STOPWORDS,
            min_df=2, max_df=0.90,
            token_pattern=r'\b[a-zA-ZàâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]{3,}\b'
        )
        dtm = vectorizer.fit_transform(texts)

        errors = {}
        best_drop = 0
        best_n = topic_range.start

        prev_err = None
        for n in topic_range:
            model = NMF(n_components=n, init='nndsvda',
                        max_iter=300, random_state=42)
            model.fit(dtm)
            err = model.reconstruction_err_
            errors[n] = round(err, 4)

            if prev_err is not None:
                drop = prev_err - err
                if drop > best_drop:
                    best_drop = drop
                    best_n = n - 1   # "coude" avant la chute

            if verbose:
                bar_len = max(0, int(30 - err / max(errors.values()) * 30))
                bar = "█" * bar_len
                print(f"  {n:2d} topics | erreur = {err:.4f} | {bar}")

            prev_err = err

        print(f"\n[NMF] ✓ Meilleur nombre de topics estimé : {best_n}")
        return {'best_num_topics': best_n, 'errors': errors}

    # ── Distribution corpus ──────────────────────────────────────

    def corpus_topic_distribution(self) -> Dict:
        """Distribution des topics dominants dans le corpus."""
        doc_topics = self.get_document_topics()
        topic_counts = defaultdict(int)
        for dt in doc_topics:
            topic_counts[dt['dominant_topic']] += 1

        total = len(doc_topics)
        topics_info = self.get_topics_dict()
        distribution = {}
        for t_id, count in sorted(topic_counts.items()):
            distribution[t_id] = {
                'label': topics_info[t_id]['label'],
                'count': count,
                'percentage': round(count / total * 100, 1)
            }
        return distribution

    def print_corpus_distribution(self) -> None:
        """Affiche la distribution des topics dans le corpus."""
        dist = self.corpus_topic_distribution()
        print("\n--- Distribution des Topics dans le corpus ---")
        for t_id, info in dist.items():
            bar = "█" * int(info['percentage'] / 2)
            print(f"  Topic {t_id+1:02d} [{info['label']:<30}] "
                  f"{info['percentage']:5.1f}% ({info['count']} docs) {bar}")

    # ── Visualisation ────────────────────────────────────────────

    def plot_wordclouds_html(self, filepath: str = "nmf_wordclouds.html",
                              num_words: int = 40) -> None:
        """
        Génère une page HTML interactive (Plotly) avec un nuage de mots
        pour chaque topic NMF.

        Chaque nuage de mots représente les termes les plus importants
        du topic, avec une taille proportionnelle au poids NMF du mot.

        Args:
            filepath  : chemin du fichier HTML de sortie
            num_words : nombre de mots max par nuage (défaut 40)

        Output:
            Fichier HTML ouvrable dans n'importe quel navigateur.
            Contient un nuage de mots par topic, disposés en grille.
        """
        if self.model is None:
            raise RuntimeError("Appelez fit() avant plot_wordclouds_html()")

        try:
            from wordcloud import WordCloud
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            import io, base64
            from PIL import Image
            import numpy as np
        except ImportError as e:
            print(f"[NMF] ⚠ Dépendance manquante : {e}")
            print("  Installez : pip install wordcloud plotly pillow")
            return

        print(f"[NMF] Génération des nuages de mots ({self.num_topics} topics)...")

        # Palette de couleurs — une couleur dominante par topic
        TOPIC_COLORS = [
            "#1f77b4",  # bleu
            "#ff7f0e",  # orange
            "#2ca02c",  # vert
            "#d62728",  # rouge
            "#9467bd",  # violet
            "#8c564b",  # marron
            "#e377c2",  # rose
            "#17becf",  # cyan
            "#bcbd22",  # jaune-vert
            "#7f7f7f",  # gris
        ]

        # Calcul de la grille (ex: 8 topics → 2 lignes × 4 colonnes)
        ncols = min(4, self.num_topics)
        nrows = -(-self.num_topics // ncols)   # division plafond

        fig = make_subplots(
            rows=nrows, cols=ncols,
            subplot_titles=[
                f"Topic {i+1} — {self._label_topic(self.get_top_words(i, 3))}"
                for i in range(self.num_topics)
            ],
            horizontal_spacing=0.05,
            vertical_spacing=0.12
        )

        for topic_id in range(self.num_topics):
            row = topic_id // ncols + 1
            col = topic_id % ncols + 1

            # Mots + poids pour ce topic
            words_weights = self.get_top_words(topic_id, num_words)
            word_freq = {w: float(p) for w, p in words_weights}

            if not word_freq:
                continue

            # Couleur dominante pour ce topic
            base_color = TOPIC_COLORS[topic_id % len(TOPIC_COLORS)]
            hex_color = base_color.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

            def make_colormap(r, g, b):
                """Génère une colormap monochrome autour de la couleur du topic."""
                def colormap(word, font_size, position, orientation, random_state=None, **kwargs):
                    # factor entre 0.4 (mots légers) et 1.0 (mots forts)
                    factor = 0.4 + (font_size / 200) * 0.6
                    # Mélange entre la couleur du topic et le blanc (220,220,220)
                    nr = int(r * factor + (1 - factor) * 220)
                    ng = int(g * factor + (1 - factor) * 220)
                    nb = int(b * factor + (1 - factor) * 220)
                    # Clamp strict 0–255 pour éviter ValueError PIL
                    nr = max(0, min(255, nr))
                    ng = max(0, min(255, ng))
                    nb = max(0, min(255, nb))
                    return f"rgb({nr},{ng},{nb})"
                return colormap

            # Génération du WordCloud en mémoire (image PIL)
            wc = WordCloud(
                width=600,
                height=400,
                background_color='white',
                color_func=make_colormap(r, g, b),
                max_words=num_words,
                prefer_horizontal=0.85,
                collocations=False,
                random_state=topic_id * 7 + 42,
            ).generate_from_frequencies(word_freq)

            # Conversion PIL → base64 PNG pour Plotly
            img_pil = wc.to_image()
            buffer = io.BytesIO()
            img_pil.save(buffer, format='PNG')
            img_b64 = base64.b64encode(buffer.getvalue()).decode()

            # Ajout dans la figure Plotly
            fig.add_trace(
                go.Image(source=f"data:image/png;base64,{img_b64}"),
                row=row, col=col
            )

        # Mise en page globale
        fig.update_layout(
            title={
                'text': f"<b>Nuages de Mots — Topics NMF ({self.num_topics} topics)</b><br>"
                        f"<sup>Taille des mots proportionnelle au poids NMF</sup>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=420 * nrows + 120,
            width=380 * ncols + 60,
            paper_bgcolor='#f8f9fa',
            plot_bgcolor='white',
            showlegend=False,
            margin=dict(t=120, b=40, l=40, r=40)
        )

        # Supprimer les axes (inutiles pour les images)
        fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)

        # Sauvegarder en HTML
        fig.write_html(
            filepath,
            include_plotlyjs='cdn',        # Plotly chargé depuis CDN — fichier léger
            full_html=True,
            config={'displayModeBar': True, 'scrollZoom': True}
        )

        print(f"[NMF] ✓ Nuages de mots sauvegardés → {filepath}")
        print(f"       Ouvrez ce fichier dans votre navigateur.")

    # ── Export ───────────────────────────────────────────────────

    def export_topics(self, filepath: str = "nmf_topics.json") -> None:
        """Sauvegarde les topics dans un fichier JSON."""
        topics = self.get_topics_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
        print(f"[NMF] Topics exportés → {filepath}")


# ─────────────────────────────────────────────────────────────────
# DÉMONSTRATION
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))

    from corpus_new import get_corpus
    from translation_new import build_translated_corpus
    from preprocessing import TextPreprocessor

    # ── 1. Chargement du corpus ────────────────────────────────
    corpus = get_corpus()
    print(f"Corpus KPMG chargé : {len(corpus)} textes")

    # ── 2. Traduction → anglais (avec cache) ──────────────────
    translated = build_translated_corpus(
        corpus,
        batch_size=8,
        cache_file='translated_corpus_cache.json'
    )

    # ── 3. Preprocessing sur les textes anglais ───────────────
    print("\n[Pipeline] Preprocessing des textes traduits...")
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
    print(f"[Pipeline] ✓ {len(texts)} textes prétraités en anglais")

    print("\n" + "="*60)
    print("DÉMONSTRATION NMF — Corpus KPMG (EN uniforme)")
    print("="*60)

    # ── 4. Entraînement NMF ───────────────────────────────────
    nmf = NMFTopicModel(num_topics=8, ngram_range=(1, 2))
    nmf.fit(texts)

    # ── 5. Topics ─────────────────────────────────────────────
    nmf.print_topics(num_words=8)

    # ── 6. Métriques ──────────────────────────────────────────
    print("\n--- Métriques ---")
    nmf.reconstruction_error()
    nmf.topic_sparsity()
    nmf.topic_diversity()

    # ── 7. Distribution par document ──────────────────────────
    print("\n--- Exemples de classification ---")
    doc_topics = nmf.get_document_topics()
    for dt in doc_topics[:8]:
        preview = translated[dt['doc_id']]['text'][:60]
        print(f"  Doc {dt['doc_id']+1:02d} [{translated[dt['doc_id']]['language'].upper()}] "
              f"→ Topic {dt['dominant_topic']+1} [{dt['topic_label']}] "
              f"({dt['dominant_weight']:.2%})")
        print(f"          \"{preview}...\"")

    # ── 8. Distribution globale ────────────────────────────────
    nmf.print_corpus_distribution()

    # ── 9. Visualisation nuages de mots ───────────────────────
    nmf.plot_wordclouds_html("nmf_wordclouds.html", num_words=40)

    # ── 10. Export JSON ───────────────────────────────────────
    nmf.export_topics("nmf_topics.json")

    print("\n✓ Pipeline complet : Corpus → Traduction → Preprocessing → NMF")
    print("  Ouvrez nmf_wordclouds.html dans votre navigateur pour voir les topics.")