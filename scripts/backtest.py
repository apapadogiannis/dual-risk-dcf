"""Back-test of the dual-risk proxies on Bitcoin, US equities and gold (Section 7.2).

Produces
  weekly_series.csv        price, c, K, raw gain and c_eff by week and asset      (Fig. 6)
  table3_c_stats.csv       descriptive statistics of the benchmark rate c         (Table 3)
  table4_K_stats.csv       descriptive statistics of the valuation ratio K        (Table 4)
  table5_ceff_stats.csv    descriptive statistics of the effective rate c_eff     (Table 5)
  g_raw_stats.csv          descriptive statistics of the raw gain K - 1           (Fig. 9)

Usage: python3 -I scripts/backtest.py DATA_DIR OUT_DIR
"""
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ASSETS, describe, primitives, weekly_prices


def main(data_dir: str, out_dir: str) -> None:
    out = pathlib.Path(out_dir)
    prices = weekly_prices(data_dir)
    p = primitives(prices)
    parts = []
    for asset in ASSETS:
        f = pd.DataFrame({"asset": asset, "price": prices[asset].loc[p["c"].index],
                          **{k: v[asset] for k, v in p.items()}}).dropna(subset=["c"])
        parts.append(f)
    weekly = pd.concat(parts)
    weekly.index.name = "week_ending"
    weekly.to_csv(out / "weekly_series.csv", float_format="%.12g")
    for key, name in (("c", "table3_c_stats"), ("K", "table4_K_stats"), ("c_eff", "table5_ceff_stats"), ("g_raw", "g_raw_stats")):
        describe(p[key]).to_csv(out / f"{name}.csv", float_format="%.12g")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
