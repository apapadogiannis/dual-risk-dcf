#!/usr/bin/env bash
# Builds paper/manuscript.pdf: the first page (first_page.tex) followed by the published article.
# Usage: paper/build_pdf.sh PATH_TO_THE_PUBLISHED_PDF     (needs pdflatex and qpdf)
set -e
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode -halt-on-error first_page.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error first_page.tex >/dev/null
qpdf first_page.pdf --pages first_page.pdf "$1" -- manuscript.pdf    # the first file gives the title and author fields
rm -f first_page.aux first_page.log first_page.out first_page.pdf
