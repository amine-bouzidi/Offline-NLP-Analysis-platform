"""
clustering.py
Clustering sémantique — Plateforme Due Diligence KPMG
Algorithme : HDBSCAN sur embeddings bge-m3
Note : La pondération AHP sera intégrée après validation avec KPMG.
"""
import os
import sys

# AJOUTER CES LIGNES ICI :
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
    
import json
import numpy as np
from typing import List, Dict, Optional
from collections import Counter
from pathlib import Path

import hdbscan
import umap


# ─────────────────────────────────────────────────────────────
# Chemin de sauvegarde des résultats
# ─────────────────────────────────────────────────────────────
# Utilisation de pathlib pour une meilleure gestion des chemins
BASE_DIR = Path(__file__).parent.parent  # Remonte d'un niveau depuis le dossier courant
OUTPUT_PATH = BASE_DIR / "outputs" / "reports"

# Alternative: chemin absolu si besoin
# OUTPUT_PATH = Path("C:/Users/PC/Documents/PFE/plateforme_analyse_textuelle/outputs/reports")


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
                         text_key: str = 'cleaned_translated_text') -> Dict:
        """
        Analyse le contenu de chaque cluster.
        Utilise cleaned_translated_text (sans stopwords anglais)
        pour des mots-clés représentatifs.
        """
        cluster_ids = sorted(set(labels))
        analysis = {}

        for cluster_id in cluster_ids:
            indices = [i for i, l in enumerate(labels) if l == cluster_id]
            docs = [corpus[i] for i in indices]

            all_words = []
            for doc in docs:
                text = doc.get(text_key, doc.get('translated_text', ''))
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

    import os
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    from sklearn.decomposition import PCA

    from corpus_new import get_corpus
    from preprocessing import TextPreprocessor
    from translation import Translator
    from semantic_encoding import SemanticEncoder

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 0 : Création du dossier de sortie
    # ─────────────────────────────────────────────────────────
    print("=" * 70)
    print("TEST CLUSTERING SUR CORPUS KPMG — DUE DILIGENCE")
    print("Corpus : 100 documents en 5 langues — 8 catégories")
    print("=" * 70)
    
    # Création du dossier de sortie avec pathlib
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    print(f"\n[Init] Dossier de sortie : {OUTPUT_PATH.absolute()}")
    print(f"[Init] Dossier existant : {OUTPUT_PATH.exists()}")
    print(f"[Init] Droits d'écriture : {os.access(OUTPUT_PATH, os.W_OK)}")

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 1 : Chargement corpus
    # ─────────────────────────────────────────────────────────
    corpus_raw = get_corpus()
    print(f"\nCorpus chargé : {len(corpus_raw)} documents")

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 2 : Prétraitement
    # ─────────────────────────────────────────────────────────
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
            'category': item['category'],
            'source_type': item.get('source_type', 'unknown'),
            'expected_language': item['language'],
            'language': result['language'],
            'language_confidence': result['language_confidence'],
            'original_text': item['text'],
            'cleaned_text': result['cleaned_text'],
        })

    for doc in corpus_prep:
        print(f"\nDocument {doc['id']} :")
        print(f"  Catégorie        : {doc['category']}")
        print(f"  Source           : {doc['source_type']}")
        print(f"  Langue attendue  : {doc['expected_language']}")
        print(f"  Langue détectée  : {doc['language']} "
              f"(confiance: {doc['language_confidence']:.0%})")
        print(f"  Original         : {doc['original_text'][:80]}...")
        print(f"  Nettoyé          : {doc['cleaned_text'][:80]}...")

    correct_lang = sum(
        1 for d in corpus_prep
        if d['language'] == d['expected_language']
    )
    print(f"\n--- Résumé prétraitement ---")
    print(f"  Documents traités      : {len(corpus_prep)}")
    print(f"  Détection langue OK    : {correct_lang}/{len(corpus_prep)} "
          f"({correct_lang / len(corpus_prep) * 100:.1f}%)")

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 3 : Traduction → anglais
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ÉTAPE 2 : TRADUCTION → ANGLAIS")
    print("=" * 70)

    translator = Translator()
    corpus_translated = translator.translate_corpus(
        corpus_prep,
        text_key='cleaned_text',
        lang_key='language'
    )

    for doc in corpus_translated:
        print(f"\nDocument {doc['id']} :")
        print(f"  Langue source    : {doc['language']}")
        print(f"  Statut           : {doc['translation_status']}")
        print(f"  Original         : {doc['cleaned_text'][:80]}...")
        print(f"  Traduit (en)     : {doc['translated_text'][:80]}...")

    translated_count = sum(1 for d in corpus_translated if d['was_translated'])
    errors = sum(1 for d in corpus_translated
                 if 'error' in d['translation_status'])
    print(f"\n--- Résumé traduction ---")
    print(f"  Déjà en anglais  : {len(corpus_translated) - translated_count}")
    print(f"  Traduits         : {translated_count}")
    print(f"  Erreurs          : {errors}")

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 4 : Nettoyage post-traduction (stopwords anglais)
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ÉTAPE 2.5 : NETTOYAGE POST-TRADUCTION")
    print("Suppression stopwords anglais pour améliorer les mots-clés")
    print("=" * 70)

    for doc in corpus_translated:
        doc['cleaned_translated_text'] = preprocessor.clean_translated(
            doc['translated_text']
        )

    sample = corpus_translated[0]
    print(f"\nExemple (Document {sample['id']}) :")
    print(f"  Avant : {sample['translated_text'][:100]}...")
    print(f"  Après : {sample['cleaned_translated_text'][:100]}...")
    print(f"\n  Nettoyage post-traduction appliqué sur "
          f"{len(corpus_translated)} documents ✓")

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 5 : Encodage sémantique
    # ─────────────────────────────────────────────────────────
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
    print(f"  Norme moyenne    : "
          f"{np.linalg.norm(embeddings, axis=1).mean():.4f} (~1.0)")

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 6 : Clustering
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ÉTAPE 4 : CLUSTERING HDBSCAN")
    print("=" * 70)

    clusterer = SemanticClusterer(
        min_cluster_size=4,
        min_samples=2,
        reduce_dims=True,
        n_components=15,
    )

    labels = clusterer.fit(embeddings)

    analysis = clusterer.analyze_clusters(
        labels,
        corpus_translated,
        text_key='cleaned_translated_text'
    )

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 7 : Rapport détaillé
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ÉTAPE 5 : RAPPORT DÉTAILLÉ PAR CLUSTER")
    print("=" * 70)

    for cluster_id, info in analysis.items():
        print(f"\n{'─'*70}")
        print(f"{info['label']} — {info['n_documents']} documents")
        print(f"{'─'*70}")
        print(f"  Mots clés : {[w for w, _ in info['top_words'][:7]]}")

        categories = [corpus_translated[i].get('category', '?')
                      for i in info['indices']]
        print(f"  Catégories: {dict(Counter(categories).most_common())}")

        langues = [corpus_translated[i].get('language', '?')
                   for i in info['indices']]
        print(f"  Langues   : {dict(Counter(langues).most_common())}")

        sources = [corpus_translated[i].get('source_type', '?')
                   for i in info['indices']]
        print(f"  Sources   : {dict(Counter(sources).most_common())}")

        print(f"\n  Documents du cluster :")
        for idx in info['indices']:
            doc = corpus_translated[idx]
            print(f"\n    Document {doc['id']} "
                  f"[{doc['category']}] [{doc['language']}] "
                  f"[{doc.get('source_type','?')}]")
            print(f"    Original  : {doc['original_text'][:70]}...")
            print(f"    Traduit   : {doc['translated_text'][:70]}...")

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 8 : Visualisation
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ÉTAPE 6 : VISUALISATION")
    print("=" * 70)

    print("\n[Visualisation] Génération de la carte sémantique...")

    pca = PCA(n_components=2, random_state=42)
    embeddings_2d = pca.fit_transform(embeddings)

    unique_labels = sorted(set(labels))
    colors = cm.tab10(np.linspace(0, 1, len(unique_labels)))
    color_map = {label: colors[i] for i, label in enumerate(unique_labels)}

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    # ── Graphique 1 : par cluster HDBSCAN ──
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

    ax1.set_title("Carte sémantique — par Cluster HDBSCAN",
                  fontsize=13, fontweight='bold')
    ax1.set_xlabel("Composante PCA 1")
    ax1.set_ylabel("Composante PCA 2")
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.4)

    # ── Graphique 2 : par catégorie ──
    ax2 = axes[1]
    categories_list = sorted(set(d.get('category', '?')
                                 for d in corpus_translated))
    cat_colors = cm.tab20(np.linspace(0, 1, len(categories_list)))
    cat_color_map = {cat: cat_colors[i]
                     for i, cat in enumerate(categories_list)}

    for cat in categories_list:
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

    ax2.set_title("Carte sémantique — par Catégorie",
                  fontsize=13, fontweight='bold')
    ax2.set_xlabel("Composante PCA 1")
    ax2.set_ylabel("Composante PCA 2")
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, linestyle='--', alpha=0.4)

    plt.suptitle("Cartographie sémantique — Due Diligence KPMG",
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()

    # Sauvegarde de la figure avec pathlib
    map_path = OUTPUT_PATH / "semantic_map_clusters.png"
    plt.savefig(str(map_path), dpi=150, bbox_inches='tight')
    plt.show()
    print(f"[Visualisation] Carte sauvegardée → {map_path}")

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 9 : Sauvegarde JSON (CORRIGÉE)
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ÉTAPE 7 : SAUVEGARDE JSON")
    print("=" * 70)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int(list(labels).count(-1))

    clustering_results = {
        'metadata': {
            'total_documents': len(corpus_raw),
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'noise_rate': round(n_noise / len(labels) * 100, 1),
            'model': 'BAAI/bge-m3',
            'parameters': {
                'min_cluster_size': 4,
                'min_samples': 2,
                'n_components_umap': 15,
            },
            'languages': dict(Counter(
                d['language'] for d in corpus_prep
            )),
            'categories': dict(Counter(
                d['category'] for d in corpus_prep
            )),
        },
        'clusters': {}
    }

    for cluster_id, info in analysis.items():
        clustering_results['clusters'][str(cluster_id)] = {
            'label': info['label'],
            'n_documents': info['n_documents'],
            'top_keywords': [w for w, _ in info['top_words'][:7]],
            'categories': dict(Counter(
                corpus_translated[i].get('category', '?')
                for i in info['indices']
            )),
            'languages': dict(Counter(
                corpus_translated[i].get('language', '?')
                for i in info['indices']
            )),
            'sources': dict(Counter(
                corpus_translated[i].get('source_type', '?')
                for i in info['indices']
            )),
            'documents': [
                {
                    'id': corpus_translated[i]['id'],
                    'category': corpus_translated[i].get('category', '?'),
                    'language': corpus_translated[i].get('language', '?'),
                    'source_type': corpus_translated[i].get('source_type', '?'),
                    'original_text': corpus_translated[i]['original_text'],
                    'translated_text': corpus_translated[i]['translated_text'],
                    'cluster': int(cluster_id),
                }
                for i in info['indices']
            ]
        }

    # Sauvegarde du fichier JSON avec pathlib et gestion d'erreur
    try:
        json_path = OUTPUT_PATH / "clustering_results.json"
        
        print(f"[JSON] Sauvegarde en cours...")
        print(f"[JSON] Chemin complet : {json_path.absolute()}")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(clustering_results, f, ensure_ascii=False, indent=2)
        
        # Vérification que le fichier a bien été créé
        if json_path.exists():
            file_size = json_path.stat().st_size
            print(f"[JSON] ✓ Résultats sauvegardés avec succès → {json_path}")
            print(f"[JSON] Taille du fichier : {file_size:,} bytes")
        else:
            print(f"[JSON] ✗ ERREUR : Le fichier n'a pas été créé !")
            
    except PermissionError as e:
        print(f"[JSON] ✗ ERREUR DE PERMISSION : {e}")
        print(f"[JSON] Essayez de lancer le script en administrateur ou changez le dossier de sortie")
    except Exception as e:
        print(f"[JSON] ✗ ERREUR INATTENDUE : {e}")
        print(f"[JSON] Type d'erreur : {type(e).__name__}")

    # ─────────────────────────────────────────────────────────
    # ÉTAPE 10 : Sauvegarde alternative (au cas où)
    # ─────────────────────────────────────────────────────────
    # Sauvegarde de secours dans le dossier courant si la première échoue
    if not (OUTPUT_PATH / "clustering_results.json").exists():
        print("\n[JSON] Tentative de sauvegarde de secours...")
        backup_path = Path("./clustering_results_backup.json")
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(clustering_results, f, ensure_ascii=False, indent=2)
            print(f"[JSON] ✓ Sauvegarde de secours → {backup_path.absolute()}")
        except Exception as e:
            print(f"[JSON] ✗ Échec de la sauvegarde de secours : {e}")

    # ─────────────────────────────────────────────────────────
    # RÉSUMÉ FINAL
    # ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("RÉSUMÉ FINAL")
    print("=" * 70)
    print(f"  Documents total     : {len(corpus_raw)}")
    print(f"  Clusters trouvés    : {n_clusters}")
    print(f"  Points bruit        : {n_noise} ({n_noise/len(labels)*100:.1f}%)")
    print(f"  Langues du corpus   : "
          f"{dict(Counter(d['language'] for d in corpus_prep).most_common())}")
    print(f"  Catégories          : "
          f"{dict(Counter(d['category'] for d in corpus_prep).most_common())}")
    print(f"\n  Fichiers générés :")
    
    # Liste tous les fichiers générés
    if OUTPUT_PATH.exists():
        for file in OUTPUT_PATH.glob("*"):
            if file.suffix in ['.png', '.json']:
                print(f"    → {file.name} ({file.stat().st_size:,} bytes)")
    else:
        print(f"    → Aucun fichier trouvé dans {OUTPUT_PATH}")
        
    print("=" * 70)