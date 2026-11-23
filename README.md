# From unified discounting to dual-risk: A new lens on DCF valuation

[![Article](https://img.shields.io/badge/Finance%20Research%20Open-10.1016%2Fj.finr.2026.100096-1f4e79)](https://doi.org/10.1016/j.finr.2026.100096)
[![SSRN](https://img.shields.io/badge/SSRN-10.2139%2Fssrn.5252774-1f4e79)](https://doi.org/10.2139/ssrn.5252774)
[![replication](https://github.com/apapadogiannis/dual-risk-dcf/actions/workflows/replicate.yml/badge.svg)](https://github.com/apapadogiannis/dual-risk-dcf/actions/workflows/replicate.yml)

Replication package for the paper by Agisilaos Papadogiannis, published in *Finance Research Open* 2(1), 100096 (2026).
Paper: `paper/finr-2-100096.pdf` (published version, open access under CC BY 4.0); journal page: [doi:10.1016/j.finr.2026.100096](https://doi.org/10.1016/j.finr.2026.100096); preprint on SSRN: [doi:10.2139/ssrn.5252774](https://doi.org/10.2139/ssrn.5252774).
Calculator and MCP server for the paper's formulas, for your own forecasts and prices: [apapadogiannis/dual-risk-calculator](https://github.com/apapadogiannis/dual-risk-calculator).

## What this is

The paper separates two things that a single discount rate mixes in a discounted cash flow value:

1. **The benchmark cost of capital, c.** What the money could earn in the closest comparable
   alternative. It is set outside the asset.
2. **The valuation ratio, K.** The benchmark fair value divided by the valuation examined. It
   carries the whole gap between two views of the asset's benefits. From c and K the paper derives
   the gain of capital, g = (1 + c)^h (K - 1), and the effective rate, c_eff = (1 + c) K^(-1/h) - 1.
3. **An illustration on prices.** For Bitcoin, US equities and gold the paper computes c from each
   asset's own trailing two-year return and K from the price one year later, week by week, and
   reports the distributions (Section 7.2, Tables 3 to 5, Figures 6 to 10).

The paper is mainly theory. This package reproduces its one computation, the illustration of
point 3, and sets every published table entry beside the recomputed one.

## How closely the published tables are reproduced

The paper used daily adjusted closes of VTI, GLD and BTC-USD from Yahoo Finance, downloaded in
2025. This package stores other sources for two of the three assets (see "Data and licensing"), so:

- **Gold** uses the same prices as the paper. 26 of its 27 table entries are equal at the
  printed precision. The remaining one is the minimum of K: the paper prints 0.6689 and the value
  is 0.66895.
- **Bitcoin** uses Coin Metrics prices. Entries differ from the published ones by
  0.4% at the median and 2.9% at most.
- **US equities** use the total return of the whole US market from the Kenneth R. French data
  library, standing in for VTI, the fund that tracks that market. Entries differ by 2.0% at the
  median. The largest relative differences are in entries close to zero (skewness, the median of
  c_eff).
- From the original price file, which is not redistributed here, the same scripts reproduce all
  81 published entries but that one.

| | Asset | Mean, paper | Mean, here | Median, paper | Median, here |
|---|---|---|---|---|---|
| c | Bitcoin | 1.1394 | 1.1381 | 0.8603 | 0.8695 |
| c | US equities | 0.1331 | 0.1381 | 0.1184 | 0.1220 |
| c | Gold | 0.0860 | 0.0860 | 0.0610 | 0.0610 |
| K | Bitcoin | 1.5632 | 1.5609 | 0.8585 | 0.8625 |
| K | US equities | 1.0269 | 1.0275 | 1.0454 | 1.0558 |
| K | Gold | 1.0264 | 1.0264 | 1.0271 | 1.0271 |
| c_eff | Bitcoin | 8.6071 | 8.6014 | 1.2812 | 1.2439 |
| c_eff | US equities | 0.1588 | 0.1670 | 0.0632 | 0.0473 |
| c_eff | Gold | 0.0807 | 0.0807 | 0.0137 | 0.0137 |

`outputs/published_vs_rebuilt.csv` has all 81 entries.

## Notes for replication

The tables and figures of the paper are reproduced. Anyone repeating the computation should
follow it as it is set out here and in `scripts/common.py`, which is more specific than the
paper's text on four points:

- **Sample.** Daily prices from 1 January 2015 to 30 December 2024. The first two years feed the
  trailing window, so c covers 419 weeks from the last week of 2016 to the first week of 2025, and
  K covers 367 weeks to the first week of 2024. (The paper describes the sample as January 2017
  through May 2025.)
- **Effective rate.** Table 5 and Figures 6 and 10 show the yearly rate, (1 + c)/K - 1, which is
  eq. (26) at a horizon of one year. The power of 1/52 written in eq. (45) is not applied.
- **Benchmark rate.** c is the annualized return over the 104 weeks ending at week t,
  (P_t / P_{t-104})^(1/2) - 1, floored at 3%.
- **Statistics.** Sample standard deviation, quartiles by linear interpolation, and skewness
  without bias adjustment.

`outputs/text_numbers.csv` adds detail to the paper's description of the series: how often the 3%
floor binds (31% of the weeks for gold, 20% for Bitcoin, 15% for US equities), how often K lies
within 10% of one (34% of the weeks for US equities, 42% for gold), and the range of the effective
rate. Each K uses a price one year later, so the series is a reading in hindsight, as the paper
says.

## Layout

```
scripts/    one script per calculation
outputs/    every result table (CSV)
figures/    Figures 6 to 10 (PNG and PDF)
data/       all input data
paper/      the published article
run_all.sh  runs every script in order
check_outputs.py  reruns the pipeline and checks every stored result
```

## Reproducing

Requirements: Python 3.11+, `pip install -r requirements.txt` (pandas, numpy, matplotlib, scipy).
`requirements-lock.txt` lists the exact versions under which `outputs/` were generated.

```bash
./run_all.sh    # runs every script below in order, under a minute
```

The scripts are deterministic and read only the files in `data/`. A GitHub Actions workflow
re-runs the pipeline on every push and monthly, and fails if any stored result is not reproduced
(see "How the check works"). Each script takes `python3 -I <script>.py DATA_DIR OUT_DIR`.

| Script | What it produces | Where it appears |
|---|---|---|
| `common.py` | Reads the prices and computes the weekly c, K, raw gain and c_eff | used by the other scripts |
| `backtest.py` | The weekly series and the descriptive statistics | Tables 3 to 5; the series of Figure 6 |
| `compare_published.py` | Every published table entry beside the recomputed one | not in the paper |
| `text_numbers.py` | The numbers stated in the text of Sections 6.1 and 7.2 | Sections 6.1 and 7.2 |
| `figures.py` | The time series and the four distribution panels | Figures 6 to 10 |

Figures 1 to 5 of the paper are diagrams and curves of formulas with no data behind them.

## How the check works

```bash
python3 check_outputs.py    # reruns ./run_all.sh, then compares
```

1. The result tables in `outputs/` are stored in this repository as the scripts wrote them.
2. `check_outputs.py` sets the stored copies aside, reruns `./run_all.sh` on the files in `data/`,
   and compares the fresh files with the stored ones, number by number.
3. A number counts as reproduced if it agrees with the stored one to nine significant digits
   (relative tolerance 1e-9). Text, labels and whole numbers must match exactly. Any other
   difference is listed and the check fails.

Why a tolerance and not a character-by-character match: the last digits of a floating-point
result depend on the processor and on the build of the numerical libraries, so two correct runs
on different machines can differ in the 12th to 16th significant digit.

The workflow behind the badge runs the pipeline on a new machine with the pinned package
versions, on every push and once a month, and applies the same comparison.

Three limits. The check compares regenerated with stored results; the comparison with the paper
is the separate table `outputs/published_vs_rebuilt.csv`, whose published column was transcribed
from the paper. Figures are redrawn from the same values but are not compared, because image
files can differ slightly between versions of the plotting library. And the check shows that the
results follow from the data and the code, not that the data or the argument is right.

## Data and licensing

- Bitcoin: `data/btc_daily.csv`, the daily reference price `PriceUSD` from the
  [Coin Metrics community data](https://coinmetrics.io/community-network-data/), 1 January 2015 to
  30 December 2024, retrieved 23 November 2026. Licensed CC BY-NC 4.0 (non-commercial use, with
  attribution).
- US equities: `data/us_market_daily.csv`, the daily excess return of the US market (`mkt_rf`) and
  the daily bill rate (`rf`), in per cent, 2 January 2015 to 30 December 2024, from the Fama/French
  3 Factors [Daily] file of the
  [Kenneth R. French data library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html),
  retrieved 23 November 2026 (file built on the September 2026 CRSP database). Copyright Eugene F.
  Fama and Kenneth R. French. `scripts/common.py` compounds their sum into an index.
- Gold: `data/gld_daily.csv`, the daily close of SPDR Gold Shares (GLD), 2 January 2015 to
  30 December 2024, from Yahoo Finance, retrieved in 2025. The fund pays no distributions, so its
  close and its adjusted close are the same series.
- `data/published_tables.csv`: Tables 3 to 5 of the paper, transcribed from the manuscript.
- Code: MIT License. Output tables and figures (`outputs/`, `figures/`): CC BY 4.0, cite the paper.
  The paper: CC BY 4.0. Third-party data keep their own terms and are not covered by either.

## Citation

> Papadogiannis, A. (2026). "From unified discounting to dual-risk: A new lens on DCF valuation." *Finance Research Open* 2(1), 100096.
> https://doi.org/10.1016/j.finr.2026.100096
> SSRN: https://doi.org/10.2139/ssrn.5252774

## Disclaimer

Independent research, conducted without funding. For informational and academic purposes only. Not
financial, investment, tax or legal advice, and not a recommendation to buy or sell any financial
instrument.
