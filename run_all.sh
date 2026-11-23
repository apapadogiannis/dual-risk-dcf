#!/usr/bin/env bash
# Reproduces the back-test of the article: the weekly series, Tables 3 to 5, the numbers stated in
# the text, the comparison with the published tables and Figures 6 to 10. Runs in under a minute.
set -e
cd "$(dirname "$0")/scripts"
mkdir -p ../outputs ../figures
for f in backtest compare_published text_numbers figures; do
  echo "== $f"; python3 -I "$f.py" ../data ../outputs
done
mv -f ../outputs/*.pdf ../outputs/*.png ../figures/
# The description of the result tables with the headline figures (outputs/results.json) and the guide
# for programs and AI agents (llms.txt). They name the Zenodo archive, so they are written once
# CITATION.cff carries its DOI.
if grep -q '^doi:' ../CITATION.cff; then echo "== make_guide"; python3 -I make_guide.py; fi
