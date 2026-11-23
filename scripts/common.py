"""Shared by the scripts: reading the stored prices and computing the weekly series.

Method of the article's back-test (Section 7.2), as it was run:
  prices   daily, resampled to weeks ending Friday (the last value of the week);
  c_t      max(0.03, (P_t / P_{t-104})^(1/2) - 1): the annualized return of the trailing 104 weeks;
  K_t      P_{t+52} / (P_t (1 + c_t)), eq. (43);    raw gain = K_t - 1, eq. (44);
  c_eff    (1 + c_t) / K_t - 1, a rate per year.
"""
import pathlib

import numpy as np
import pandas as pd

# id in this package -> label in the article's tables
ASSETS = {"BTC": "BTC-USD", "US_MARKET": "VTI", "GLD": "GLD"}
WINDOW, HORIZON, FLOOR = 104, 52, 0.03


def daily_prices(data_dir) -> pd.DataFrame:
    d = pathlib.Path(data_dir)
    btc = pd.read_csv(d / "btc_daily.csv", index_col="date", parse_dates=True)["price_usd"]
    gld = pd.read_csv(d / "gld_daily.csv", index_col="date", parse_dates=True)["close"]
    m = pd.read_csv(d / "us_market_daily.csv", index_col="date", parse_dates=True)
    ret = (m["mkt_rf"] + m["rf"]) / 100          # total return of the US market on each trading day
    ret.iloc[0] = 0.0                            # the index starts at 100 at the close of the first day
    market = 100 * (1 + ret).cumprod()
    return pd.concat({"BTC": btc, "US_MARKET": market, "GLD": gld}, axis=1).sort_index()


def weekly_prices(data_dir) -> pd.DataFrame:
    return daily_prices(data_dir).resample("W-FRI").last().dropna(how="all")


def primitives(prices: pd.DataFrame) -> dict[str, pd.DataFrame]:
    c = ((prices / prices.shift(WINDOW)) ** (52 / WINDOW) - 1).clip(lower=FLOOR).iloc[WINDOW:]
    K = prices.shift(-HORIZON).loc[c.index] / (prices.loc[c.index] * (1 + c))
    return {"c": c, "K": K, "g_raw": K - 1, "c_eff": (1 + c) / K - 1}


def describe(frame: pd.DataFrame) -> pd.DataFrame:
    """The statistics of the article's tables: sample standard deviation, quartiles by linear
    interpolation, skewness and excess kurtosis without bias adjustment."""
    rows = {}
    for asset in ASSETS:
        x = frame[asset].dropna().to_numpy()
        dev = x - x.mean()
        m2, m3, m4 = (dev ** 2).mean(), (dev ** 3).mean(), (dev ** 4).mean()
        q25, q50, q75 = np.quantile(x, [0.25, 0.5, 0.75])
        rows[asset] = {"count": len(x), "mean": x.mean(), "std": x.std(ddof=1), "min": x.min(), "q25": q25,
                       "median": q50, "q75": q75, "max": x.max(), "skew": m3 / m2 ** 1.5,
                       "excess_kurtosis": m4 / m2 ** 2 - 3}
    out = pd.DataFrame.from_dict(rows, orient="index")
    out.index.name = "asset"
    return out
