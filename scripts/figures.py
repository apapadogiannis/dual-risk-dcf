"""Figures 6 to 10 of the article, redrawn from outputs/weekly_series.csv.

Produces
  fig6_timeseries.png/.pdf     weekly c, K, raw gain and c_eff for the three assets   (Fig. 6)
  fig7_pdf_cdf_c.png/.pdf      distribution of c                                     (Fig. 7)
  fig8_pdf_cdf_K.png/.pdf      distribution of K                                     (Fig. 8)
  fig9_pdf_cdf_g_raw.png/.pdf  distribution of the raw gain                          (Fig. 9)
  fig10_pdf_cdf_c_eff.png/.pdf distribution of c_eff                                 (Fig. 10)

Figures 1 to 5 of the article are diagrams and curves of formulas, drawn in its LaTeX source.

Usage: python3 -I scripts/figures.py DATA_DIR OUT_DIR   (after backtest.py)
"""
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ASSETS

COLORS = {"BTC": "tab:red", "US_MARKET": "tab:blue", "GLD": "tab:green"}
NAMES = {"BTC": "Bitcoin", "US_MARKET": "US equities", "GLD": "Gold (GLD)"}
plt.style.use("ggplot")
plt.rcParams.update({"font.family": "serif", "font.size": 12, "axes.titlesize": 14, "legend.fontsize": 10,
                     "lines.linewidth": 1.8, "grid.color": "#dddddd", "svg.hashsalt": "dual-risk"})


def save(fig, out, name):
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}", dpi=200, metadata={"CreationDate": None} if ext == "pdf" else None)
    plt.close(fig)


def main(data_dir: str, out_dir: str) -> None:
    out = pathlib.Path(out_dir)
    w = pd.read_csv(out / "weekly_series.csv", parse_dates=["week_ending"])
    series = {k: w.pivot(index="week_ending", columns="asset", values=k) for k in ("c", "K", "g_raw", "c_eff")}

    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True, constrained_layout=True)
    panels = (("c", "Benchmark rate ($c_t$)", "$c_t$", None),
              ("K", "Valuation ratio ($K_t = P_{t+1y}/[P_t(1+c_t)]$)", "$K_t$", 1),
              ("g_raw", "Raw gain ($K_t - 1$)", "$K_t - 1$", 0),
              ("c_eff", r"Effective rate ($c_{\mathrm{eff},t} = (1+c_t)/K_t - 1$, one-year horizon)", r"$c_{\mathrm{eff},t}$", None))
    for ax, (key, title, ylabel, line) in zip(axes, panels):
        for a in ASSETS:
            ax.plot(series[key].index, series[key][a], color=COLORS[a], label=NAMES[a])
        if line is not None:
            ax.axhline(line, color="black", lw=0.8)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
    axes[3].set_yscale("symlog", linthresh=0.03)
    save(fig, out, "fig6_timeseries")

    for key, symbol, name in (("c", "c_t", "fig7_pdf_cdf_c"), ("K", "K_t", "fig8_pdf_cdf_K"),
                              ("g_raw", "K_t - 1", "fig9_pdf_cdf_g_raw"), ("c_eff", r"c_{\mathrm{eff},t}", "fig10_pdf_cdf_c_eff")):
        fig, axes = plt.subplots(len(ASSETS), 2, figsize=(10, 4 * len(ASSETS)), constrained_layout=True)
        for i, a in enumerate(ASSETS):
            x = series[key][a].dropna().to_numpy()
            ax_pdf, ax_cdf = axes[i]
            ax_pdf.hist(x, bins=50, density=True, alpha=0.6, color=COLORS[a])
            grid = np.linspace(x.min(), x.max(), 200)
            ax_pdf.plot(grid, gaussian_kde(x)(grid), color="black", lw=1.2)
            ax_pdf.set_title(f"{NAMES[a]}: density of ${symbol}$")
            ax_pdf.set_xlabel(f"${symbol}$")
            xs = np.sort(x)
            ax_cdf.plot(xs, np.arange(1, len(xs) + 1) / len(xs), color=COLORS[a], lw=1.5)
            ax_cdf.set_title(f"{NAMES[a]}: cumulative distribution of ${symbol}$")
            ax_cdf.set_xlabel(f"${symbol}$")
            ax_cdf.set_ylabel("Share of weeks at or below")
        save(fig, out, name)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
