"""
similarity.py
Calcul de similarité cosinus et déduplication du corpus
Utilisé après l'encodage sémantique dans le pipeline Due Diligence KPMG
"""

import numpy as np
from typing import List, Dict, Optional
from collections import Counter


class SimilarityEngine:
    """
    Calcul de similarité cosinus entre embeddings et déduplication.
    Les embeddings bge-m3 étant normalisés (L2),
    la similarité cosinus se réduit à un simple produit scalaire.
    """

    def cosine_similarity(self, vec1: np.ndarray,
                          vec2: np.ndarray) -> float:
        """Similarité cosinus entre deux vecteurs."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Calcule la matrice de similarité cosinus complète.

        Args:
            embeddings: Matrice (n, dim) d'embeddings normalisés

        Returns:
            Matrice symétrique (n, n)
        """
        print(f"[Similarity] Calcul matrice ({embeddings.shape[0]}x{embeddings.shape[0]})...")
        matrix = np.dot(embeddings, embeddings.T)
        matrix = np.clip(matrix, -1.0, 1.0)
        print(f"[Similarity] Matrice calculée ✓")
        return matrix

    def find_similar_pairs(self, embeddings: np.ndarray,
                           texts: List[str],
                           threshold: float = 0.85) -> List[Dict]:
        """
        Trouve toutes les paires de textes avec similarité > threshold.

        Args:
            embeddings: Matrice d'embeddings
            texts: Liste des textes correspondants
            threshold: Seuil de similarité

        Returns:
            Liste de paires similaires triées par score décroissant
        """
        matrix = self.similarity_matrix(embeddings)
        n = len(texts)
        pairs = []

        for i in range(n):
            for j in range(i + 1, n):
                sim = matrix[i, j]
                if sim >= threshold:
                    pairs.append({
                        'idx_1': i,
                        'idx_2': j,
                        'text_1': texts[i][:80] + '...',
                        'text_2': texts[j][:80] + '...',
                        'similarity': round(float(sim), 4),
                    })

        pairs.sort(key=lambda x: x['similarity'], reverse=True)
        print(f"[Similarity] {len(pairs)} paires similaires (seuil={threshold})")
        return pairs

    def deduplicate(self, embeddings: np.ndarray,
                    corpus: List[Dict],
                    threshold: float = 0.92,
                    text_key: str = 'translated_text') -> Dict:
        """
        Supprime les doublons sémantiques du corpus.
        En cas de doublon, conserve le premier document trouvé.
        (La pondération sera appliquée dans une phase ultérieure.)

        Args:
            embeddings: Matrice d'embeddings
            corpus: Liste de documents
            threshold: Seuil de similarité pour considérer deux textes comme doublons

        Returns:
            Dict avec corpus dédupliqué, embeddings filtrés et statistiques
        """
        print(f"\n[Similarity] Déduplication (seuil={threshold})...")
        matrix = self.similarity_matrix(embeddings)
        n = len(corpus)
        to_remove = set()

        for i in range(n):
            if i in to_remove:
                continue
            for j in range(i + 1, n):
                if j in to_remove:
                    continue
                if matrix[i, j] >= threshold:
                    to_remove.add(j)  # on garde i, on supprime j

        kept_indices = [i for i in range(n) if i not in to_remove]
        deduplicated_corpus = [corpus[i] for i in kept_indices]
        deduplicated_embeddings = embeddings[kept_indices]

        stats = {
            'original_count': n,
            'removed_count': len(to_remove),
            'kept_count': len(kept_indices),
            'reduction_rate': round(len(to_remove) / n * 100, 1),
        }

        print(f"[Similarity] Documents originaux : {stats['original_count']}")
        print(f"[Similarity] Doublons supprimés  : {stats['removed_count']}")
        print(f"[Similarity] Documents conservés : {stats['kept_count']}")
        print(f"[Similarity] Taux de réduction   : {stats['reduction_rate']}%")

        return {
            'corpus': deduplicated_corpus,
            'embeddings': deduplicated_embeddings,
            'stats': stats,
            'removed_indices': list(to_remove),
        }

    def semantic_search(self, query_embedding: np.ndarray,
                        corpus_embeddings: np.ndarray,
                        corpus: List[Dict],
                        top_k: int = 5,
                        text_key: str = 'translated_text') -> List[Dict]:
        """
        Recherche sémantique : trouve les documents les plus
        proches d'une requête dans le corpus.

        Args:
            query_embedding: Vecteur de la requête
            corpus_embeddings: Embeddings du corpus
            corpus: Liste des documents
            top_k: Nombre de résultats à retourner

        Returns:
            Top-k documents les plus similaires
        """
        scores = np.dot(corpus_embeddings, query_embedding)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            results.append({
                'rank': rank,
                'score': round(float(scores[idx]), 4),
                'text': corpus[idx].get(text_key, '')[:120],
                'document': corpus[idx],
            })

        return results


if __name__ == "__main__":
    print("=" * 65)
    print("TEST SIMILARITY — DUE DILIGENCE KPMG")
    print("=" * 65)

    np.random.seed(42)
    n_docs = 8
    dim = 1024

    base_embeddings = np.random.randn(n_docs, dim)

    # Simuler 2 doublons
    base_embeddings[3] = base_embeddings[1] + np.random.randn(dim) * 0.01
    base_embeddings[6] = base_embeddings[4] + np.random.randn(dim) * 0.01

    norms = np.linalg.norm(base_embeddings, axis=1, keepdims=True)
    embeddings = base_embeddings / norms

    texts = [f"Document {i} — texte sur la réputation KPMG." for i in range(n_docs)]
    corpus = [{'translated_text': t} for t in texts]

    engine = SimilarityEngine()

    matrix = engine.similarity_matrix(embeddings)
    print(f"\nShape matrice        : {matrix.shape}")
    print(f"Diagonale (auto-sim) : {matrix.diagonal().mean():.4f} (~1.0)")

    pairs = engine.find_similar_pairs(embeddings, texts, threshold=0.80)
    print(f"\nPaires détectées : {len(pairs)}")
    for p in pairs[:3]:
        print(f"  Doc {p['idx_1']} ↔ Doc {p['idx_2']} : {p['similarity']:.4f}")

    result = engine.deduplicate(embeddings, corpus, threshold=0.90)
    print(f"\nAprès déduplication : {result['stats']['kept_count']} documents conservés")
