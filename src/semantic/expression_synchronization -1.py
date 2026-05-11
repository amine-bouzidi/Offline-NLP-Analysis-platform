"""
Module d'analyse des dynamiques collectives — Étape 4.2
crowd_dynamics.py

Deux axes principaux :
  1. Convergence lexicale dans le temps
     → mesurer si le vocabulaire collectif se synchronise autour des mêmes mots
     → métriques : entropie lexicale, TTR, top-mots par mois

  2. Émergence thématique
     → détecter les mots qui apparaissent soudainement dans un mois donné
     → score d'émergence = fréquence relative ce mois / fréquence relative mois précédents
     → permet d'identifier les signaux déclencheurs avant même de lire les textes
"""

import json
import re
import math
import os
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# STOPWORDS (multilingues — EN + FR principaux)
# ─────────────────────────────────────────────────────────────

STOPWORDS = {
    # Anglais
    "the","and","for","are","was","with","that","this","have","has","been",
    "from","they","said","will","its","not","but","had","his","her","our",
    "their","also","into","more","who","than","over","after","about","such",
    "when","there","which","were","all","can","one","two","new","out","him",
    "she","any","would","some","what","your","how","now","get","got","just",
    "like","very","even","did","does","use","used","then","them","these",
    "those","could","should","other","first","last","many","much","well",
    "still","being","while","since","only","both","each","where","here",
    "make","made","say","says","company","companies","mcdonald","mcdonalds",
    # Français
    "les","des","une","est","qui","que","dans","sur","par","avec","pour",
    "pas","plus","mais","ont","aux","leur","leurs","son","ses","ces","tout",
    "nous","vous","ils","elles","très","aussi","entre","depuis","contre",
    "lors","dont","elle","lui","même","fait","dit","doit","peut","fois",
}


# ─────────────────────────────────────────────────────────────
# 1. TOKENISATION
# ─────────────────────────────────────────────────────────────

