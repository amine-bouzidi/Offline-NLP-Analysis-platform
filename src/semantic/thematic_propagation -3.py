"""
Module de propagation thématique — Étape 4.3.3
thematic_propagation.py

Objectif : détecter si Twitter précède la presse ou l'inverse
sur les sujets clés, en mesurant le décalage temporel optimal
entre les deux séries de fréquence d'un même mot.

Fonctions :
  - build_aligned_series     : aligner les deux séries sur les mois communs
  - cross_correlation        : calcul CC(k) pour lags -max_lag à +max_lag
  - detect_propagation       : trouver le lag optimal pour chaque mot
  - plot_propagation_summary : visualisation des résultats
  - plot_word_propagation    : zoom sur un mot spécifique
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
    "press":    "#E63946",
    "twitter":  "#1D9BF0",
    "tw_leads": "#FF9F1C",
    "pr_leads": "#6A4C93",
    "simult":   "#2EC4B6",
    "bg":       "#F8F9FA",
    "grid":     "#DEE2E6",
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
# 1. ALIGNEMENT DES SÉRIES
# ─────────────────────────────────────────────────────────────

def build_aligned_series(
    vocab_press: Dict[str, Counter],
    vocab_twitter: Dict[str, Counter],
    top_n: int = 75,
) -> Tuple[List[str], Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """
    Construit les séries temporelles de fréquence relative pour
    chaque mot, alignées sur les mois communs aux deux sources.

    freq_relative(mot, mois) = count(mot, mois) / total_tokens(mois)

    Retourne :
      - months      : liste des mois communs triés
      - series_press  : {mot: array fréquence presse}
      - series_twitter: {mot: array fréquence twitter}
    """
    # Mois communs aux deux sources
    months = sorted(set(vocab_press.keys()) & set(vocab_twitter.keys()))

    # Mots communs aux deux sources
    total_p: Counter = Counter()
    total_t: Counter = Counter()
    for c in vocab_press.values():   total_p.update(c)
    for c in vocab_twitter.values(): total_t.update(c)

    common_words = set(total_p.keys()) & set(total_t.keys())

    # Top N mots communs (par fréquence presse)
    top_words = [
        w for w, _ in total_p.most_common(200)
        if w in common_words
    ][:top_n]

    series_press   = {}
    series_twitter = {}

    for word in top_words:
        sp, st = [], []
        for m in months:
            total_tokens_p = sum(vocab_press[m].values())   or 1
            total_tokens_t = sum(vocab_twitter[m].values()) or 1
            sp.append(vocab_press[m].get(word, 0)   / total_tokens_p)
            st.append(vocab_twitter[m].get(word, 0) / total_tokens_t)

        series_press[word]   = np.array(sp)
        series_twitter[word] = np.array(st)

    return months, series_press, series_twitter


# ─────────────────────────────────────────────────────────────
# 2. CORRÉLATION CROISÉE
# ─────────────────────────────────────────────────────────────

def cross_correlation(
    series_tw: np.ndarray,
    series_pr: np.ndarray,
    max_lag: int = 4,
) -> Tuple[List[int], List[float]]:
    """
    Calcule la corrélation croisée entre la série Twitter et la série Presse
    pour les décalages k allant de -max_lag à +max_lag.

    Formule pour un lag k :
      CC(k) = Σ (x_tw(t) - μ_tw) × (x_pr(t+k) - μ_pr)
              ─────────────────────────────────────────────
                        n × σ_tw × σ_pr

    Interprétation du lag optimal :
      k < 0  → Twitter est en avance  (Twitter parle du sujet avant la presse)
      k = 0  → simultané              (les deux réagissent en même temps)
      k > 0  → Presse est en avance   (la presse initie, Twitter suit)

    Retourne (lags, correlations) — deux listes alignées.
    """
    n      = len(series_tw)
    mu_tw  = series_tw.mean()
    mu_pr  = series_pr.mean()
    std_tw = series_tw.std()
    std_pr = series_pr.std()

    # Si l'une des séries est constante (pas de variation), CC non définie
    if std_tw == 0 or std_pr == 0:
        lags = list(range(-max_lag, max_lag + 1))
        return lags, [0.0] * len(lags)

    lags = list(range(-max_lag, max_lag + 1))
    correlations = []

    for k in lags:
        if k < 0:
            # Twitter décalé vers la droite : on compare tw(t) avec pr(t-k)
            # → tw[0..|k|-1] avec pr[|k|..n-1]
            tw_part = series_tw[:n + k] - mu_tw   # n+k éléments (k<0 donc n+k < n)
            pr_part = series_pr[-k:]    - mu_pr    # n+k éléments
        elif k > 0:
            # Presse décalée vers la droite : on compare tw(t+k) avec pr(t)
            tw_part = series_tw[k:]  - mu_tw       # n-k éléments
            pr_part = series_pr[:n - k] - mu_pr    # n-k éléments
        else:
            # k=0 : pas de décalage
            tw_part = series_tw - mu_tw
            pr_part = series_pr - mu_pr

        n_pairs = len(tw_part)
        if n_pairs == 0:
            correlations.append(0.0)
        else:
            cc = np.sum(tw_part * pr_part) / (n_pairs * std_tw * std_pr)
            correlations.append(round(float(cc), 5))

    return lags, correlations


# ─────────────────────────────────────────────────────────────
# 3. DÉTECTION DE LA PROPAGATION
# ─────────────────────────────────────────────────────────────

def detect_propagation(
    vocab_press: Dict[str, Counter],
    vocab_twitter: Dict[str, Counter],
    top_n: int = 75,
    max_lag: int = 4,
    min_cc: float = 0.20,
) -> Dict[str, Dict]:
    """
    Pour chaque mot commun aux deux sources :
      1. Construire les séries temporelles alignées
      2. Calculer la cross-correlation pour lags -4 à +4
      3. Identifier le lag optimal (CC maximale)
      4. Garder si CC_max >= min_cc (corrélation significative)
      5. Classer : Twitter en avance / simultané / Presse en avance

    Retourne {mot: {optimal_lag, cc_max, direction, cc_full}}
    trié par cc_max décroissant.
    """
    months, series_press, series_twitter = build_aligned_series(
        vocab_press, vocab_twitter, top_n=top_n
    )

    results = {}
    for word in series_press:
        lags, cc_values = cross_correlation(
            series_twitter[word],
            series_press[word],
            max_lag=max_lag,
        )

        cc_max     = max(cc_values)
        if cc_max < min_cc:
            continue

        optimal_lag = lags[cc_values.index(cc_max)]

        # Classification de la direction
        if optimal_lag < 0:
            direction = "twitter_leads"    # Twitter précède la presse
        elif optimal_lag > 0:
            direction = "press_leads"      # Presse précède Twitter
        else:
            direction = "simultaneous"     # Réaction simultanée

        results[word] = {
            "optimal_lag": optimal_lag,
            "cc_max":      round(cc_max, 4),
            "direction":   direction,
            "cc_full":     dict(zip(lags, cc_values)),
        }

    return dict(sorted(results.items(), key=lambda x: -x[1]["cc_max"]))


# ─────────────────────────────────────────────────────────────
# 4. VISUALISATIONS
# ─────────────────────────────────────────────────────────────

def plot_propagation_summary(
    propagation: Dict[str, Dict],
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Deux graphiques de synthèse :
      - Distribution des directions (Twitter leads / simultané / Presse leads)
      - Distribution des lags optimaux (-4 à +4)
    """
    if not propagation:
        print("Aucune propagation détectée.")
        return None

    directions = Counter(info["direction"] for info in propagation.values())
    lag_counts = Counter(info["optimal_lag"] for info in propagation.values())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4))
    fig.patch.set_facecolor(COLORS["bg"])

    # ── Distribution des directions ───────────────────────────
    ax1.set_facecolor(COLORS["bg"])
    dir_labels = {
        "twitter_leads": "Twitter en avance",
        "simultaneous":  "Simultané",
        "press_leads":   "Presse en avance",
    }
    dir_colors = {
        "twitter_leads": COLORS["tw_leads"],
        "simultaneous":  COLORS["simult"],
        "press_leads":   COLORS["pr_leads"],
    }
    labels = [dir_labels[d] for d in dir_labels if d in directions]
    values = [directions[d] for d in dir_labels if d in directions]
    colors = [dir_colors[d] for d in dir_labels if d in directions]

    bars = ax1.bar(labels, values, color=colors, alpha=0.88, width=0.5)
    for bar, val in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.2, str(val),
                 ha="center", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Nombre de mots", fontsize=10)
    ax1.set_title("Direction de propagation thématique", fontsize=12, fontweight="bold")
    ax1.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.6)

    # ── Distribution des lags optimaux ────────────────────────
    ax2.set_facecolor(COLORS["bg"])
    all_lags  = list(range(-4, 5))
    lag_vals  = [lag_counts.get(l, 0) for l in all_lags]
    bar_colors = [
        COLORS["tw_leads"] if l < 0
        else COLORS["pr_leads"] if l > 0
        else COLORS["simult"]
        for l in all_lags
    ]
    ax2.bar(all_lags, lag_vals, color=bar_colors, alpha=0.88, width=0.7)
    ax2.axvline(0, color="gray", ls="--", lw=1.2, alpha=0.7)
    ax2.set_xticks(all_lags)
    ax2.set_xticklabels(
        [f"TW+{abs(l)}m" if l < 0 else ("Simult." if l == 0 else f"PR+{l}m")
         for l in all_lags],
        fontsize=8, rotation=20
    )
    ax2.set_ylabel("Nombre de mots", fontsize=10)
    ax2.set_title("Distribution des lags optimaux", fontsize=12, fontweight="bold")
    ax2.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.6)

    # Légende manuelle
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS["tw_leads"], label="Twitter en avance"),
        Patch(facecolor=COLORS["simult"],   label="Simultané"),
        Patch(facecolor=COLORS["pr_leads"], label="Presse en avance"),
    ]
    ax2.legend(handles=legend_elements, fontsize=9, framealpha=0.85)

    fig.suptitle("Synthèse — Propagation thématique Twitter ↔ Presse",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_word_propagation(
    word: str,
    propagation: Dict[str, Dict],
    months: List[str],
    series_press: Dict[str, np.ndarray],
    series_twitter: Dict[str, np.ndarray],
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Zoom sur un mot spécifique : deux panneaux.
      - Gauche  : séries temporelles Press vs Twitter
      - Droite  : cross-correlogramme (barres par lag)
    """
    if word not in propagation:
        print(f"'{word}' non trouvé dans les résultats de propagation.")
        return None

    info    = propagation[word]
    sp      = series_press[word]
    st      = series_twitter[word]
    dts     = [_m2dt(m) for m in months]
    cc_full = info["cc_full"]
    lags    = list(cc_full.keys())
    cc_vals = list(cc_full.values())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))
    fig.patch.set_facecolor(COLORS["bg"])

    # ── Séries temporelles ────────────────────────────────────
    ax1.set_facecolor(COLORS["bg"])
    ax1.plot(dts, sp, color=COLORS["press"],   lw=2, label="Presse")
    ax1.plot(dts, st, color=COLORS["twitter"], lw=2, label="Twitter")
    ax1.fill_between(dts, sp, alpha=0.15, color=COLORS["press"])
    ax1.fill_between(dts, st, alpha=0.12, color=COLORS["twitter"])

    for mk in SCANDALS:
        if mk in months:
            ax1.axvline(_m2dt(mk), color="gray", lw=1, ls=":", alpha=0.6)

    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=8)
    ax1.set_ylabel("Fréquence relative", fontsize=10)
    ax1.set_title(f'"{word}" — fréquence Presse vs Twitter', fontsize=11, fontweight="bold")
    ax1.legend(fontsize=9, framealpha=0.85)
    ax1.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)

    # ── Cross-correlogramme ───────────────────────────────────
    ax2.set_facecolor(COLORS["bg"])
    bar_colors = [
        COLORS["tw_leads"] if l < 0
        else COLORS["pr_leads"] if l > 0
        else COLORS["simult"]
        for l in lags
    ]
    ax2.bar(lags, cc_vals, color=bar_colors, alpha=0.88, width=0.6)
    ax2.axvline(0,   color="gray", ls="--", lw=1,   alpha=0.6)
    ax2.axhline(0,   color="gray", ls="-",  lw=0.7, alpha=0.5)
    ax2.axhline(0.20, color="red", ls="--", lw=1,   alpha=0.7, label="Seuil 0.20")

    # Marquer le lag optimal
    opt_lag = info["optimal_lag"]
    ax2.bar(opt_lag, cc_full[opt_lag],
            color="gold", alpha=1.0, width=0.6,
            edgecolor="black", lw=1.5, label=f"Lag optimal = {opt_lag}")

    ax2.set_xticks(lags)
    ax2.set_xticklabels(
        [f"TW+{abs(l)}m" if l < 0 else ("0" if l == 0 else f"PR+{l}m")
         for l in lags],
        fontsize=8, rotation=20
    )
    ax2.set_ylabel("CC(k)", fontsize=10)
    dir_label = {
        "twitter_leads": "Twitter précède la Presse",
        "press_leads":   "Presse précède Twitter",
        "simultaneous":  "Réaction simultanée",
    }.get(info["direction"], "")
    ax2.set_title(
        f'Cross-correlation — {dir_label}\n(CC_max={info["cc_max"]}, lag={opt_lag})',
        fontsize=10, fontweight="bold"
    )
    ax2.legend(fontsize=8, framealpha=0.85)
    ax2.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)

    fig.suptitle(f'Propagation thématique — "{word}"',
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_top_propagation(
    propagation: Dict[str, Dict],
    months: List[str],
    series_press: Dict[str, np.ndarray],
    series_twitter: Dict[str, np.ndarray],
    top_n: int = 6,
    direction_filter: Optional[str] = None,
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Grille de cross-correlogrammes pour les top_n mots.
    direction_filter : 'twitter_leads' | 'press_leads' | 'simultaneous' | None
    """
    filtered = {
        w: info for w, info in propagation.items()
        if direction_filter is None or info["direction"] == direction_filter
    }
    words = list(filtered.keys())[:top_n]
    n     = len(words)
    if n == 0:
        print("Aucun mot à afficher.")
        return None

    cols = min(3, n)
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4.5, rows * 3.2))
    fig.patch.set_facecolor(COLORS["bg"])

    axes_flat = np.array(axes).flatten() if n > 1 else [axes]

    for i, word in enumerate(words):
        ax   = axes_flat[i]
        info = filtered[word]
        cc_full = info["cc_full"]
        lags    = list(cc_full.keys())
        cc_vals = list(cc_full.values())

        ax.set_facecolor(COLORS["bg"])
        bar_colors = [
            COLORS["tw_leads"] if l < 0
            else COLORS["pr_leads"] if l > 0
            else COLORS["simult"]
            for l in lags
        ]
        ax.bar(lags, cc_vals, color=bar_colors, alpha=0.85, width=0.6)
        ax.axvline(0,    color="gray", ls="--", lw=1,   alpha=0.5)
        ax.axhline(0,    color="gray", ls="-",  lw=0.7, alpha=0.4)
        ax.axhline(0.20, color="red",  ls="--", lw=0.8, alpha=0.6)

        opt = info["optimal_lag"]
        ax.bar(opt, cc_full[opt], color="gold", alpha=1.0,
               width=0.6, edgecolor="black", lw=1.2)

        ax.set_xticks(lags)
        ax.set_xticklabels([str(l) for l in lags], fontsize=7)
        ax.set_title(
            f'"{word}"\nlag={opt}  CC={info["cc_max"]}',
            fontsize=9, fontweight="bold"
        )
        ax.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.4)

    for j in range(n, len(axes_flat)):
        axes_flat[j].set_visible(False)

    dir_titles = {
        "twitter_leads": "Twitter en avance",
        "press_leads":   "Presse en avance",
        "simultaneous":  "Simultané",
        None:            "Tous",
    }
    fig.suptitle(
        f"Cross-correlogrammes — {dir_titles.get(direction_filter, 'Tous')}",
        fontsize=13, fontweight="bold", y=1.01
    )
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
    OUT_DIR      = "outputs_propagation"
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Chargement du corpus...")
    corpus = load_corpus(PRESS_PATH, TWITTER_PATH)
    vocab_press   = build_monthly_vocab(corpus, origin="press")
    vocab_twitter = build_monthly_vocab(corpus, origin="twitter")

    # ── Détection propagation ───────────────────────────────────
    print("Calcul de la propagation thématique...")
    propagation = detect_propagation(
        vocab_press, vocab_twitter,
        top_n=75, max_lag=4, min_cc=0.20
    )

    # Reconstruire les séries pour les plots par mot
    months, series_press, series_twitter = build_aligned_series(
        vocab_press, vocab_twitter, top_n=75
    )

    # ── Résumé console ─────────────────────────────────────────
    print(f"\nMots avec propagation significative : {len(propagation)}")

    directions = Counter(info["direction"] for info in propagation.values())
    print(f"\n  Twitter en avance : {directions.get('twitter_leads', 0)} mots")
    print(f"  Simultané         : {directions.get('simultaneous', 0)} mots")
    print(f"  Presse en avance  : {directions.get('press_leads', 0)} mots")

    print("\n── Top 10 mots — Twitter en avance ──")
    tw_leads = {w: i for w, i in propagation.items() if i["direction"] == "twitter_leads"}
    for w, info in list(tw_leads.items())[:10]:
        print(f"  {w:20s}  lag={info['optimal_lag']}  CC={info['cc_max']:.3f}")

    print("\n── Top 10 mots — Presse en avance ──")
    pr_leads = {w: i for w, i in propagation.items() if i["direction"] == "press_leads"}
    for w, info in list(pr_leads.items())[:10]:
        print(f"  {w:20s}  lag={info['optimal_lag']}  CC={info['cc_max']:.3f}")

    # ── Visualisations ──────────────────────────────────────────
    print("\nGénération des visualisations...")

    plot_propagation_summary(
        propagation,
        output_path=f"{OUT_DIR}/01_propagation_summary.png", show=False
    )
    print("  ✓ 01_propagation_summary.png")

    # Zoom sur quelques mots clés
    for word in ["food", "sales", "menu", "customers"]:
        if word in propagation:
            plot_word_propagation(
                word, propagation, months, series_press, series_twitter,
                output_path=f"{OUT_DIR}/02_word_{word}.png", show=False
            )
            print(f"  ✓ 02_word_{word}.png")

    plot_top_propagation(
        propagation, months, series_press, series_twitter,
        top_n=6, direction_filter="twitter_leads",
        output_path=f"{OUT_DIR}/03_top_twitter_leads.png", show=False
    )
    print("  ✓ 03_top_twitter_leads.png")

    plot_top_propagation(
        propagation, months, series_press, series_twitter,
        top_n=6, direction_filter="press_leads",
        output_path=f"{OUT_DIR}/04_top_press_leads.png", show=False
    )
    print("  ✓ 04_top_press_leads.png")

    print(f"\nTous les graphiques dans '{OUT_DIR}/'")