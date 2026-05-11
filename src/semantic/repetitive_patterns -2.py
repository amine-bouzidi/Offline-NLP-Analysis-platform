"""
Module de détection des schémas répétitifs — Étape 4.3.2
repetitive_patterns.py

Objectif : détecter les mots qui reviennent de façon cyclique dans le corpus,
indépendamment des scandales.

Fonctions :
  - build_word_timeseries   : série temporelle de fréquence par mot
  - autocorrelation         : calcul R(k) pour lags 1–12
  - detect_repetitive_patterns : détection + classification des cycles
  - plot_repetitive_patterns   : visualisation série + autocorrelogramme
"""

import os
import math
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────

COLORS = {
    "series":  "#6A4C93",
    "bar_sig": "#FF9F1C",
    "bar_ns":  "#DEE2E6",
    "seuil":   "#E63946",
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


# ─────────────────────────────────────────────────────────────
# 1. SÉRIE TEMPORELLE PAR MOT
# ─────────────────────────────────────────────────────────────

def build_word_timeseries(
    monthly_vocab: Dict[str, Counter],
    top_n: int = 100,
) -> Tuple[List[str], Dict[str, np.ndarray]]:
    """
    Pour chaque mot parmi les top_n les plus fréquents du corpus,
    construit sa série temporelle de fréquence relative mois par mois.

    freq_relative(mot, mois) = count(mot, mois) / total_tokens(mois)

    Retourne :
      - months  : liste des mois triés (YYYY-MM)
      - timeseries : {mot: array de longueur nb_mois}
    """
    months = sorted(monthly_vocab.keys())

    # Top N mots sur l'ensemble du corpus
    global_count: Counter = Counter()
    for c in monthly_vocab.values():
        global_count.update(c)
    top_words = [w for w, _ in global_count.most_common(top_n)]

    timeseries = {}
    for word in top_words:
        series = []
        for m in months:
            total = sum(monthly_vocab[m].values()) or 1
            freq  = monthly_vocab[m].get(word, 0) / total
            series.append(freq)
        timeseries[word] = np.array(series)

    return months, timeseries


# ─────────────────────────────────────────────────────────────
# 2. AUTOCORRÉLATION
# ─────────────────────────────────────────────────────────────

def autocorrelation(series: np.ndarray, max_lag: int = 12) -> np.ndarray:
    """
    Calcule l'autocorrélation de la série pour les lags k = 1 à max_lag.

    Formule :
      R(k) = Σ (x(t) - μ) × (x(t+k) - μ)  /  (n × σ²)

    où :
      μ  = moyenne de la série
      σ² = variance de la série
      n  = longueur totale

    Pour chaque lag k on compare chaque valeur x(t) avec
    la valeur x(t+k) — c'est-à-dire la même série décalée de k mois.
    Si elles montent et descendent ensemble → R(k) proche de 1.
    Si elles sont indépendantes            → R(k) proche de 0.

    Retourne un array de longueur max_lag.
    acf[0] = R(lag=1), acf[11] = R(lag=12).
    """
    n   = len(series)
    mu  = series.mean()
    var = series.var()

    # Pas assez de données ou série constante
    if var == 0 or n < max_lag + 2:
        return np.zeros(max_lag)

    acf = np.zeros(max_lag)
    for k in range(1, max_lag + 1):
        # x(t) - μ pour t = 0 .. n-k-1
        x_t  = series[:n - k] - mu
        # x(t+k) - μ pour t+k = k .. n-1
        x_tk = series[k:] - mu
        # Produit scalaire / normalisation
        acf[k - 1] = np.sum(x_t * x_tk) / (n * var)

    return acf


# ─────────────────────────────────────────────────────────────
# 3. DÉTECTION ET CLASSIFICATION DES CYCLES
# ─────────────────────────────────────────────────────────────

def detect_repetitive_patterns(
    monthly_vocab: Dict[str, Counter],
    top_n: int = 150,
    max_lag: int = 12,
    acf_threshold: float = 0.25,
) -> Dict[str, Dict]:
    """
    Détecte les mots avec des schémas cycliques significatifs.

    Pour chaque mot dans le top_n :
      1. Construire sa série temporelle de fréquence relative
      2. Calculer R(k) pour k = 1 à max_lag
      3. Trouver le lag dominant = k avec le R le plus élevé
      4. Garder si R(dominant) >= acf_threshold

    Classification des cycles selon le lag dominant :
      lag 1–2  → court_terme   (persistance post-scandale)
      lag 3–4  → trimestriel   (résultats financiers, campagnes)
      lag 5–6  → semestriel
      lag 7–12 → annuel        (saisonnalité)

    Retourne {mot: {dominant_lag, acf_value, cycle_type, acf_full}}
    trié par acf_value décroissant.
    """
    months, timeseries = build_word_timeseries(monthly_vocab, top_n=top_n)
    results = {}

    for word, series in timeseries.items():
        acf = autocorrelation(series, max_lag=max_lag)

        # Lag dominant : index du max + 1 (car acf[0] = lag 1)
        dominant_lag = int(np.argmax(acf)) + 1
        acf_value    = float(acf[dominant_lag - 1])

        # Filtrer les schémas non significatifs
        if acf_value < acf_threshold:
            continue

        # Classifier le cycle
        if dominant_lag <= 2:
            cycle_type = "court_terme"
        elif dominant_lag <= 4:
            cycle_type = "trimestriel"
        elif dominant_lag <= 6:
            cycle_type = "semestriel"
        else:
            cycle_type = "annuel"

        results[word] = {
            "dominant_lag": dominant_lag,
            "acf_value":    round(acf_value, 4),
            "cycle_type":   cycle_type,
            "acf_full":     [round(float(v), 4) for v in acf],
        }

    return dict(sorted(results.items(), key=lambda x: -x[1]["acf_value"]))


# ─────────────────────────────────────────────────────────────
# 4. VISUALISATION
# ─────────────────────────────────────────────────────────────

def plot_repetitive_patterns(
    patterns: Dict[str, Dict],
    monthly_vocab: Dict[str, Counter],
    top_words: int = 6,
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Pour chaque mot sélectionné, affiche deux panneaux côte à côte :
      - Gauche  : série temporelle de fréquence relative (courbe)
      - Droite  : autocorrelogramme (barres par lag, orange si significatif)

    Permet de confirmer visuellement chaque cycle détecté.
    """
    words = list(patterns.keys())[:top_words]
    n     = len(words)
    if n == 0:
        print("Aucun schéma répétitif détecté.")
        return None

    months, timeseries = build_word_timeseries(monthly_vocab, top_n=200)
    dts = [_m2dt(m) for m in months]

    fig, axes = plt.subplots(n, 2, figsize=(14, n * 2.8))
    fig.patch.set_facecolor(COLORS["bg"])

    # Si un seul mot, axes n'est pas 2D
    if n == 1:
        axes = [axes]

    for i, word in enumerate(words):
        info   = patterns[word]
        series = timeseries[word]
        acf    = info["acf_full"]
        lags   = list(range(1, len(acf) + 1))

        # ── Panneau gauche : série temporelle ─────────────────
        ax_s = axes[i][0]
        ax_s.set_facecolor(COLORS["bg"])
        ax_s.fill_between(dts, series, alpha=0.2, color=COLORS["series"])
        ax_s.plot(dts, series, color=COLORS["series"], lw=1.8)

        # Marquer les mois de scandale
        for mk in SCANDALS:
            if mk in months:
                ax_s.axvline(_m2dt(mk), color="gray", lw=1, ls=":", alpha=0.6)

        ax_s.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax_s.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
        plt.setp(ax_s.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=7)
        ax_s.set_title(f'"{word}" — fréquence relative mensuelle',
                       fontsize=10, fontweight="bold")
        ax_s.set_ylabel("Fréq. relative", fontsize=8)
        ax_s.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)

        # ── Panneau droit : autocorrelogramme ─────────────────
        ax_a = axes[i][1]
        ax_a.set_facecolor(COLORS["bg"])

        # Barres orange si R >= seuil, grises sinon
        bar_colors = [
            COLORS["bar_sig"] if v >= 0.25 else COLORS["bar_ns"]
            for v in acf
        ]
        ax_a.bar(lags, acf, color=bar_colors, alpha=0.88, width=0.6)
        ax_a.axhline(0.25, color=COLORS["seuil"], ls="--", lw=1.2,
                     alpha=0.8, label="Seuil significatif (0.25)")
        ax_a.axhline(0,    color="gray", ls="-", lw=0.7, alpha=0.5)

        ax_a.set_xticks(lags)
        ax_a.set_xticklabels([str(l) for l in lags], fontsize=8)
        ax_a.set_xlabel("Lag (mois)", fontsize=8)
        ax_a.set_ylabel("R(k)", fontsize=8)

        cycle_labels = {
            "court_terme":  "Court terme",
            "trimestriel":  "Trimestriel",
            "semestriel":   "Semestriel",
            "annuel":       "Annuel",
        }
        cycle_label = cycle_labels.get(info["cycle_type"], "")
        ax_a.set_title(
            f"Autocorrelogramme — lag dominant = {info['dominant_lag']} mois"
            f"  [{cycle_label}, R={info['acf_value']}]",
            fontsize=9, fontweight="bold"
        )
        ax_a.legend(fontsize=8, framealpha=0.85)
        ax_a.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)

    fig.suptitle("Schémas répétitifs détectés par autocorrélation",
                 fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_cycle_distribution(
    patterns: Dict[str, Dict],
    title_suffix: str = "",
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Graphique de synthèse : distribution des types de cycles détectés
    et histogramme des lags dominants.
    """
    if not patterns:
        print("Aucun pattern à afficher.")
        return None

    cycle_counts = Counter(info["cycle_type"] for info in patterns.values())
    lag_counts   = Counter(info["dominant_lag"] for info in patterns.values())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.patch.set_facecolor(COLORS["bg"])

    # ── Distribution des types ─────────────────────────────────
    ax1.set_facecolor(COLORS["bg"])
    labels = list(cycle_counts.keys())
    values = list(cycle_counts.values())
    colors = ["#FF9F1C", "#6A4C93", "#2EC4B6", "#E63946"][:len(labels)]
    ax1.bar(labels, values, color=colors, alpha=0.85)
    ax1.set_title(f"Distribution des types de cycles{' — ' + title_suffix if title_suffix else ''}",
                  fontsize=11, fontweight="bold")
    ax1.set_ylabel("Nb de mots")
    ax1.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)
    for j, (lbl, val) in enumerate(zip(labels, values)):
        ax1.text(j, val + 0.3, str(val), ha="center", fontsize=10, fontweight="bold")

    # ── Histogramme des lags dominants ────────────────────────
    ax2.set_facecolor(COLORS["bg"])
    all_lags = list(range(1, 13))
    lag_vals = [lag_counts.get(l, 0) for l in all_lags]
    ax2.bar(all_lags, lag_vals, color=COLORS["bar_sig"], alpha=0.85, width=0.7)
    ax2.set_xticks(all_lags)
    ax2.set_xlabel("Lag dominant (mois)", fontsize=10)
    ax2.set_ylabel("Nb de mots", fontsize=10)
    ax2.set_title("Distribution des lags dominants", fontsize=11, fontweight="bold")
    ax2.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)

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
    import matplotlib
    matplotlib.use("Agg")

    from temporal_analysis import load_corpus
    from crowd_dynamics import build_monthly_vocab

    PRESS_PATH   = "press_scrapper.json"
    TWITTER_PATH = "twitter_scraper.json"
    OUT_DIR      = "outputs_patterns"
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Chargement du corpus...")
    corpus = load_corpus(PRESS_PATH, TWITTER_PATH)

    vocab_press   = build_monthly_vocab(corpus, origin="press")
    vocab_twitter = build_monthly_vocab(corpus, origin="twitter")

    # ── Détection des patterns ──────────────────────────────────
    print("Détection des schémas répétitifs — Presse...")
    patterns_press = detect_repetitive_patterns(vocab_press, top_n=150, acf_threshold=0.25)

    print("Détection des schémas répétitifs — Twitter...")
    patterns_twitter = detect_repetitive_patterns(vocab_twitter, top_n=150, acf_threshold=0.25)

    # ── Résumé console ─────────────────────────────────────────
    print(f"\nNb mots avec cycle détecté — presse: {len(patterns_press)}, twitter: {len(patterns_twitter)}")

    print("\n── Top 10 patterns Presse ──")
    for w, info in list(patterns_press.items())[:10]:
        print(f"  {w:20s}  lag={info['dominant_lag']:2d} mois  "
              f"R={info['acf_value']:.3f}  [{info['cycle_type']}]")

    print("\n── Top 10 patterns Twitter ──")
    for w, info in list(patterns_twitter.items())[:10]:
        print(f"  {w:20s}  lag={info['dominant_lag']:2d} mois  "
              f"R={info['acf_value']:.3f}  [{info['cycle_type']}]")

    # Distribution par type de cycle
    print("\n── Distribution cycles Presse ──")
    for ctype, count in Counter(i["cycle_type"] for i in patterns_press.values()).items():
        print(f"  {ctype}: {count} mots")

    print("\n── Distribution cycles Twitter ──")
    for ctype, count in Counter(i["cycle_type"] for i in patterns_twitter.values()).items():
        print(f"  {ctype}: {count} mots")

    # ── Visualisations ──────────────────────────────────────────
    print("\nGénération des visualisations...")

    plot_repetitive_patterns(
        patterns_press, vocab_press, top_words=6,
        output_path=f"{OUT_DIR}/01_patterns_press.png", show=False
    )
    print("  ✓ 01_patterns_press.png")

    plot_repetitive_patterns(
        patterns_twitter, vocab_twitter, top_words=6,
        output_path=f"{OUT_DIR}/02_patterns_twitter.png", show=False
    )
    print("  ✓ 02_patterns_twitter.png")

    plot_cycle_distribution(
        patterns_press, title_suffix="Presse",
        output_path=f"{OUT_DIR}/03_cycle_distribution_press.png", show=False
    )
    print("  ✓ 03_cycle_distribution_press.png")

    plot_cycle_distribution(
        patterns_twitter, title_suffix="Twitter",
        output_path=f"{OUT_DIR}/04_cycle_distribution_twitter.png", show=False
    )
    print("  ✓ 04_cycle_distribution_twitter.png")

    print(f"\nTous les graphiques dans '{OUT_DIR}/'")