def tokenize(text: str) -> List[str]:
    """
    Tokenisation simple : mots alphabétiques ≥ 3 caractères, en minuscules,
    sans stopwords ni hashtags/mentions.
    """
    text = re.sub(r"http\S+|www\S+", "", text)          # URLs
    text = re.sub(r"[@#]\w+", "", text)                  # mentions / hashtags
    tokens = re.findall(r"[a-zA-ZÀ-ÿ]{3,}", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def build_monthly_vocab(
    docs: List[Dict],
    origin: Optional[str] = None
) -> Dict[str, Counter]:
    """
    Construit un Counter de tokens pour chaque mois (clé YYYY-MM).
    origin : 'press' | 'twitter' | None (tous)
    """
    if origin:
        docs = [d for d in docs if d.get("origin") == origin]

    monthly: Dict[str, Counter] = defaultdict(Counter)
    for d in docs:
        tokens = tokenize(d.get("text", ""))
        monthly[d["year_month"]].update(tokens)

    return dict(sorted(monthly.items()))


# ─────────────────────────────────────────────────────────────
# 2. CONVERGENCE LEXICALE
# ─────────────────────────────────────────────────────────────

def lexical_entropy(counter: Counter) -> float:
    """
    Entropie de Shannon sur la distribution des tokens.
    Entropie haute = vocabulaire dispersé (normal)
    Entropie basse  = vocabulaire concentré sur peu de mots (convergence)
    H = -Σ p(w) * log2(p(w))
    """
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return -sum(
        (c / total) * math.log2(c / total)
        for c in counter.values() if c > 0
    )


def type_token_ratio(counter: Counter) -> float:
    """
    TTR = nb types (mots uniques) / nb tokens total.
    TTR élevé = vocabulaire riche et varié
    TTR bas    = vocabulaire répétitif et convergent
    """
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return len(counter) / total


def lexical_convergence(
    monthly_vocab: Dict[str, Counter]
) -> Dict[str, Dict]:
    """
    Calcule pour chaque mois :
      - entropie lexicale
      - TTR
      - top 10 mots
      - concentration = part du top-10 dans le total (% des tokens)

    Un mois avec entropie basse + concentration haute = synchronisation collective.
    """
    result = {}
    for month, counter in monthly_vocab.items():
        total = sum(counter.values())
        top10 = counter.most_common(10)
        top10_count = sum(c for _, c in top10)

        result[month] = {
            "entropy":        round(lexical_entropy(counter), 4),
            "ttr":            round(type_token_ratio(counter), 4),
            "total_tokens":   total,
            "unique_words":   len(counter),
            "concentration":  round(top10_count / total * 100, 2) if total else 0,
            "top10":          [(w, c) for w, c in top10],
        }
    return result


# ─────────────────────────────────────────────────────────────
# 3. ÉMERGENCE THÉMATIQUE
# ─────────────────────────────────────────────────────────────

def compute_emergence_scores(
    monthly_vocab: Dict[str, Counter],
    window: int = 3,
    min_count: int = 5,
    top_n: int = 15,
) -> Dict[str, List[Tuple[str, float]]]:
    """
    Pour chaque mois M, compare la fréquence relative d'un mot dans M
    avec sa fréquence relative sur les `window` mois précédents.

    Score d'émergence = freq_relative(M) / (freq_relative(M-window..M-1) + ε)

    Un mot avec un score élevé = apparu soudainement ce mois-ci
    → signal d'un événement déclencheur.

    Retourne {mois: [(mot, score), ...]} trié par score décroissant.
    """
    months = sorted(monthly_vocab.keys())
    results = {}

    for i, month in enumerate(months):
        current = monthly_vocab[month]
        total_current = sum(current.values())
        if total_current == 0:
            continue

        # Vocabulaire de référence = window mois précédents
        past_months = months[max(0, i - window):i]
        past_combined: Counter = Counter()
        for pm in past_months:
            past_combined.update(monthly_vocab[pm])
        total_past = sum(past_combined.values())

        scores = []
        for word, count in current.items():
            if count < min_count:
                continue
            freq_current = count / total_current
            freq_past = (past_combined.get(word, 0) / total_past) if total_past > 0 else 0
            score = freq_current / (freq_past + 1e-6)
            scores.append((word, round(score, 2)))

        scores.sort(key=lambda x: -x[1])
        results[month] = scores[:top_n]

    return results


def detect_emerging_themes(
    monthly_vocab: Dict[str, Counter],
    scandals: Optional[Dict[str, str]] = None,
    window: int = 3,
    score_threshold: float = 5.0,
) -> Dict[str, Dict]:
    """
    Filtre les émergences significatives (score ≥ threshold) et les relie
    aux scandales connus si disponibles.

    Retourne {mois: {words, scandal_label, emergence_intensity}}
    """
    scandals = scandals or {}
    emergence = compute_emergence_scores(monthly_vocab, window=window)

    significant = {}
    for month, words in emergence.items():
        strong = [(w, s) for w, s in words if s >= score_threshold]
        if strong:
            significant[month] = {
                "emerging_words":       strong,
                "scandal":              scandals.get(month, ""),
                "emergence_intensity":  round(strong[0][1], 2) if strong else 0,
                "nb_emerging_words":    len(strong),
            }
    return significant


# ─────────────────────────────────────────────────────────────
# 4. VISUALISATIONS
# ─────────────────────────────────────────────────────────────

COLORS = {
    "press":   "#E63946",
    "twitter": "#1D9BF0",
    "entropy": "#6A4C93",
    "ttr":     "#2EC4B6",
    "emerge":  "#FF9F1C",
    "bg":      "#F8F9FA",
    "grid":    "#DEE2E6",
}

SCANDALS = {
    "2021-01": "Verdict Easterbrook",
    "2021-11": "Grève #FightFor15",
    "2022-03": "Retrait Russie",
    "2023-10": "Boycott Palestine",
    "2024-07": "E.coli outbreak",
    "2024-08": "Pic crise E.coli",
}

def _m2dt(m: str) -> datetime:
    return datetime.strptime(m + "-01", "%Y-%m-%d")


def plot_lexical_convergence(
    convergence_data: Dict[str, Dict],
    scandals: Optional[Dict[str, str]] = None,
    title_suffix: str = "",
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Graphique double axe : entropie lexicale + concentration top-10.
    Quand l'entropie baisse et la concentration monte = synchronisation collective.
    """
    scandals = scandals or SCANDALS
    months = sorted(convergence_data.keys())
    dts    = [_m2dt(m) for m in months]

    entropy = [convergence_data[m]["entropy"]       for m in months]
    conc    = [convergence_data[m]["concentration"] for m in months]

    fig, ax1 = plt.subplots(figsize=(16, 5))
    fig.patch.set_facecolor(COLORS["bg"])
    ax1.set_facecolor(COLORS["bg"])

    ax1.fill_between(dts, entropy, alpha=0.2, color=COLORS["entropy"])
    ax1.plot(dts, entropy, color=COLORS["entropy"], lw=2, label="Entropie lexicale")
    ax1.set_ylabel("Entropie (Shannon)", color=COLORS["entropy"], fontsize=11)
    ax1.tick_params(axis="y", labelcolor=COLORS["entropy"])

    ax2 = ax1.twinx()
    ax2.fill_between(dts, conc, alpha=0.15, color=COLORS["emerge"])
    ax2.plot(dts, conc, color=COLORS["emerge"], lw=2, ls="--", label="Concentration top-10 (%)")
    ax2.set_ylabel("Concentration top-10 (%)", color=COLORS["emerge"], fontsize=11)
    ax2.tick_params(axis="y", labelcolor=COLORS["emerge"])

    for mk, lbl in scandals.items():
        if mk in months:
            dt = _m2dt(mk)
            ax1.axvline(dt, color="gray", lw=1.2, ls=":", alpha=0.7)
            ax1.text(dt, max(entropy) * 0.98, lbl,
                     rotation=90, fontsize=7, color="gray",
                     va="top", ha="right", alpha=0.85)

    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=9)
    ax1.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.6)

    l1, lb1 = ax1.get_legend_handles_labels()
    l2, lb2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lb1 + lb2, fontsize=10, framealpha=0.85)
    ax1.set_title(f"Convergence lexicale dans le temps{' — ' + title_suffix if title_suffix else ''}",
                  fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_emergence_heatmap(
    emergence_scores: Dict[str, List[Tuple[str, float]]],
    top_words: int = 20,
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Heatmap mots × mois : intensité = score d'émergence.
    Révèle visuellement quels mots émergent à quels moments.
    Seuls les top_words mots avec les scores max toutes périodes confondues.
    """
    # Collecter tous les mots significatifs
    word_max_score: Counter = Counter()
    for month_words in emergence_scores.values():
        for w, s in month_words:
            if s > word_max_score[w]:
                word_max_score[w] = s

    top_w = [w for w, _ in word_max_score.most_common(top_words)]
    months = sorted(emergence_scores.keys())

    # Construire la matrice
    matrix = np.zeros((len(top_w), len(months)))
    for j, month in enumerate(months):
        score_map = dict(emergence_scores[month])
        for i, word in enumerate(top_w):
            matrix[i, j] = score_map.get(word, 0)

    fig, ax = plt.subplots(figsize=(max(14, len(months) * 0.32), max(6, len(top_w) * 0.45)))
    fig.patch.set_facecolor(COLORS["bg"])

    im = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", interpolation="nearest")

    # Axes
    step = max(1, len(months) // 18)
    ax.set_xticks(range(0, len(months), step))
    ax.set_xticklabels(months[::step], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(top_w)))
    ax.set_yticklabels(top_w, fontsize=9)

    # Marquer les scandales
    for mk in SCANDALS:
        if mk in months:
            idx = months.index(mk)
            ax.axvline(idx, color="blue", lw=1.5, alpha=0.4)

    plt.colorbar(im, ax=ax, shrink=0.7, label="Score d'émergence")
    ax.set_title("Carte d'émergence thématique — mots × mois",
                 fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_top_emerging_words(
    significant: Dict[str, Dict],
    scandals: Optional[Dict[str, str]] = None,
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Barres horizontales : pour chaque mois significatif,
    les 5 mots les plus émergents avec leur score.
    """
    scandals = scandals or SCANDALS
    months_sig = sorted(significant.keys())
    n = len(months_sig)
    if n == 0:
        print("Aucune émergence significative détectée.")
        return None

    cols = min(3, n)
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5.5, rows * 3.5))
    fig.patch.set_facecolor(COLORS["bg"])

    if n == 1:
        axes = np.array([axes])
    axes_flat = np.array(axes).flatten()

    for i, month in enumerate(months_sig):
        ax = axes_flat[i]
        ax.set_facecolor(COLORS["bg"])
        words_scores = significant[month]["emerging_words"][:6]
        words  = [w for w, _ in words_scores][::-1]
        scores = [s for _, s in words_scores][::-1]

        bars = ax.barh(words, scores, color=COLORS["emerge"], alpha=0.85)
        for bar, score in zip(bars, scores):
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                    f"×{score:.1f}", va="center", fontsize=8.5, color=COLORS["emerge"])

        scandal_label = scandals.get(month, "")
        title = f"{month}" + (f"\n{scandal_label}" if scandal_label else "")
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_xlabel("Score d'émergence", fontsize=9)
        ax.grid(axis="x", color=COLORS["grid"], ls="--", lw=0.5)

    # Masquer les axes vides
    for j in range(n, len(axes_flat)):
        axes_flat[j].set_visible(False)

    fig.suptitle("Mots émergents par mois significatif",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_dynamics_dashboard(
    convergence_press: Dict,
    convergence_twitter: Dict,
    significant_press: Dict,
    significant_twitter: Dict,
    scandals: Optional[Dict[str, str]] = None,
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Dashboard synthétique : entropie presse vs twitter + nb mots émergents par mois.
    """
    scandals = scandals or SCANDALS
    months_p = sorted(convergence_press.keys())
    months_t = sorted(convergence_twitter.keys())

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=False)
    fig.patch.set_facecolor(COLORS["bg"])

    # ── Entropie comparée ──────────────────────────────────────
    ax1.set_facecolor(COLORS["bg"])
    dts_p = [_m2dt(m) for m in months_p]
    dts_t = [_m2dt(m) for m in months_t]
    ent_p = [convergence_press[m]["entropy"]   for m in months_p]
    ent_t = [convergence_twitter[m]["entropy"] for m in months_t]

    ax1.plot(dts_p, ent_p, color=COLORS["press"],   lw=2, label="Entropie Presse")
    ax1.plot(dts_t, ent_t, color=COLORS["twitter"], lw=2, label="Entropie Twitter")

    for mk, lbl in scandals.items():
        dt = _m2dt(mk)
        ax1.axvline(dt, color=COLORS["emerge"], lw=1.2, ls="--", alpha=0.7)
        ax1.text(dt, max(ent_p + ent_t) * 0.98, lbl,
                 rotation=90, fontsize=7, color=COLORS["emerge"],
                 va="top", ha="right", alpha=0.9)

    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=8)
    ax1.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)
    ax1.legend(fontsize=10, framealpha=0.85)
    ax1.set_title("Entropie lexicale comparée — Presse vs Twitter",
                  fontsize=12, fontweight="bold")
    ax1.set_ylabel("Entropie (Shannon)")

    # ── Nombre de mots émergents par mois ─────────────────────
    ax2.set_facecolor(COLORS["bg"])
    all_months = sorted(set(months_p) | set(months_t))
    dts_all    = [_m2dt(m) for m in all_months]
    nb_p = [significant_press.get(m, {}).get("nb_emerging_words", 0)   for m in all_months]
    nb_t = [significant_twitter.get(m, {}).get("nb_emerging_words", 0) for m in all_months]

    w = 12  # largeur barre en jours
    import matplotlib.dates as mdates2
    from datetime import timedelta
    dts_l = [d - timedelta(days=6) for d in dts_all]
    dts_r = [d + timedelta(days=6) for d in dts_all]

    ax2.bar(dts_l, nb_p, width=12, color=COLORS["press"],   alpha=0.8, label="Mots émergents Presse")
    ax2.bar(dts_r, nb_t, width=12, color=COLORS["twitter"], alpha=0.8, label="Mots émergents Twitter")

    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=8)
    ax2.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)
    ax2.legend(fontsize=10, framealpha=0.85)
    ax2.set_title("Nombre de mots émergents significatifs (score ≥ 5)",
                  fontsize=12, fontweight="bold")
    ax2.set_ylabel("Nb mots émergents")

    fig.suptitle("Dashboard Dynamiques Collectives — Corpus McDonald's",
                 fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


# ─────────────────────────────────────────────────────────────
# 5. POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from temporal_analysis import load_corpus

    PRESS_PATH   = r"C:\Users\GAB Informatique\Documents\Master 2\PFE\plateforme_analyse_textuelle\src\semantic\press_scrapper.json"
    TWITTER_PATH = r"C:\Users\GAB Informatique\Documents\Master 2\PFE\plateforme_analyse_textuelle\src\semantic\twitter_scraper (1).json"
    OUT_DIR      = "outputs_crowd"
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Chargement du corpus…")
    corpus = load_corpus(PRESS_PATH, TWITTER_PATH)

    # ── Vocabulaires mensuels ───────────────────────────────────
    print("Construction des vocabulaires mensuels…")
    vocab_press   = build_monthly_vocab(corpus, origin="press")
    vocab_twitter = build_monthly_vocab(corpus, origin="twitter")

    # ── Convergence lexicale ────────────────────────────────────
    print("Calcul de la convergence lexicale…")
    conv_press   = lexical_convergence(vocab_press)
    conv_twitter = lexical_convergence(vocab_twitter)

    # Affichage résumé
    print("\n── Entropie lors des pics (Twitter) ──")
    for m in ["2021-01","2021-11","2022-03","2023-10","2023-11","2024-07","2024-08"]:
        if m in conv_twitter:
            d = conv_twitter[m]
            print(f"  {m}: entropie={d['entropy']:.3f}  concentration={d['concentration']}%  "
                  f"top3={[w for w,_ in d['top10'][:3]]}")

    # ── Émergence thématique ────────────────────────────────────
    print("\nCalcul des émergences thématiques…")
    emerg_press   = compute_emergence_scores(vocab_press)
    emerg_twitter = compute_emergence_scores(vocab_twitter)

    sig_press   = detect_emerging_themes(vocab_press,   SCANDALS)
    sig_twitter = detect_emerging_themes(vocab_twitter, SCANDALS)

    print(f"\n  Mois significatifs Presse  : {sorted(sig_press.keys())}")
    print(f"  Mois significatifs Twitter : {sorted(sig_twitter.keys())}")

    print("\nTop émergences Twitter lors des scandales :")
    for m in ["2023-10","2024-08","2022-03"]:
        if m in sig_twitter:
            top = sig_twitter[m]["emerging_words"][:5]
            print(f"  {m} ({SCANDALS.get(m,'')}): {top}")

    # ── Visualisations ──────────────────────────────────────────
    print("\nGénération des visualisations…")

    import matplotlib
    matplotlib.use("Agg")

    plot_lexical_convergence(conv_press, SCANDALS, "Presse",
        output_path=f"{OUT_DIR}/01_convergence_press.png", show=False)
    print("  ✓ 01_convergence_press.png")

    plot_lexical_convergence(conv_twitter, SCANDALS, "Twitter",
        output_path=f"{OUT_DIR}/02_convergence_twitter.png", show=False)
    print("  ✓ 02_convergence_twitter.png")

    plot_emergence_heatmap(emerg_twitter,
        output_path=f"{OUT_DIR}/03_emergence_heatmap_twitter.png", show=False)
    print("  ✓ 03_emergence_heatmap_twitter.png")

    plot_top_emerging_words(sig_twitter, SCANDALS,
        output_path=f"{OUT_DIR}/04_top_emerging_twitter.png", show=False)
    print("  ✓ 04_top_emerging_twitter.png")

    plot_top_emerging_words(sig_press, SCANDALS,
        output_path=f"{OUT_DIR}/05_top_emerging_press.png", show=False)
    print("  ✓ 05_top_emerging_press.png")

    plot_dynamics_dashboard(conv_press, conv_twitter, sig_press, sig_twitter, SCANDALS,
        output_path=f"{OUT_DIR}/06_dashboard_dynamics.png", show=False)
    print("  ✓ 06_dashboard_dynamics.png")

    print(f"\nTous les graphiques sont dans '{OUT_DIR}/'")


# ─────────────────────────────────────────────────────────────
# 6. SYNCHRONISATION DES EXPRESSIONS (Étape 4.3.1)
# ─────────────────────────────────────────────────────────────

def doc_to_tf_vector(tokens: List[str], vocab: List[str]) -> np.ndarray:
    """
    Convertit une liste de tokens en vecteur TF (Term Frequency).
    Chaque dimension correspond à un mot du vocabulaire commun.
    tf(mot) = count(mot) / total_tokens
    """
    counter = Counter(tokens)
    total   = sum(counter.values()) or 1
    return np.array([counter.get(w, 0) / total for w in vocab], dtype=float)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Similarité cosinus entre deux vecteurs.
    cos(θ) = (A · B) / (||A|| × ||B||)
    Retourne 0 si l'un des vecteurs est nul.
    """
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def monthly_synchronization(
    docs: List[Dict],
    origin: str = "twitter",
    sample_size: int = 300,
    min_docs: int = 10,
    random_seed: int = 42,
) -> Dict[str, Dict]:
    """
    Calcule le score de synchronisation pour chaque mois.

    Pour chaque mois :
      1. Échantillonner min(sample_size, nb_docs) documents
      2. Tokeniser chaque document → vecteur TF sur vocabulaire commun du mois
      3. Calculer la similarité cosinus entre toutes les paires
      4. Retourner la moyenne = score de synchronisation du mois

    Un score élevé = les documents se ressemblent → foule synchronisée.
    Un score bas   = vocabulaires dispersés → comportements individuels.

    Retourne {mois: {sync_score, nb_docs, nb_pairs, std}}
    """
    import random as rnd
    rnd.seed(random_seed)

    # Grouper par mois et par origin
    monthly: Dict[str, List] = defaultdict(list)
    for d in docs:
        if d.get("origin") == origin:
            monthly[d["year_month"]].append(d)

    results = {}
    for month in sorted(monthly.keys()):
        month_docs = monthly[month]
        if len(month_docs) < min_docs:
            continue

        # Échantillonnage
        sample = rnd.sample(month_docs, min(sample_size, len(month_docs)))

        # Tokenisation de chaque doc
        tokenized = [tokenize(d.get("text", "")) for d in sample]
        tokenized = [t for t in tokenized if len(t) >= 2]  # ignorer docs vides
        if len(tokenized) < min_docs:
            continue

        # Vocabulaire commun du mois (union de tous les tokens)
        vocab = list({w for tokens in tokenized for w in tokens})
        if not vocab:
            continue

        # Vecteurs TF
        vectors = [doc_to_tf_vector(t, vocab) for t in tokenized]

        # Similarités cosinus sur toutes les paires
        similarities = []
        n = len(vectors)
        for i in range(n):
            for j in range(i + 1, n):
                similarities.append(cosine_similarity(vectors[i], vectors[j]))

        if not similarities:
            continue

        results[month] = {
            "sync_score": round(float(np.mean(similarities)), 5),
            "std":        round(float(np.std(similarities)),  5),
            "nb_docs":    len(month_docs),
            "nb_pairs":   len(similarities),
        }

    return results


def plot_synchronization(
    sync_press: Dict[str, Dict],
    sync_twitter: Dict[str, Dict],
    scandals: Optional[Dict[str, str]] = None,
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Courbes de synchronisation mensuelle Presse vs Twitter.
    Un pic de synchronisation lors d'un scandale confirme
    que la foule converge vers un discours commun.
    """
    scandals = scandals or SCANDALS

    months_p = sorted(sync_press.keys())
    months_t = sorted(sync_twitter.keys())
    dts_p    = [_m2dt(m) for m in months_p]
    dts_t    = [_m2dt(m) for m in months_t]
    scores_p = [sync_press[m]["sync_score"]   for m in months_p]
    scores_t = [sync_twitter[m]["sync_score"] for m in months_t]

    fig, ax = plt.subplots(figsize=(16, 5))
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    ax.fill_between(dts_p, scores_p, alpha=0.2, color=COLORS["press"])
    ax.plot(dts_p, scores_p, color=COLORS["press"],   lw=2,   label="Synchronisation Presse")
    ax.fill_between(dts_t, scores_t, alpha=0.15, color=COLORS["twitter"])
    ax.plot(dts_t, scores_t, color=COLORS["twitter"], lw=2,   label="Synchronisation Twitter")

    # Barres d'erreur (std) pour montrer la dispersion
    ax.fill_between(
        dts_p,
        [sync_press[m]["sync_score"] - sync_press[m]["std"]   for m in months_p],
        [sync_press[m]["sync_score"] + sync_press[m]["std"]   for m in months_p],
        alpha=0.08, color=COLORS["press"]
    )
    ax.fill_between(
        dts_t,
        [sync_twitter[m]["sync_score"] - sync_twitter[m]["std"] for m in months_t],
        [sync_twitter[m]["sync_score"] + sync_twitter[m]["std"] for m in months_t],
        alpha=0.06, color=COLORS["twitter"]
    )

    # Annotations scandales
    y_max = max(scores_p + scores_t)
    for mk, lbl in scandals.items():
        dt = _m2dt(mk)
        ax.axvline(dt, color=COLORS["emerge"], lw=1.3, ls="--", alpha=0.75)
        ax.text(dt, y_max * 0.98, lbl,
                rotation=90, fontsize=7.5, color=COLORS["emerge"],
                va="top", ha="right", alpha=0.9)

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=9)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.4f"))
    ax.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.6)
    ax.legend(fontsize=10, framealpha=0.85)
    ax.set_ylabel("Score de synchronisation (cosinus moyen)", fontsize=11)
    ax.set_title("Synchronisation lexicale mensuelle — Presse vs Twitter",
                 fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig