# clustering.py - CORRIGÉ CHEMINS
"""
Clustering sémantique — Plateforme Due Diligence KPMG
"""

import numpy as np
from typing import List, Dict, Optional
from collections import Counter
import sys
import os

# Ajouter parent directory au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import hdbscan
import umap
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.decomposition import PCA

class SemanticClusterer:
    """
    Clustering sémantique avec HDBSCAN.
    Précédé d'une réduction dimensionnelle UMAP.
    """

    def __init__(self,
                 min_cluster_size: int = 5,
                 min_samples: int = 3,
                 reduce_dims: bool = True,
                 n_components: int = 50):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.reduce_dims = reduce_dims
        self.n_components = n_components
        self.clusterer = None
        self.reducer = None

    def _reduce_dimensions(self, embeddings: np.ndarray) -> np.ndarray:
        n_components = min(self.n_components, embeddings.shape[0] - 2)
        print(f"[Clustering] Réduction UMAP "
              f"{embeddings.shape[1]}D → {n_components}D...")
        self.reducer = umap.UMAP(
            n_components=n_components,
            metric='cosine',
            n_neighbors=min(15, embeddings.shape[0] - 1),
            min_dist=0.1,
            random_state=42,
        )
        reduced = self.reducer.fit_transform(embeddings)
        print(f"[Clustering] Réduction terminée ✓")
        return reduced

    def fit(self, embeddings: np.ndarray) -> np.ndarray:
        print(f"\n[Clustering] Début du clustering...")
        print(f"[Clustering] Documents  : {embeddings.shape[0]}")
        print(f"[Clustering] Dimensions : {embeddings.shape[1]}")

        if self.reduce_dims and embeddings.shape[0] > self.n_components:
            embeddings_r = self._reduce_dimensions(embeddings)
        else:
            embeddings_r = embeddings

        print(f"[Clustering] HDBSCAN "
              f"(min_cluster_size={self.min_cluster_size}, "
              f"min_samples={self.min_samples})...")

        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric='euclidean',
            cluster_selection_method='eom',
            prediction_data=True,
        )

        labels = self.clusterer.fit_predict(embeddings_r)

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        print(f"[Clustering] Clusters trouvés  : {n_clusters}")
        print(f"[Clustering] Points bruit      : {n_noise} "
              f"({n_noise / len(labels) * 100:.1f}%)")

        return labels

    def analyze_clusters(self, labels: np.ndarray,
                         corpus: List[Dict],
                         text_key: str = 'translated_text') -> Dict:
        cluster_ids = sorted(set(labels))
        analysis = {}

        for cluster_id in cluster_ids:
            indices = [i for i, l in enumerate(labels) if l == cluster_id]
            docs = [corpus[i] for i in indices]

            all_words = []
            for doc in docs:
                text = doc.get(text_key, '')
                all_words.extend(text.lower().split())

            top_words = Counter(all_words).most_common(10)
            label = "Bruit (non classé)" if cluster_id == -1 else f"Cluster {cluster_id}"

            analysis[cluster_id] = {
                'label': label,
                'n_documents': len(indices),
                'top_words': top_words,
                'indices': indices,
            }

        return analysis


