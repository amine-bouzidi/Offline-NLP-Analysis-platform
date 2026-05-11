"""
Module d'analyse temporelle pour corpus multiplateforme
Étape 4.1 — Préparation temporelle et foulescopie

Fonctions :
  - Chargement et normalisation des données press/twitter
  - Agrégations temporelles (jour, semaine, mois, trimestre)
  - Détection de pics d'activité (z-score)
  - Visualisations matplotlib (activité, comparaison, heatmap, pics)
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec


# ─────────────────────────────────────────────
# 1. CHARGEMENT ET NORMALISATION
# ─────────────────────────────────────────────

def load_press(path: str) -> List[Dict]:
    """
    Charge le fichier press_scrapper.json et normalise les dates.
    Retourne une liste de dicts avec au moins : date (datetime.date), source, text, title.
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    articles = raw.get("articles", raw) if isinstance(raw, dict) else raw
    normalized = []
    for art in articles:
        raw_date = art.get("date", "")
        try:
            parsed = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        normalized.append({
            "date":       parsed,
            "year_month": parsed.strftime("%Y-%m"),
            "year":       parsed.year,
            "source":     art.get("source", "unknown"),
            "title":      art.get("title", ""),
            "text":       art.get("text", ""),
            "origin":     "press",
        })
    return normalized


def load_twitter(path: str) -> List[Dict]:
    """
    Charge le fichier twitter_scraper.json et normalise les dates.
    Retourne une liste de dicts avec au moins : date (datetime.date), handle, text.
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    tweets = raw.get("tweets", raw) if isinstance(raw, dict) else raw
    normalized = []
    for tw in tweets:
        raw_date = tw.get("date", "")
        try:
            # Format ISO : 2022-10-30T07:57:27.000Z
            parsed = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        normalized.append({
            "date":       parsed,
            "year_month": parsed.strftime("%Y-%m"),
            "year":       parsed.year,
            "handle":     tw.get("handle", ""),
            "followers":  tw.get("nb_followers", 0),
            "text":       tw.get("text", ""),
            "origin":     "twitter",
        })
    return normalized


def load_corpus(press_path: str, twitter_path: str) -> List[Dict]:
    """Charge et fusionne les deux sources en un corpus unifié."""
    press   = load_press(press_path)
    twitter = load_twitter(twitter_path)
    corpus  = press + twitter
    corpus.sort(key=lambda x: x["date"])
    return corpus


# ─────────────────────────────────────────────
# 2. FONCTIONS D'AGRÉGATION TEMPORELLE
# ─────────────────────────────────────────────

def aggregate_by_day(docs: List[Dict], origin: Optional[str] = None) -> Dict[date, int]:
    """
    Agrège les documents par jour.
    origin : 'press' | 'twitter' | None (tous)
    """
    if origin:
        docs = [d for d in docs if d.get("origin") == origin]
    counter: Counter = Counter(d["date"] for d in docs)
    return dict(sorted(counter.items()))


def aggregate_by_week(docs: List[Dict], origin: Optional[str] = None) -> Dict[date, int]:
    """
    Agrège les documents par semaine ISO (lundi de la semaine).
    """
    if origin:
        docs = [d for d in docs if d.get("origin") == origin]
    counter: Counter = Counter()
    for d in docs:
        monday = d["date"] - __import__("datetime").timedelta(days=d["date"].weekday())
        counter[monday] += 1
    return dict(sorted(counter.items()))


def aggregate_by_month(docs: List[Dict], origin: Optional[str] = None) -> Dict[str, int]:
    """
    Agrège les documents par mois (clé : 'YYYY-MM').
    """
    if origin:
        docs = [d for d in docs if d.get("origin") == origin]
    counter: Counter = Counter(d["year_month"] for d in docs)
    return dict(sorted(counter.items()))


def aggregate_by_quarter(docs: List[Dict], origin: Optional[str] = None) -> Dict[str, int]:
    """
    Agrège par trimestre (clé : 'YYYY-QN').
    """
    if origin:
        docs = [d for d in docs if d.get("origin") == origin]
    counter: Counter = Counter()
    for d in docs:
        q = (d["date"].month - 1) // 3 + 1
        counter[f"{d['date'].year}-Q{q}"] += 1
    return dict(sorted(counter.items()))


def aggregate_by_source(docs: List[Dict], granularity: str = "month") -> Dict[str, Dict]:
    """
    Agrège par source ET par granularité temporelle.
    Retourne {source: {période: count}}.
    granularity : 'month' | 'quarter' | 'year'
    """
    result: Dict[str, Counter] = defaultdict(Counter)
    for d in docs:
        if granularity == "month":
            period = d["year_month"]
        elif granularity == "quarter":
            q = (d["date"].month - 1) // 3 + 1
            period = f"{d['date'].year}-Q{q}"
        else:
            period = str(d["date"].year)
        result[d.get("origin", "unknown")][period] += 1
    return {src: dict(sorted(c.items())) for src, c in result.items()}


def detect_activity_peaks(
    monthly: Dict[str, int],
    z_threshold: float = 2.0
) -> Dict[str, dict]:
    """
    Détecte les pics d'activité par z-score.
    Retourne les mois dont le z-score dépasse z_threshold.

    Retourne un dict {mois: {'count': int, 'z_score': float, 'ratio_vs_mean': float}}
    """
    if len(monthly) < 3:
        return {}

    values = np.array(list(monthly.values()), dtype=float)
    mean   = values.mean()
    std    = values.std()

    if std == 0:
        return {}

    peaks = {}
    for month, count in monthly.items():
        z = (count - mean) / std
        if z >= z_threshold:
            peaks[month] = {
                "count":          count,
                "z_score":        round(float(z), 2),
                "ratio_vs_mean":  round(count / mean, 2),
            }
    return dict(sorted(peaks.items(), key=lambda x: -x[1]["z_score"]))


def temporal_summary(
    docs: List[Dict],
    scandals: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Résumé temporel complet : plage de dates, distributions, pics par source.
    """
    if not docs:
        return {}

    dates    = [d["date"] for d in docs]
    monthly  = aggregate_by_month(docs)
    by_src   = aggregate_by_source(docs, granularity="month")
    peaks    = detect_activity_peaks(monthly)

    return {
        "date_range":    {"start": str(min(dates)), "end": str(max(dates))},
        "total_docs":    len(docs),
        "by_origin":     {
            origin: len([d for d in docs if d["origin"] == origin])
            for origin in ("press", "twitter")
        },
        "monthly":       monthly,
        "by_source":     by_src,
        "peaks":         peaks,
        "scandals":      scandals or {},
    }


