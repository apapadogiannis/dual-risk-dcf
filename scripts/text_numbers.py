"""Numbers that the article states in its text and that are in none of its tables.

Produces
  text_numbers.csv   one row per quantity: where the article states it, what the article says,
                     the asset, and the value computed here

Covers the sample (Section 7.2), the paragraphs "Dynamic behavior", "Distributional insights",
"Sensitivity to c_min" and "Cross-asset contrasts", and the two values of K read off Fig. 3.

Usage: python3 -I scripts/text_numbers.py DATA_DIR OUT_DIR
"""
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ASSETS, FLOOR, primitives, weekly_prices


def main(data_dir: str, out_dir: str) -> None:
    prices = weekly_prices(data_dir)
    p = primitives(prices)
    c, K, ce = p["c"], p["K"].dropna(), p["c_eff"].dropna()
    rows = []

    def add(where, says, quantity, asset, value):
        rows.append({"where": where, "article_says": says, "quantity": quantity, "asset": asset, "value": value})

    add("Section 7.2", "sample spans January 2017 through May 2025", "first week with a benchmark rate c", "all", str(c.index[0].date()))
    add("Section 7.2", "sample spans January 2017 through May 2025", "last week with a benchmark rate c", "all", str(c.index[-1].date()))
    add("Section 7.2", "sample spans January 2017 through May 2025", "last week with a valuation ratio K", "all", str(K.index[-1].date()))
    add("Section 7.2", "weekly total-return data", "first week of prices", "all", str(prices.index[0].date()))
    for a in ASSETS:
        add("Sensitivity to c_min", "floor has almost no effect on VTI or GLD; Bitcoin is frequently at the floor",
            "share of weeks in which c is at the 3% floor", a, float((c[a] <= FLOOR).mean()))
    add("Dynamic behavior", "Bitcoin's c peaks above 500%", "largest c", "BTC", float(c["BTC"].max()))
    add("Dynamic behavior", "in deep downturns K > 2", "share of weeks with K above 2", "BTC", float((K["BTC"] > 2).mean()))
    add("Dynamic behavior", "in boom phases K < 0.5", "share of weeks with K below 0.5", "BTC", float((K["BTC"] < 0.5).mean()))
    for a in ("US_MARKET", "GLD"):
        add("Dynamic behavior", "VTI and GLD stay within +/-10% of fair value", "share of weeks with K between 0.9 and 1.1", a,
            float(((K[a] >= 0.9) & (K[a] <= 1.1)).mean()))
        add("Descriptive statistics", "interquartile ranges within +/-10%", "25th percentile of K", a, float(K[a].quantile(0.25)))
        add("Descriptive statistics", "interquartile ranges within +/-10%", "75th percentile of K", a, float(K[a].quantile(0.75)))
        add("Descriptive statistics", "VTI and GLD stay within roughly 0%-30%", "share of weeks with c_eff between 0 and 0.30", a,
            float(((ce[a] >= 0) & (ce[a] <= 0.30)).mean()))
        add("Descriptive statistics", "VTI and GLD stay within roughly 0%-30%", "smallest c_eff", a, float(ce[a].min()))
        add("Descriptive statistics", "VTI and GLD stay within roughly 0%-30%", "largest c_eff", a, float(ce[a].max()))
    add("Distributional insights", "Bitcoin raw gains up to +900%", "largest raw gain K - 1", "BTC", float(K["BTC"].max() - 1))
    add("Distributional insights", "VTI raw gain within +/-75%", "smallest raw gain", "US_MARKET", float(K["US_MARKET"].min() - 1))
    add("Distributional insights", "VTI raw gain within +/-75%", "largest raw gain", "US_MARKET", float(K["US_MARKET"].max() - 1))
    add("Distributional insights", "GLD raw gain within +/-40%", "smallest raw gain", "GLD", float(K["GLD"].min() - 1))
    add("Distributional insights", "GLD raw gain within +/-40%", "largest raw gain", "GLD", float(K["GLD"].max() - 1))
    add("Distributional insights", "GLD c of about 5%", "median c", "GLD", float(c["GLD"].median()))
    for g in (0.2, -0.2):
        add("Section 6.1, under Fig. 3", "at c = 10% and five years, g = 0.2 gives K of about 1.12 and g = -0.2 about 0.88",
            f"K for g = {g}", "none", 1 + g / 1.10 ** 5)
    pd.DataFrame(rows).to_csv(pathlib.Path(out_dir) / "text_numbers.csv", index=False, float_format="%.12g")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