if __name__ == "__main__":
    # Imports locaux APRÈS adjustment du path
    from preprocessing import TextPreprocessor
    from translation import Translator
    from semantic_encoding import SemanticEncoder
    from test_corpus import get_corpus

    print("=" * 70)
    print("TEST CLUSTERING SUR CORPUS RÉEL — DUE DILIGENCE KPMG")
    print("=" * 70)

    corpus_raw = get_corpus()
    print(f"\nCorpus chargé : {len(corpus_raw)} documents")

    print("\n" + "=" * 70)
    print("ÉTAPE 1 : PRÉTRAITEMENT")
    print("=" * 70)

    preprocessor = TextPreprocessor()
    corpus_prep = []

    for item in corpus_raw:
        result = preprocessor.process(
            item['text'],
            detect_language=True,
            remove_stopwords=True
        )
        corpus_prep.append({
            'id': item['id'],
            'category': item.get('category', 'unknown'),
            'expected_language': item['language'],
            'language': result['language'],
            'language_confidence': result['language_confidence'],
            'original_text': item['text'],
            'cleaned_text': result['cleaned_text'],
        })

    correct_lang = sum(
        1 for d in corpus_prep
        if d['language'] == d['expected_language']
    )
    print(f"\n--- Résumé prétraitement ---")
    print(f"  Documents traités      : {len(corpus_prep)}")
    print(f"  Détection langue OK    : {correct_lang}/{len(corpus_prep)} ({correct_lang / len(corpus_prep) * 100:.1f}%)")

    print("\n" + "=" * 70)
    print("ÉTAPE 2 : TRADUCTION → ANGLAIS")
    print("=" * 70)

    translator = Translator()
    corpus_translated = translator.translate_corpus(
        corpus_prep,
        text_key='cleaned_text',
        lang_key='language'
    )

    translated_count = sum(1 for d in corpus_translated if d['was_translated'])
    print(f"\n--- Résumé traduction ---")
    print(f"  Déjà en anglais  : {len(corpus_translated) - translated_count}")
    print(f"  Traduits         : {translated_count}")

    print("\n" + "=" * 70)
    print("ÉTAPE 3 : ENCODAGE SÉMANTIQUE — bge-m3")
    print("=" * 70)

    encoder = SemanticEncoder()
    encoding = encoder.encode_corpus(
        corpus_translated,
        text_key='translated_text'
    )
    embeddings = encoding['embeddings']

    print(f"\n--- Résumé encodage ---")
    print(f"  Shape embeddings : {embeddings.shape}")
    print(f"  Dimension vecteur: {embeddings.shape[1]}")

    print("\n" + "=" * 70)
    print("ÉTAPE 4 : CLUSTERING HDBSCAN")
    print("=" * 70)

    clusterer = SemanticClusterer(
        min_cluster_size=3,
        min_samples=2,
        reduce_dims=True,
        n_components=10,
    )

    labels = clusterer.fit(embeddings)
    analysis = clusterer.analyze_clusters(
        labels,
        corpus_translated,
        text_key='translated_text'
    )

    print("\n" + "=" * 70)
    print("RÉSUMÉ FINAL")
    print("=" * 70)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    print(f"  Documents total    : {len(corpus_raw)}")
    print(f"  Clusters trouvés   : {n_clusters}")
    print(f"  Points bruit       : {n_noise}")
    print("=" * 70)

    print("\n[Visualisation] Génération de la carte sémantique...")

    pca = PCA(n_components=2, random_state=42)
    embeddings_2d = pca.fit_transform(embeddings)

    unique_labels = sorted(set(labels))
    colors = cm.tab10(np.linspace(0, 1, len(unique_labels)))
    color_map = {label: colors[i] for i, label in enumerate(unique_labels)}

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    ax1 = axes[0]
    for label in unique_labels:
        indices = [i for i, l in enumerate(labels) if l == label]
        x = embeddings_2d[indices, 0]
        y = embeddings_2d[indices, 1]
        
        if label == -1:
            cluster_name = "Bruit"
            marker = 'x'
            color = 'gray'
        else:
            cluster_name = f"Cluster {label}"
            marker = 'o'
            color = color_map[label]
        
        ax1.scatter(x, y, label=cluster_name, color=color,
                    marker=marker, s=80, alpha=0.8)
        
        for idx in indices:
            doc_id = corpus_translated[idx].get('id', idx)
            ax1.annotate(str(doc_id),
                         (embeddings_2d[idx, 0], embeddings_2d[idx, 1]),
                         fontsize=7, ha='center', va='bottom')

    ax1.set_title("Carte sémantique — par Cluster HDBSCAN", fontsize=13, fontweight='bold')
    ax1.set_xlabel("Composante PCA 1")
    ax1.set_ylabel("Composante PCA 2")
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.4)

    ax2 = axes[1]
    categories = list(set(d.get('category', '?') for d in corpus_translated))
    cat_colors = cm.tab20(np.linspace(0, 1, len(categories)))
    cat_color_map = {cat: cat_colors[i] for i, cat in enumerate(categories)}

    for cat in categories:
        indices = [i for i, d in enumerate(corpus_translated)
                   if d.get('category', '?') == cat]
        x = embeddings_2d[indices, 0]
        y = embeddings_2d[indices, 1]
        ax2.scatter(x, y, label=cat, color=cat_color_map[cat],
                    s=80, alpha=0.8)
        for idx in indices:
            doc_id = corpus_translated[idx].get('id', idx)
            ax2.annotate(str(doc_id),
                         (embeddings_2d[idx, 0], embeddings_2d[idx, 1]),
                         fontsize=7, ha='center', va='bottom')

    ax2.set_title("Carte sémantique — par Catégorie", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Composante PCA 1")
    ax2.set_ylabel("Composante PCA 2")
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.4)

    plt.suptitle("Cartographie sémantique du corpus — Due Diligence KPMG",
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig("semantic_map_clusters.png", dpi=150, bbox_inches='tight')
    plt.show()
    print("[Visualisation] Carte sauvegardée → semantic_map_clusters.png")