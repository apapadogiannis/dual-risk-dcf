"""Sets every entry of the article's Tables 3 to 5 beside the value this package computes.

The article used daily adjusted closes of VTI, GLD and BTC-USD from one vendor. This package
stores Bitcoin and US equity series from other sources (see the README), so two of the three
assets are reproduced closely and not exactly. Gold uses the same prices as the article.

Produces
  published_vs_rebuilt.csv   table, asset, statistic, published value, value here, difference
  published_vs_rebuilt_summary.csv   by asset: entries, entries equal at the printed precision,
                                     largest relative difference

Usage: python3 -I scripts/compare_published.py DATA_DIR OUT_DIR   (after backtest.py)
"""
import pathlib
import sys
from decimal import Decimal

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ASSETS

FILES = {"table3_c": "table3_c_stats.csv", "table4_K": "table4_K_stats.csv", "table5_ceff": "table5_ceff_stats.csv"}


def main(data_dir: str, out_dir: str) -> None:
    out = pathlib.Path(out_dir)
    label_to_id = {v: k for k, v in ASSETS.items()}
    pub = pd.read_csv(pathlib.Path(data_dir) / "published_tables.csv", dtype=str)
    here = {t: pd.read_csv(out / f, index_col="asset") for t, f in FILES.items()}
    rows = []
    for r in pub.itertuples():
        asset = label_to_id[r.asset]
        value = float(here[r.table].loc[asset, r.stat])
        decimals = -Decimal(r.value).as_tuple().exponent
        published = float(r.value)
        rows.append({"table": r.table, "asset": asset, "article_label": r.asset, "stat": r.stat,
                     "published": r.value, "rebuilt": value, "difference": value - published,
                     "relative_difference": (value - published) / abs(published) if published else 0.0,
                     "equal_as_printed": int(round(value, decimals) == published)})
    table = pd.DataFrame(rows)
    table.to_csv(out / "published_vs_rebuilt.csv", index=False, float_format="%.12g")
    g = table.groupby("asset", sort=False)
    summary = pd.DataFrame({"entries": g.size(), "equal_as_printed": g["equal_as_printed"].sum(),
                            "largest_relative_difference": g["relative_difference"].apply(lambda x: x.abs().max()),
                            "median_relative_difference": g["relative_difference"].apply(lambda x: x.abs().median())})
    summary.to_csv(out / "published_vs_rebuilt_summary.csv", float_format="%.12g")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
