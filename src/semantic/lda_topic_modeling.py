"""
Module LDA (Latent Dirichlet Allocation) pour la détection thématique
Utilise Gensim - Méthode probabiliste classique de topic modeling

Principe :
  - LDA suppose que chaque document est un mélange de topics
  - Chaque topic est une distribution de mots
  - L'algorithme apprend ces distributions de façon itérative (MCMC/variational bayes)
"""

import warnings
warnings.filterwarnings("ignore")

import re
import json
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

import numpy as np

# Gensim
from gensim import corpora, models
from gensim.models import CoherenceModel
from gensim.utils import simple_preprocess

# Optionnel - visualisation interactive
try:
    import pyLDAvis
    import pyLDAvis.gensim_models as gensimvis
    PYLDAVIS_AVAILABLE = True
except ImportError:
    PYLDAVIS_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────
# STOPWORDS multilingues légers (sans dépendance NLTK)
# ─────────────────────────────────────────────────────────────────
STOPWORDS = {
    'fr': set(['le', 'la', 'les', 'de', 'des', 'un', 'une', 'et', 'est',
               'en', 'dans', 'sur', 'pour', 'par', 'avec', 'au', 'aux',
               'qui', 'que', 'quoi', 'dont', 'où', 'ou', 'mais', 'donc',
               'ni', 'car', 'il', 'elle', 'ils', 'elles', 'nous', 'vous',
               'on', 'je', 'tu', 'se', 'à', 'du', 'ce', 'si', 'même',
               'plus', 'très', 'bien', 'tout', 'tous', 'aussi', 'plus',
               'cette', 'cet', 'son', 'sa', 'ses', 'leur', 'leurs', 'mon',
               'ma', 'mes', 'ton', 'ta', 'tes', 'notre', 'votre', 'a']),
    'en': set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
               'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are',
               'was', 'were', 'be', 'been', 'have', 'has', 'had',
               'do', 'does', 'did', 'will', 'would', 'shall', 'should',
               'may', 'might', 'can', 'could', 'it', 'its', 'this',
               'that', 'these', 'those', 'they', 'them', 'their',
               'he', 'she', 'we', 'you', 'i', 'my', 'his', 'her', 'our']),
}

# Stopwords combinés (tous ensembles)
ALL_STOPWORDS = set().union(*STOPWORDS.values())


# ─────────────────────────────────────────────────────────────────
# PRÉTRAITEMENT POUR LDA
# ─────────────────────────────────────────────────────────────────

def preprocess_for_lda(texts: List[str],
                        min_token_len: int = 3,
                        extra_stopwords: Optional[set] = None) -> List[List[str]]:
    """
    Transforme une liste de textes bruts en liste de tokens pour LDA.

    Args:
        texts             : liste de chaînes brutes
        min_token_len     : longueur minimale d'un token (défaut 3)
        extra_stopwords   : mots vides supplémentaires

    Returns:
        Liste de listes de tokens [[tok, tok, ...], ...]
    """
    stop = ALL_STOPWORDS.copy()
    if extra_stopwords:
        stop.update(extra_stopwords)

    processed = []
    for text in texts:
        # simple_preprocess : minuscule + supprime ponctuation + tokenise
        tokens = simple_preprocess(text, deacc=True, min_len=min_token_len)
        # Retirer stopwords
        tokens = [t for t in tokens if t not in stop]
        processed.append(tokens)
    return processed


# ─────────────────────────────────────────────────────────────────
# CLASSE PRINCIPALE LDA
# ─────────────────────────────────────────────────────────────────

