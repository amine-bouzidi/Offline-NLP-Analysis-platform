# bertopic_analysis_csv.py - VERSION CORRIGÉE
"""
Pipeline BERTopic multilingue avec corpus CSV en entrée.
Génère tous les outputs: HTML, JSON, CSV, PNG
CORRECTION: Gestion robuste du chemin CSV
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

import hdbscan
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import umap
from bertopic import BERTopic
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer

# Imports locaux
try:
    from preprocessing import ENGLISH_STOPWORDS_EXTENDED, TextPreprocessor
except:
    from src.preprocessing.preprocessing import TextPreprocessor
    ENGLISH_STOPWORDS_EXTENDED = set()

try:
    from semantic_encoding import SemanticEncoder
except:
    from src.semantic.semantic_encoding import SemanticEncoder

try:
    from similarity import SimilarityEngine
except:
    from src.semantic.similarity import SimilarityEngine

try:
    from translation_new import Translator
except:
    from src.semantic.translation import Translator


# =============================================================
# CONFIGURATION
# =============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n📁 OUTPUT DIR: {OUTPUT_DIR.absolute()}")


# =============================================================
# LOAD CSV CORPUS - VERSION CORRIGÉE
# =============================================================

def load_corpus_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """
    Charge corpus depuis fichier CSV.
    CORRECTION: Gère les chemins avec r"..." correctement
    """
    
    # Nettoyer le path
    csv_path = str(csv_path).strip()
    
    # Enlever les guillemets (simples ou doubles)
    if csv_path.startswith('"') and csv_path.endswith('"'):
        csv_path = csv_path[1:-1]
    if csv_path.startswith("'") and csv_path.endswith("'"):
        csv_path = csv_path[1:-1]
    
    # Enlever le préfixe 'r' si présent
    if csv_path.startswith("r'") or csv_path.startswith('r"'):
        csv_path = csv_path[2:-1]
    
    # Vérifier que ce n'est pas un chemin avec le 'r' literal
    if csv_path.startswith("r"):
        csv_path = csv_path[1:].strip('"').strip("'")
    
    csv_path = csv_path.strip()
    
    print(f"\n[📂] Chargement CSV...")
    print(f"    Chemin fourni: {csv_path}")
    
    csv_path_obj = Path(csv_path)
    
    print(f"    Chemin absolu: {csv_path_obj.absolute()}")
    print(f"    Existe: {csv_path_obj.exists()}")
    
    if not csv_path_obj.exists():
        print(f"\n❌ ERREUR: Fichier CSV non trouvé!")
        print(f"\n💡 SOLUTIONS:")
        print(f"   1. Vérifier le chemin exactement (lettres minuscules/majuscules)")
        print(f"   2. IMPORTANT: Ne PAS taper r\"...\" ni d'autres guillemets")
        print(f"   3. Format correct:")
        print(f"      C:\\Users\\GAB Informatique\\Documents\\Master 2\\PFE\\plateforme_analyse_textuelle\\datasets\\tweets_apple_20260501_135633.csv")
        print(f"   4. Ou chemin relatif:")
        print(f"      datasets/tweets_apple_20260501_135633.csv")
        print(f"\n   Fichiers disponibles dans datasets/:")
        
        datasets_dir = Path("datasets")
        if datasets_dir.exists():
            csv_files = list(datasets_dir.glob("*.csv"))
            if csv_files:
                for f in csv_files[:10]:
                    print(f"      • {f}")
            else:
                print(f"      (aucun CSV trouvé)")
        else:
            print(f"      (dossier datasets/ non trouvé)")
        
        raise FileNotFoundError(f"CSV non trouvé: {csv_path}")
    
    print(f"    ✓ Fichier trouvé!")
    
    try:
        df = pd.read_csv(csv_path_obj)
    except Exception as e:
        print(f"\n❌ ERREUR lecture CSV: {e}")
        raise
    
    print(f"    ✓ {len(df)} lignes chargées")
    print(f"    ✓ Colonnes: {list(df.columns)}")
    
    corpus = []
    for idx, row in df.iterrows():
        corpus.append({
            "id": row.get("id", str(idx)) if "id" in df.columns else str(idx),
            "text": str(row.get("text", "")),
            "category": str(row.get("category", "unknown")) if "category" in df.columns else "unknown",
            "language": str(row.get("language", "en")) if "language" in df.columns else "en",
            "source_type": str(row.get("source_type", "csv")) if "source_type" in df.columns else "csv",
        })
    
    return corpus


# =============================================================
# UTILITAIRES
# =============================================================

def auto_topic_name(topic_words: List[tuple], top_n: int = 3) -> str:
    """Crée un nom lisible à partir des top mots d'un topic."""
    if not topic_words:
        return "Unlabeled Topic"
    words = [w.replace("_", " ").strip() for w, _ in topic_words[:top_n]]
    words = [w for w in words if w]
    if not words:
        return "Unlabeled Topic"
    return " / ".join(word.title() for word in words)