# ─────────────────────────────────────────────
# 3. VISUALISATIONS
# ─────────────────────────────────────────────

# Palette projet
COLORS = {
    "press":   "#E63946",
    "twitter": "#1D9BF0",
    "both":    "#6A4C93",
    "peak":    "#FF9F1C",
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


def _month_to_dt(m: str) -> datetime:
    return datetime.strptime(m + "-01", "%Y-%m-%d")


def plot_activity_over_time(
    monthly_press: Dict[str, int],
    monthly_twitter: Dict[str, int],
    scandals: Optional[Dict[str, str]] = None,
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Graphique principal : activité mensuelle Press vs Twitter (double axe Y).
    Marque les scandales clés en annotation verticale.
    """
    scandals = scandals or SCANDALS

    months_p = [_month_to_dt(m) for m in monthly_press]
    counts_p = list(monthly_press.values())

    months_t = [_month_to_dt(m) for m in monthly_twitter]
    counts_t = list(monthly_twitter.values())

    fig, ax1 = plt.subplots(figsize=(16, 6))
    fig.patch.set_facecolor(COLORS["bg"])
    ax1.set_facecolor(COLORS["bg"])

    # Press (axe gauche)
    ax1.fill_between(months_p, counts_p, alpha=0.25, color=COLORS["press"])
    ax1.plot(months_p, counts_p, color=COLORS["press"], lw=2.2, label="Presse")
    ax1.set_ylabel("Articles presse / mois", color=COLORS["press"], fontsize=11)
    ax1.tick_params(axis="y", labelcolor=COLORS["press"])
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # Twitter (axe droit)
    ax2 = ax1.twinx()
    ax2.fill_between(months_t, counts_t, alpha=0.18, color=COLORS["twitter"])
    ax2.plot(months_t, counts_t, color=COLORS["twitter"], lw=2.2, label="Twitter")
    ax2.set_ylabel("Tweets / mois", color=COLORS["twitter"], fontsize=11)
    ax2.tick_params(axis="y", labelcolor=COLORS["twitter"])
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    # Annotations scandales
    for month_key, label in scandals.items():
        dt = _month_to_dt(month_key)
        ax1.axvline(dt, color=COLORS["peak"], lw=1.4, ls="--", alpha=0.8)
        ax1.text(dt, ax1.get_ylim()[1] * 0.97, label,
                 rotation=90, fontsize=7.5, color=COLORS["peak"],
                 va="top", ha="right", alpha=0.9)

    # Formatage axe X
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=9)

    ax1.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.7)

    # Légende fusionnée
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc="upper left", fontsize=10, framealpha=0.85)

    ax1.set_title("Activité mensuelle — Presse & Twitter (McDonald's)",
                  fontsize=14, fontweight="bold", pad=14)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_source_comparison(
    monthly_press: Dict[str, int],
    monthly_twitter: Dict[str, int],
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Barres côte-à-côte normalisées (% du total par source) pour comparer
    la réactivité presse vs Twitter aux mêmes périodes.
    """
    all_months = sorted(set(monthly_press) | set(monthly_twitter))

    total_p = sum(monthly_press.values()) or 1
    total_t = sum(monthly_twitter.values()) or 1

    pct_p = [monthly_press.get(m, 0) / total_p * 100 for m in all_months]
    pct_t = [monthly_twitter.get(m, 0) / total_t * 100 for m in all_months]

    x    = np.arange(len(all_months))
    w    = 0.42

    fig, ax = plt.subplots(figsize=(18, 5))
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    ax.bar(x - w/2, pct_p, w, label="Presse",  color=COLORS["press"],   alpha=0.85)
    ax.bar(x + w/2, pct_t, w, label="Twitter", color=COLORS["twitter"], alpha=0.85)

    # Marquage scandales
    for month_key in SCANDALS:
        if month_key in all_months:
            idx = all_months.index(month_key)
            ax.axvline(idx, color=COLORS["peak"], lw=1.2, ls=":", alpha=0.7)

    step = max(1, len(all_months) // 20)
    ax.set_xticks(x[::step])
    ax.set_xticklabels(all_months[::step], rotation=45, ha="right", fontsize=8)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f%%"))
    ax.set_ylabel("Part mensuelle (% du total)", fontsize=11)
    ax.set_title("Comparaison de réactivité normalisée — Presse vs Twitter",
                 fontsize=13, fontweight="bold", pad=12)
    ax.legend(fontsize=10, framealpha=0.85)
    ax.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.6)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_heatmap_by_year_month(
    docs: List[Dict],
    origin: str = "twitter",
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Heatmap : lignes = années, colonnes = mois (1–12).
    Révèle les saisonnalités et les années « chaudes ».
    """
    filtered = [d for d in docs if d["origin"] == origin]

    # Matrice année × mois
    year_month_count: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for d in filtered:
        year_month_count[d["date"].year][d["date"].month] += 1

    years  = sorted(year_month_count)
    matrix = np.array([[year_month_count[y][m] for m in range(1, 13)] for y in years],
                      dtype=float)

    fig, ax = plt.subplots(figsize=(13, max(3, len(years) * 0.65 + 1.5)))
    fig.patch.set_facecolor(COLORS["bg"])

    cmap = "YlOrRd" if origin == "twitter" else "Blues"
    im   = ax.imshow(matrix, aspect="auto", cmap=cmap, interpolation="nearest")

    ax.set_xticks(range(12))
    ax.set_xticklabels(["Jan","Fév","Mar","Avr","Mai","Jun",
                         "Jul","Aoû","Sep","Oct","Nov","Déc"], fontsize=10)
    ax.set_yticks(range(len(years)))
    ax.set_yticklabels(years, fontsize=10)

    # Valeurs dans chaque cellule
    for i, y in enumerate(years):
        for j in range(12):
            val = int(matrix[i, j])
            if val > 0:
                ax.text(j, i, f"{val:,}", ha="center", va="center",
                        fontsize=7, color="black" if val < matrix.max() * 0.6 else "white")

    plt.colorbar(im, ax=ax, shrink=0.8, label="Nombre de documents")
    label = "Twitter" if origin == "twitter" else "Presse"
    ax.set_title(f"Heatmap d'activité mensuelle — {label} (McDonald's)",
                 fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_peaks_annotated(
    monthly: Dict[str, int],
    peaks: Dict[str, dict],
    scandals: Optional[Dict[str, str]] = None,
    origin_label: str = "Corpus",
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Graphique en aires avec annotation explicite de chaque pic détecté (z-score).
    """
    scandals = scandals or SCANDALS
    months   = [_month_to_dt(m) for m in monthly]
    counts   = list(monthly.values())
    mean_val = np.mean(counts)
    std_val  = np.std(counts)

    fig, ax = plt.subplots(figsize=(16, 6))
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    color = COLORS["twitter"] if "Twitter" in origin_label else COLORS["press"]

    ax.fill_between(months, counts, alpha=0.2, color=color)
    ax.plot(months, counts, color=color, lw=2, label=origin_label)

    # Ligne moyenne + bandes ±2σ
    ax.axhline(mean_val, color="gray", ls="--", lw=1.2, alpha=0.7, label=f"Moyenne ({mean_val:.0f})")
    ax.fill_between(months,
                    mean_val + 2 * std_val,
                    mean_val - 2 * std_val,
                    color="gray", alpha=0.08, label="±2σ")

    # Annotation des pics
    for m_key, info in peaks.items():
        dt = _month_to_dt(m_key)
        ax.scatter(dt, info["count"], color=COLORS["peak"], s=80, zorder=5)
        label_text = scandals.get(m_key, m_key)
        ax.annotate(
            f"{label_text}\n(z={info['z_score']}, ×{info['ratio_vs_mean']} moy.)",
            xy=(dt, info["count"]),
            xytext=(15, 15),
            textcoords="offset points",
            fontsize=8,
            color=COLORS["peak"],
            arrowprops=dict(arrowstyle="->", color=COLORS["peak"], lw=1),
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=COLORS["peak"], alpha=0.85),
        )

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=9)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.6)
    ax.legend(fontsize=9, framealpha=0.85)
    ax.set_title(f"Pics d'activité détectés (z ≥ 2.0) — {origin_label}",
                 fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


def plot_dashboard(
    docs: List[Dict],
    scandals: Optional[Dict[str, str]] = None,
    output_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Dashboard 2×2 : activité globale / comparaison normalisée /
    heatmap Twitter / heatmap Presse.
    """
    scandals    = scandals or SCANDALS
    monthly_p   = aggregate_by_month(docs, origin="press")
    monthly_t   = aggregate_by_month(docs, origin="twitter")
    peaks_t     = detect_activity_peaks(monthly_t)
    peaks_p     = detect_activity_peaks(monthly_p)

    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor(COLORS["bg"])
    gs  = GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32)

    # ── ax1 : activité Press vs Twitter ──────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor(COLORS["bg"])

    months_p = [_month_to_dt(m) for m in monthly_p]
    months_t = [_month_to_dt(m) for m in monthly_t]

    ax1.fill_between(months_p, list(monthly_p.values()), alpha=0.22, color=COLORS["press"])
    ax1.plot(months_p, list(monthly_p.values()), color=COLORS["press"], lw=2, label="Presse")

    ax2 = ax1.twinx()
    ax2.fill_between(months_t, list(monthly_t.values()), alpha=0.18, color=COLORS["twitter"])
    ax2.plot(months_t, list(monthly_t.values()), color=COLORS["twitter"], lw=2, label="Twitter")

    for mk, lbl in scandals.items():
        dt = _month_to_dt(mk)
        ax1.axvline(dt, color=COLORS["peak"], lw=1.3, ls="--", alpha=0.8)
        ax1.text(dt, ax1.get_ylim()[1] * 0.96, lbl,
                 rotation=90, fontsize=7, color=COLORS["peak"],
                 va="top", ha="right", alpha=0.9)

    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=8)
    ax1.set_ylabel("Articles / mois", color=COLORS["press"], fontsize=10)
    ax2.set_ylabel("Tweets / mois",   color=COLORS["twitter"], fontsize=10)
    ax1.tick_params(axis="y", labelcolor=COLORS["press"])
    ax2.tick_params(axis="y", labelcolor=COLORS["twitter"])
    ax1.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.6)
    l1, lb1 = ax1.get_legend_handles_labels()
    l2, lb2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lb1 + lb2, fontsize=9, framealpha=0.85)
    ax1.set_title("Activité mensuelle — Presse & Twitter", fontsize=12, fontweight="bold")

    # ── ax3 : pics Twitter ────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor(COLORS["bg"])
    mn_t = [_month_to_dt(m) for m in monthly_t]
    ct_t = list(monthly_t.values())
    mean_t = np.mean(ct_t)
    ax3.fill_between(mn_t, ct_t, alpha=0.2, color=COLORS["twitter"])
    ax3.plot(mn_t, ct_t, color=COLORS["twitter"], lw=1.8)
    ax3.axhline(mean_t, color="gray", ls="--", lw=1, alpha=0.7)
    for mk, info in peaks_t.items():
        ax3.scatter(_month_to_dt(mk), info["count"], color=COLORS["peak"], s=60, zorder=5)
        ax3.annotate(f"z={info['z_score']}",
                     xy=(_month_to_dt(mk), info["count"]),
                     xytext=(5, 8), textcoords="offset points",
                     fontsize=7, color=COLORS["peak"])
    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=7)
    ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax3.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)
    ax3.set_title(f"Pics Twitter ({len(peaks_t)} détectés, z≥2)", fontsize=11, fontweight="bold")

    # ── ax4 : pics Presse ─────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(COLORS["bg"])
    mn_p = [_month_to_dt(m) for m in monthly_p]
    ct_p = list(monthly_p.values())
    mean_p = np.mean(ct_p)
    ax4.fill_between(mn_p, ct_p, alpha=0.22, color=COLORS["press"])
    ax4.plot(mn_p, ct_p, color=COLORS["press"], lw=1.8)
    ax4.axhline(mean_p, color="gray", ls="--", lw=1, alpha=0.7)
    for mk, info in peaks_p.items():
        ax4.scatter(_month_to_dt(mk), info["count"], color=COLORS["peak"], s=60, zorder=5)
        ax4.annotate(f"z={info['z_score']}",
                     xy=(_month_to_dt(mk), info["count"]),
                     xytext=(5, 8), textcoords="offset points",
                     fontsize=7, color=COLORS["peak"])
    ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax4.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=7)
    ax4.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax4.grid(axis="y", color=COLORS["grid"], ls="--", lw=0.5)
    ax4.set_title(f"Pics Presse ({len(peaks_p)} détectés, z≥2)", fontsize=11, fontweight="bold")

    fig.suptitle("Dashboard Temporel — Corpus McDonald's (2021–2025)",
                 fontsize=15, fontweight="bold", y=1.01)

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    return fig


# ─────────────────────────────────────────────
# 4. POINT D'ENTRÉE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    PRESS_PATH   = r"C:\Users\GAB Informatique\Documents\Master 2\PFE\plateforme_analyse_textuelle\src\semantic\press_scrapper.json"
    TWITTER_PATH = r"C:\Users\GAB Informatique\Documents\Master 2\PFE\plateforme_analyse_textuelle\src\semantic\twitter_scraper (1).json"
    OUT_DIR      = "outputs_temporal"
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Chargement du corpus…")
    corpus = load_corpus(PRESS_PATH, TWITTER_PATH)
    print(f"  → {len(corpus):,} documents chargés "
          f"({sum(1 for d in corpus if d['origin']=='press'):,} presse + "
          f"{sum(1 for d in corpus if d['origin']=='twitter'):,} tweets)")

    # Résumé temporel
    summary = temporal_summary(corpus, SCANDALS)
    print(f"\nPlage : {summary['date_range']['start']} → {summary['date_range']['end']}")
    print(f"Pics presse  : {list(detect_activity_peaks(aggregate_by_month(corpus, 'press')).keys())}")
    print(f"Pics Twitter : {list(detect_activity_peaks(aggregate_by_month(corpus, 'twitter')).keys())}")

    # Visualisations
    monthly_p = aggregate_by_month(corpus, "press")
    monthly_t = aggregate_by_month(corpus, "twitter")

    print("\nGénération des visualisations…")
    plot_activity_over_time(monthly_p, monthly_t, SCANDALS,
                            output_path=f"{OUT_DIR}/01_activity_over_time.png", show=False)
    print("  ✓ 01_activity_over_time.png")

    plot_source_comparison(monthly_p, monthly_t,
                           output_path=f"{OUT_DIR}/02_source_comparison.png", show=False)
    print("  ✓ 02_source_comparison.png")

    plot_heatmap_by_year_month(corpus, origin="twitter",
                               output_path=f"{OUT_DIR}/03_heatmap_twitter.png", show=False)
    print("  ✓ 03_heatmap_twitter.png")

    plot_heatmap_by_year_month(corpus, origin="press",
                               output_path=f"{OUT_DIR}/04_heatmap_press.png", show=False)
    print("  ✓ 04_heatmap_press.png")

    peaks_t = detect_activity_peaks(monthly_t)
    plot_peaks_annotated(monthly_t, peaks_t, SCANDALS, "Twitter",
                         output_path=f"{OUT_DIR}/05_peaks_twitter.png", show=False)
    print("  ✓ 05_peaks_twitter.png")

    peaks_p = detect_activity_peaks(monthly_p)
    plot_peaks_annotated(monthly_p, peaks_p, SCANDALS, "Presse",
                         output_path=f"{OUT_DIR}/06_peaks_press.png", show=False)
    print("  ✓ 06_peaks_press.png")

    plot_dashboard(corpus, SCANDALS,
                   output_path=f"{OUT_DIR}/07_dashboard.png", show=False)
    print("  ✓ 07_dashboard.png")

    print(f"\nTous les graphiques sont dans le dossier '{OUT_DIR}/'")