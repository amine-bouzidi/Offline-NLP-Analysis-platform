"""
semantic_encoding.py
Encodage vectoriel avec le modèle BAAI/bge-m3
Modèle multilingue haute performance pour le Due Diligence KPMG
"""

import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL = "BAAI/bge-m3"


class SemanticEncoder:
    """
    Encodeur sémantique basé sur bge-m3.
    Transforme les textes en vecteurs denses (embeddings)
    utilisés pour le clustering et la recherche sémantique.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        print(f"[SemanticEncoder] Chargement du modèle {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"[SemanticEncoder] Modèle chargé ✓")

    def encode(self, text: str) -> np.ndarray:
        """Encode un seul texte en vecteur."""
        return self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def encode_batch(self, texts: List[str],
                     batch_size: int = 32,
                     show_progress: bool = True) -> np.ndarray:
        """
        Encode un batch de textes.

        Args:
            texts: Liste de textes à encoder
            batch_size: Taille des lots pour l'encodage
            show_progress: Afficher la progression

        Returns:
            Matrice numpy (n_textes, 1024)
        """
        print(f"\n[SemanticEncoder] Encodage de {len(texts)} textes...")

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )

        print(f"[SemanticEncoder] Encodage terminé — shape: {embeddings.shape}")
        return embeddings

    def encode_corpus(self, corpus: List[Dict],
                      text_key: str = 'translated_text') -> Dict:
        """
        Encode un corpus complet (sortie de translation.py).

        Args:
            corpus: Liste de documents
            text_key: Clé du texte à encoder dans chaque document

        Returns:
            Dict avec embeddings et métadonnées
        """
        texts = [doc.get(text_key, '') for doc in corpus]
        texts = [t if t.strip() else 'no content' for t in texts]

        embeddings = self.encode_batch(texts)

        return {
            'embeddings': embeddings,
            'texts': texts,
            'n_documents': len(texts),
            'embedding_dim': embeddings.shape[1],
            'model': self.model_name,
        }

    def save_embeddings(self, embeddings: np.ndarray,
                        path: str = 'embeddings.npy') -> None:
        """Sauvegarde les embeddings au format numpy."""
        np.save(path, embeddings)
        print(f"[SemanticEncoder] Embeddings sauvegardés → {path}")

    def load_embeddings(self, path: str = 'embeddings.npy') -> np.ndarray:
        """Charge des embeddings précédemment sauvegardés."""
        embeddings = np.load(path)
        print(f"[SemanticEncoder] Embeddings chargés — shape: {embeddings.shape}")
        return embeddings


if __name__ == "__main__":
    encoder = SemanticEncoder()

    texts = [
        "KPMG Algeria is recognized for its high quality audit services.",
        "The company has faced several financial irregularities in recent months.",
        "Employees report a positive work environment and strong leadership.",
        "Multiple clients have complained about delays in service delivery.",
        "KPMG Algeria is expanding its advisory services to new sectors.",
    ]

    print("\n" + "=" * 65)
    print("TEST SEMANTIC ENCODING — DUE DILIGENCE KPMG")
    print("=" * 65)

    embeddings = encoder.encode_batch(texts)
    print(f"\nDimension des embeddings : {embeddings.shape}")
    print(f"Norme d'un vecteur      : {np.linalg.norm(embeddings[0]):.4f} (~1.0)")

    sim_01 = float(np.dot(embeddings[0], embeddings[1]))
    sim_04 = float(np.dot(embeddings[0], embeddings[4]))
    print(f"\nSimilarité texte 1 ↔ texte 2 (thèmes différents) : {sim_01:.4f}")
    print(f"Similarité texte 1 ↔ texte 5 (même entité KPMG)  : {sim_04:.4f}")

    encoder.save_embeddings(embeddings, 'test_embeddings.npy')