# =============================================================
# PREPROCESSING ET TRADUCTION
# =============================================================

def preprocess_and_translate(corpus_raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prétraitement + Traduction."""
    
    print("\n" + "="*70)
    print("ÉTAPE 1 : PRÉTRAITEMENT")
    print("="*70)
    
    preprocessor = TextPreprocessor()
    corpus_prep = []
    
    for i, item in enumerate(corpus_raw):
        if (i + 1) % max(1, len(corpus_raw) // 10) == 0:
            print(f"  Prétraitement: {i+1}/{len(corpus_raw)}")
        
        result = preprocessor.process(
            item["text"],
            detect_language=True,
            remove_stopwords=True,
        )
        corpus_prep.append({
            "id": item["id"],
            "category": item["category"],
            "source_type": item.get("source_type", "unknown"),
            "expected_language": item["language"],
            "language": result["language"],
            "language_confidence": result["language_confidence"],
            "original_text": item["text"],
            "cleaned_text": result["cleaned_text"],
        })
    
    correct_lang = sum(1 for d in corpus_prep if d["language"] == d["expected_language"])
    print(f"\n[✓] Détection langue: {correct_lang}/{len(corpus_prep)} ({correct_lang/len(corpus_prep)*100:.1f}%)")
    
    # ═════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("ÉTAPE 2 : TRADUCTION → ANGLAIS")
    print("="*70)
    
    translator = Translator(device='auto')
    corpus_translated = translator.translate_corpus(
        corpus_prep,
        text_field="cleaned_text",
        lang_field="language",
        batch_size=8,
        save_cache="translated_corpus_cache.json",
    )
    
    translated_count = sum(1 for d in corpus_translated if d.get("was_translated", False))
    print(f"[✓] Traduits: {translated_count}/{len(corpus_translated)}")
    
    # ═════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("ÉTAPE 2.5 : NETTOYAGE POST-TRADUCTION")
    print("="*70)
    
    for doc in corpus_translated:
        doc["cleaned_translated_text"] = preprocessor.clean_translated(
            doc["translated_text"]
        )
    
    print("[✓] Nettoyage post-traduction complété")
    
    return corpus_translated


# =============================================================
# BUILD BERTOPIC MODEL
# =============================================================

def build_bertopic_model(n_docs: int) -> BERTopic:
    """Construit modèle BERTopic."""
    print("\n[🔧] Configuration BERTopic...")
    
    n_neighbors = max(2, min(15, n_docs - 1))
    
    vectorizer = CountVectorizer(
        stop_words=list(ENGLISH_STOPWORDS_EXTENDED) if ENGLISH_STOPWORDS_EXTENDED else None,
        ngram_range=(1, 2),
        min_df=2,
        token_pattern=r"(?u)\b\w\w+\b",
    )
    
    umap_model = umap.UMAP(
        n_components=15,
        metric="cosine",
        n_neighbors=n_neighbors,
        min_dist=0.1,
        random_state=42,
    )
    
    hdbscan_model = hdbscan.HDBSCAN(
        min_cluster_size=4,
        min_samples=2,
        metric="euclidean",
        cluster_selection_method="eom",
        prediction_data=True,
    )
    
    model = BERTopic(
        language="english",
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer,
        min_topic_size=4,
        calculate_probabilities=True,
        verbose=True,
    )
    
    print("[✓] Modèle BERTopic configuré")
    return model


# =============================================================
# VISUALISATIONS
# =============================================================

def save_visualizations(
    model: BERTopic,
    embeddings: np.ndarray,
    topics: np.ndarray,
    corpus: List[Dict[str, Any]],
) -> None:
    """Sauvegarde TOUS les graphiques."""
    
    print("\n" + "="*70)
    print("ÉTAPE 7 : VISUALISATIONS")
    print("="*70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # ═════════════════════════════════════════════════════════
    # 1. INTERTOPIC MAP
    # ═════════════════════════════════════════════════════════
    try:
        print("\n  → Intertopic distance map...")
        fig = model.visualize_topics(custom_labels=True)
        output_path = OUTPUT_DIR / "bertopic_intertopic_map.html"
        fig.write_html(str(output_path))
        print(f"     ✓ {output_path}")
    except Exception as exc:
        print(f"     ✗ Erreur: {exc}")
    
    # ═════════════════════════════════════════════════════════
    # 2. BARCHART
    # ═════════════════════════════════════════════════════════
    try:
        print("\n  → Top keywords barchart...")
        fig = model.visualize_barchart(
            top_n_topics=12,
            custom_labels=True
        )
        output_path = OUTPUT_DIR / "bertopic_top_words_barchart.html"
        fig.write_html(str(output_path))
        print(f"     ✓ {output_path}")
    except Exception as exc:
        print(f"     ✗ Erreur: {exc}")
    
    # ═════════════════════════════════════════════════════════
    # 3. HEATMAP
    # ═════════════════════════════════════════════════════════
    topic_info = model.get_topic_info()
    if int((topic_info.Topic != -1).sum()) >= 2:
        try:
            print("\n  → Topic similarity heatmap...")
            fig = model.visualize_heatmap(custom_labels=True)
            output_path = OUTPUT_DIR / "bertopic_topic_heatmap.html"
            fig.write_html(str(output_path))
            print(f"     ✓ {output_path}")
        except Exception as exc:
            print(f"     ✗ Erreur: {exc}")
    
    # ═════════════════════════════════════════════════════════
    # 4. CARTE SÉMANTIQUE 2D
    # ═════════════════════════════════════════════════════════
    try:
        print("\n  → Semantic map (PCA 2D)...")
        
        pca = PCA(n_components=2, random_state=42)
        embeddings_2d = pca.fit_transform(embeddings)
        unique_topics = sorted(set(topics.tolist()))
        
        fig, axes = plt.subplots(1, 2, figsize=(18, 7))
        
        # Gauche: Topics
        topic_colors = cm.tab20(np.linspace(0, 1, max(len(unique_topics), 2)))
        topic_color_map = {topic: topic_colors[i] for i, topic in enumerate(unique_topics)}
        
        ax1 = axes[0]
        for topic in unique_topics:
            idxs = [i for i, t in enumerate(topics) if t == topic]
            x = embeddings_2d[idxs, 0]
            y = embeddings_2d[idxs, 1]
            if topic == -1:
                ax1.scatter(x, y, label="Outliers", color="gray", marker="x", s=80, alpha=0.85)
            else:
                ax1.scatter(x, y, label=f"Topic {topic}", 
                           color=topic_color_map[topic], s=80, alpha=0.85)
        ax1.set_title("Topics (BERTopic)", fontsize=12, fontweight="bold")
        ax1.set_xlabel("PCA 1")
        ax1.set_ylabel("PCA 2")
        ax1.grid(True, linestyle="--", alpha=0.35)
        ax1.legend(loc="upper right", fontsize=8)
        
        # Droite: Catégories
        categories = sorted(set(d.get("category", "?") for d in corpus))
        cat_colors = cm.tab20(np.linspace(0, 1, max(len(categories), 2)))
        cat_color_map = {cat: cat_colors[i] for i, cat in enumerate(categories)}
        
        ax2 = axes[1]
        for cat in categories:
            idxs = [i for i, d in enumerate(corpus) if d.get("category", "?") == cat]
            x = embeddings_2d[idxs, 0]
            y = embeddings_2d[idxs, 1]
            ax2.scatter(x, y, label=cat, color=cat_color_map[cat], s=80, alpha=0.85)
        ax2.set_title("Categories", fontsize=12, fontweight="bold")
        ax2.set_xlabel("PCA 1")
        ax2.set_ylabel("PCA 2")
        ax2.grid(True, linestyle="--", alpha=0.35)
        ax2.legend(loc="upper right", fontsize=8)
        
        plt.suptitle("BERTopic Semantic Map - CSV Corpus", 
                    fontsize=14, fontweight="bold")
        plt.tight_layout()
        
        output_path = OUTPUT_DIR / "bertopic_semantic_map.png"
        plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"     ✓ {output_path}")
    except Exception as exc:
        print(f"     ✗ Erreur: {exc}")


# =============================================================
# MAIN
# =============================================================

def main() -> None:
    print("\n" + "="*70)
    print("BERTOPIC PIPELINE — CORPUS CSV")
    print("="*70)
    
    # INPUT CSV
    print("\n📂 Entrer le chemin CSV:")
    print("   IMPORTANT: Sans guillemets ni r\"...\"")
    print("   Exemple: C:\\Users\\...\\tweets_apple_20260501_135633.csv")
    print("   Ou: datasets/tweets_apple_20260501_135633.csv\n")
    
    csv_path = input("Chemin CSV: ").strip()
    
    # Charger corpus
    corpus_raw = load_corpus_from_csv(csv_path)
    print(f"✓ Corpus chargé: {len(corpus_raw)} documents")
    
    # Prétraitement + Traduction
    corpus_enriched = preprocess_and_translate(corpus_raw)
    
    # ═════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("ÉTAPE 3 : ENCODAGE SÉMANTIQUE — BAAI/bge-m3")
    print("="*70)
    
    encoder = SemanticEncoder()
    encoding = encoder.encode_corpus(
        corpus_enriched,
        text_key="translated_text"
    )
    embeddings = encoding["embeddings"]
    print(f"[✓] Embeddings: {embeddings.shape}")
    
    # ═════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("ÉTAPE 4 : ANALYSE SIMILARITÉ (DIAGNOSTIC)")
    print("="*70)
    
    sim_engine = SimilarityEngine()
    sim_matrix = sim_engine.similarity_matrix(embeddings)
    avg_off_diag = (np.sum(sim_matrix) - np.trace(sim_matrix)) / (sim_matrix.size - len(sim_matrix))
    print(f"[✓] Similarité moyenne: {avg_off_diag:.4f}")
    
    # ═════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("ÉTAPE 5 : BERTOPIC (UMAP + HDBSCAN)")
    print("="*70)
    
    docs_for_topics = [
        d.get("cleaned_translated_text", "") or "no content" 
        for d in corpus_enriched
    ]
    
    model = build_bertopic_model(len(docs_for_topics))
    
    topics, probabilities = model.fit_transform(
        docs_for_topics,
        embeddings=embeddings
    )
    topics = np.asarray(topics)
    
    print(f"[✓] Topics trouvés: {len(set(topics)) - (1 if -1 in topics else 0)}")
    
    # ═════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("ÉTAPE 6 : NOMMAGE AUTOMATIQUE TOPICS")
    print("="*70)
    
    topic_info = model.get_topic_info().copy()
    topic_name_map: Dict[int, str] = {-1: "Outliers / Noise"}
    
    for topic_id in topic_info["Topic"].tolist():
        if topic_id == -1:
            continue
        words = model.get_topic(topic_id) or []
        topic_name_map[int(topic_id)] = auto_topic_name(words, top_n=3)
        print(f"  Topic {topic_id}: {topic_name_map[int(topic_id)]}")
    
    sorted_ids = sorted(topic_name_map.keys())
    custom_labels = [topic_name_map[t] for t in sorted_ids]
    model.set_topic_labels(custom_labels)
    
    # ═════════════════════════════════════════════════════════
    # SAVE VISUALIZATIONS
    # ═════════════════════════════════════════════════════════
    
    save_visualizations(model, embeddings, topics, corpus_enriched)
    
    # ═════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("ÉTAPE 8 : EXPORT CSV")
    print("="*70)
    
    # Topics info CSV
    topic_info["topic_name"] = topic_info["Topic"].map(
        lambda t: topic_name_map.get(int(t), f"Topic {int(t)}")
    )
    topics_csv = OUTPUT_DIR / "bertopic_topics_info.csv"
    topic_info.to_csv(topics_csv, index=False)
    print(f"[✓] {topics_csv}")
    
    # Documents CSV
    doc_df = pd.DataFrame(corpus_enriched)
    doc_df["topic"] = topics
    doc_df["topic_name"] = doc_df["topic"].map(
        lambda t: topic_name_map.get(int(t), f"Topic {int(t)}")
    )
    if probabilities is not None:
        max_proba = np.asarray(probabilities).max(axis=1)
        doc_df["topic_probability"] = max_proba
    else:
        doc_df["topic_probability"] = np.nan
    
    docs_csv = OUTPUT_DIR / "bertopic_documents_topics.csv"
    doc_df.to_csv(docs_csv, index=False)
    print(f"[✓] {docs_csv}")
    
    # ═════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("ÉTAPE 9 : EXPORT JSON")
    print("="*70)
    
    n_topics = int((topic_info.Topic != -1).sum())
    n_outliers = int((topics == -1).sum())
    
    results = {
        "metadata": {
            "total_documents": len(corpus_raw),
            "n_topics": n_topics,
            "n_outliers": n_outliers,
            "outlier_rate": round(n_outliers / len(topics) * 100, 1),
            "embedding_model": encoding.get("model", "BAAI/bge-m3"),
            "bertopic_params": {
                "umap_n_components": 15,
                "umap_metric": "cosine",
                "hdbscan_min_cluster_size": 4,
                "hdbscan_min_samples": 2,
            },
            "languages": dict(Counter(d["language"] for d in corpus_enriched)),
            "categories": dict(Counter(d["category"] for d in corpus_enriched)),
        },
        "topics": {},
    }
    
    for topic_id in sorted(set(topics.tolist())):
        topic_docs = doc_df[doc_df["topic"] == topic_id]
        top_words = [w for w, _ in (model.get_topic(int(topic_id)) or [])[:7]]
        
        results["topics"][str(int(topic_id))] = {
            "topic_name": topic_name_map.get(int(topic_id), f"Topic {int(topic_id)}"),
            "n_documents": int(len(topic_docs)),
            "top_keywords": top_words,
            "categories": topic_docs["category"].value_counts().to_dict(),
            "languages": topic_docs["language"].value_counts().to_dict(),
            "sources": topic_docs["source_type"].value_counts().to_dict(),
            "sample_documents": topic_docs[[
                "id", "category", "language", "original_text"
            ]].head(3).to_dict(orient="records"),
        }
    
    json_path = OUTPUT_DIR / "bertopic_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[✓] {json_path}")
    
    # ═════════════════════════════════════════════════════════
    # RÉSUMÉ FINAL
    # ═════════════════════════════════════════════════════════
    
    print("\n" + "="*70)
    print("✅ RÉSUMÉ FINAL")
    print("="*70)
    print(f"\n📊 Statistiques:")
    print(f"   • Documents total: {len(corpus_raw)}")
    print(f"   • Topics trouvés: {n_topics}")
    print(f"   • Documents outliers: {n_outliers} ({n_outliers/len(topics)*100:.1f}%)")
    print(f"   • Langues: {len(results['metadata']['languages'])}")
    print(f"   • Catégories: {len(results['metadata']['categories'])}")
    
    print(f"\n📁 Outputs (tous dans: {OUTPUT_DIR.absolute()}):")
    print(f"   ✓ bertopic_topics_info.csv")
    print(f"   ✓ bertopic_documents_topics.csv")
    print(f"   ✓ bertopic_results.json")
    print(f"   ✓ bertopic_intertopic_map.html")
    print(f"   ✓ bertopic_top_words_barchart.html")
    print(f"   ✓ bertopic_topic_heatmap.html")
    print(f"   ✓ bertopic_semantic_map.png")
    
    print("\n" + "="*70)


    # ═════════════════════════════════════════════════════════
    # ÉTAPE 10 : MISE À JOUR DU DASHBOARD LOVABLE (FRONT-END)
    # ═════════════════════════════════════════════════════════
    print("\n" + "="*70)
    print("ÉTAPE 10 : EXPORT VERS LOVABLE")
    print("="*70)

    # Définition du chemin vers le dossier public de ton application Lovable
    path_lovable = Path(r"C:\Users\GAB Informatique\Documents\Github\insightflow-ai\public\due_diligence_clients.json")
    try:
        # On utilise l'objet 'results' que tu viens de créer à l'étape 9
        # On ajoute un timestamp pour que le front-end sache quand les données ont été générées
        results["last_update"] = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
        
        # Créer le dossier parent s'il n'existe pas (sécurité)
        path_lovable.parent.mkdir(parents=True, exist_ok=True)

        with open(path_lovable, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"[✓] Dashboard Lovable mis à jour !")
        print(f"    Cible : {path_lovable}")
    except Exception as e:
        print(f"[❌] Erreur lors de la mise à jour Lovable : {e}")


if __name__ == "__main__":
    main()