class LDATopicModel:
    """
    Modèle LDA complet : entraînement, évaluation, inférence, export.

    Usage rapide :
        lda = LDATopicModel(num_topics=5)
        lda.fit(corpus_texts)
        lda.print_topics()
        doc_topics = lda.get_document_topics(corpus_texts)
    """

    def __init__(self,
                 num_topics: int = 5,
                 passes: int = 15,
                 iterations: int = 100,
                 alpha: str = 'auto',
                 eta: str = 'auto',
                 random_state: int = 42,
                 min_token_len: int = 3):
        """
        Args:
            num_topics    : nombre de topics à extraire
            passes        : passes d'entraînement (plus = meilleur, plus lent)
            iterations    : itérations internes par document
            alpha         : prior dirichlet sur les topics par document
                            ('auto' = apprend automatiquement)
            eta           : prior dirichlet sur les mots par topic
                            ('auto' = apprend automatiquement)
            random_state  : graine aléatoire pour reproductibilité
            min_token_len : longueur minimale des tokens
        """
        self.num_topics = num_topics
        self.passes = passes
        self.iterations = iterations
        self.alpha = alpha
        self.eta = eta
        self.random_state = random_state
        self.min_token_len = min_token_len

        # Attributs remplis après fit()
        self.model = None
        self.dictionary = None
        self.corpus_bow = None          # Bag-of-words Gensim
        self.processed_texts = None     # Tokens après prétraitement

    # ── Entraînement ───────────────────────────────────────────

    def fit(self, texts: List[str],
            extra_stopwords: Optional[set] = None) -> "LDATopicModel":
        """
        Entraîne le modèle LDA sur une liste de textes bruts.

        Args:
            texts           : liste de textes
            extra_stopwords : stopwords supplémentaires

        Returns:
            self  (pour chaînage)
        """
        print(f"[LDA] Prétraitement de {len(texts)} documents...")
        self.processed_texts = preprocess_for_lda(
            texts,
            min_token_len=self.min_token_len,
            extra_stopwords=extra_stopwords
        )

        # Filtrer les documents vides
        valid = [(i, t) for i, t in enumerate(self.processed_texts) if t]
        if len(valid) < len(self.processed_texts):
            print(f"  ⚠ {len(self.processed_texts) - len(valid)} documents vides ignorés.")
        idx, self.processed_texts = zip(*valid) if valid else ([], [])
        self.processed_texts = list(self.processed_texts)

        # Dictionnaire Gensim
        print(f"[LDA] Construction du dictionnaire...")
        self.dictionary = corpora.Dictionary(self.processed_texts)
        # Filtrer les tokens très rares (< 2 docs) ou très fréquents (> 90%)
        self.dictionary.filter_extremes(no_below=2, no_above=0.90)

        vocab_size = len(self.dictionary)
        print(f"  Vocabulaire : {vocab_size} termes")

        # Représentation Bag-of-Words
        self.corpus_bow = [
            self.dictionary.doc2bow(doc) for doc in self.processed_texts
        ]

        # Entraînement LDA
        print(f"[LDA] Entraînement ({self.num_topics} topics, {self.passes} passes)...")
        self.model = models.LdaModel(
            corpus=self.corpus_bow,
            id2word=self.dictionary,
            num_topics=self.num_topics,
            random_state=self.random_state,
            passes=self.passes,
            iterations=self.iterations,
            alpha=self.alpha,
            eta=self.eta,
            per_word_topics=True
        )
        print("[LDA] ✓ Entraînement terminé.")
        return self

    # ── Affichage des topics ────────────────────────────────────

    def print_topics(self, num_words: int = 10) -> None:
        """Affiche les topics avec leurs mots-clés."""
        if self.model is None:
            raise RuntimeError("Appelez fit() avant print_topics()")

        print("\n" + "=" * 60)
        print(f"TOPICS LDA ({self.num_topics} topics, top {num_words} mots)")
        print("=" * 60)

        for i in range(self.num_topics):
            words = self.model.show_topic(i, topn=num_words)
            words_str = " | ".join([f"{w} ({p:.3f})" for w, p in words])
            label = self._label_topic(words)
            print(f"\nTopic {i+1:02d} [{label}]")
            print(f"  {words_str}")

    def get_topics_dict(self, num_words: int = 10) -> List[Dict]:
        """
        Retourne les topics sous forme de liste de dicts.

        Returns:
            [{'id': 0, 'label': '...', 'words': [('mot', prob), ...]}, ...]
        """
        if self.model is None:
            raise RuntimeError("Appelez fit() avant get_topics_dict()")

        topics = []
        for i in range(self.num_topics):
            words = self.model.show_topic(i, topn=num_words)
            topics.append({
                'id': i,
                'label': self._label_topic(words),
                'words': [(w, round(p, 4)) for w, p in words]
            })
        return topics

    def _label_topic(self, words: List[Tuple[str, float]]) -> str:
        """Génère un label court à partir des 3 premiers mots."""
        top3 = [w for w, _ in words[:3]]
        return " / ".join(top3)

    # ── Distribution par document ───────────────────────────────

    def get_document_topics(self,
                             texts: Optional[List[str]] = None,
                             minimum_probability: float = 0.05) -> List[Dict]:
        """
        Retourne la distribution thématique de chaque document.

        Args:
            texts               : si None, utilise le corpus d'entraînement
            minimum_probability : seuil pour inclure un topic

        Returns:
            Liste de dicts par document : {dominant_topic, topic_distribution, label}
        """
        if self.model is None:
            raise RuntimeError("Appelez fit() avant get_document_topics()")

        if texts is not None:
            processed = preprocess_for_lda(texts, min_token_len=self.min_token_len)
            bows = [self.dictionary.doc2bow(doc) for doc in processed]
        else:
            bows = self.corpus_bow

        topics_dict = self.get_topics_dict()
        results = []

        for i, bow in enumerate(bows):
            topic_dist = self.model.get_document_topics(
                bow, minimum_probability=minimum_probability
            )
            # Trier par probabilité décroissante
            topic_dist = sorted(topic_dist, key=lambda x: x[1], reverse=True)

            dominant_id = topic_dist[0][0] if topic_dist else 0
            dominant_prob = topic_dist[0][1] if topic_dist else 0.0
            label = topics_dict[dominant_id]['label'] if topic_dist else 'unknown'

            results.append({
                'doc_id': i,
                'dominant_topic': dominant_id,
                'dominant_probability': round(dominant_prob, 4),
                'topic_label': label,
                'full_distribution': {
                    t_id: round(prob, 4) for t_id, prob in topic_dist
                }
            })

        return results

    # ── Métriques de qualité ────────────────────────────────────

    def compute_coherence(self, coherence_type: str = 'c_v') -> float:
        """
        Calcule le score de cohérence du modèle.

        Args:
            coherence_type : 'c_v' (recommandé) | 'u_mass' | 'c_uci'

        Returns:
            Score de cohérence (plus haut = meilleur, typiquement 0.3–0.7)
        """
        if self.model is None:
            raise RuntimeError("Appelez fit() avant compute_coherence()")

        cm = CoherenceModel(
            model=self.model,
            texts=self.processed_texts,
            dictionary=self.dictionary,
            coherence=coherence_type
        )
        score = cm.get_coherence()
        print(f"[LDA] Cohérence ({coherence_type}): {score:.4f}")
        return score

    def compute_perplexity(self) -> float:
        """
        Calcule la perplexité sur le corpus d'entraînement.
        (Plus bas = meilleur, mais ne corrèle pas toujours avec la qualité humaine)
        """
        if self.model is None:
            raise RuntimeError("Appelez fit() avant compute_perplexity()")
        perp = self.model.log_perplexity(self.corpus_bow)
        print(f"[LDA] Log-perplexité : {perp:.4f}")
        return perp

    # ── Recherche du nombre optimal de topics ──────────────────

    @staticmethod
    def find_optimal_topics(texts: List[str],
                             topic_range: range = range(2, 11),
                             passes: int = 10,
                             verbose: bool = True) -> Dict:
        """
        Cherche le nombre optimal de topics par score de cohérence.

        Args:
            texts       : corpus de textes
            topic_range : plage de nombres de topics à tester
            passes      : passes d'entraînement (réduit pour la vitesse)
            verbose     : afficher la progression

        Returns:
            {'best_num_topics': int, 'scores': {n: score, ...}}
        """
        processed = preprocess_for_lda(texts)
        dictionary = corpora.Dictionary(processed)
        dictionary.filter_extremes(no_below=2, no_above=0.90)
        corpus_bow = [dictionary.doc2bow(doc) for doc in processed]

        scores = {}
        best_score = -1
        best_n = topic_range.start

        for n in topic_range:
            lda = models.LdaModel(
                corpus=corpus_bow,
                id2word=dictionary,
                num_topics=n,
                passes=passes,
                random_state=42
            )
            cm = CoherenceModel(
                model=lda,
                texts=processed,
                dictionary=dictionary,
                coherence='c_v'
            )
            score = cm.get_coherence()
            scores[n] = round(score, 4)

            if score > best_score:
                best_score = score
                best_n = n

            if verbose:
                bar = "█" * int(score * 20)
                print(f"  {n:2d} topics | cohérence = {score:.4f} | {bar}")

        print(f"\n[LDA] ✓ Meilleur nombre de topics : {best_n} (cohérence = {best_score:.4f})")
        return {'best_num_topics': best_n, 'scores': scores}

    # ── Export ──────────────────────────────────────────────────

    def export_topics(self, filepath: str = "lda_topics.json") -> None:
        """Sauvegarde les topics dans un fichier JSON."""
        topics = self.get_topics_dict()
        # Convertir les float32 numpy en float Python natif
        for t in topics:
            t['words'] = [(w, float(p)) for w, p in t['words']]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
        print(f"[LDA] Topics exportés → {filepath}")

    def export_pyldavis(self, filepath: str = "lda_visualization.html") -> None:
        """
        Génère la visualisation interactive pyLDAvis.
        Ouvrir le fichier HTML dans un navigateur.
        """
        if not PYLDAVIS_AVAILABLE:
            print("[LDA] ⚠ pyLDAvis non disponible. Installez : pip install pyldavis")
            return

        print("[LDA] Génération de la visualisation pyLDAvis...")
        vis = gensimvis.prepare(self.model, self.corpus_bow, self.dictionary)
        pyLDAvis.save_html(vis, filepath)
        print(f"[LDA] ✓ Visualisation sauvegardée → {filepath}")
        print("       Ouvrez ce fichier dans votre navigateur.")

    # ── Statistiques du corpus ──────────────────────────────────

    def corpus_topic_distribution(self) -> Dict:
        """
        Résume la distribution des topics sur tout le corpus.

        Returns:
            {topic_id: {'count': int, 'percentage': float, 'label': str}}
        """
        doc_topics = self.get_document_topics()
        topic_counts = defaultdict(int)

        for dt in doc_topics:
            topic_counts[dt['dominant_topic']] += 1

        topics_info = self.get_topics_dict()
        total = len(doc_topics)

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


# ─────────────────────────────────────────────────────────────────
# DÉMONSTRATION / TEST
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))

    from corpus_new import get_corpus
    from translation_new import build_translated_corpus, get_english_texts
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
    print("DÉMONSTRATION LDA — Corpus KPMG (EN uniforme)")
    print("="*60)

    # ── 4. Entraînement LDA ───────────────────────────────────
    lda = LDATopicModel(num_topics=8, passes=30, random_state=42)
    lda.fit(texts)

    # ── 5. Topics ─────────────────────────────────────────────
    lda.print_topics(num_words=8)

    # ── 6. Métriques ──────────────────────────────────────────
    print("\n--- Métriques de qualité ---")
    coherence = lda.compute_coherence('c_v')
    lda.compute_perplexity()

    # ── 7. Distribution par document ──────────────────────────
    print("\n--- Exemples de classification ---")
    doc_topics = lda.get_document_topics()
    for dt in doc_topics[:8]:
        preview = translated[dt['doc_id']]['text'][:60]
        print(f"  Doc {dt['doc_id']+1:02d} [{translated[dt['doc_id']]['language'].upper()}] "
              f"→ Topic {dt['dominant_topic']+1} [{dt['topic_label']}] "
              f"({dt['dominant_probability']:.2%})")
        print(f"          \"{preview}...\"")

    # ── 8. Distribution globale ────────────────────────────────
    lda.print_corpus_distribution()

    # ── 9. Export ─────────────────────────────────────────────
    lda.export_topics("lda_topics.json")
    lda.export_pyldavis("lda_visualization.html")

    print("\n✓ Pipeline complet : Corpus → Traduction → Preprocessing → LDA")