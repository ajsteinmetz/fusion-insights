#!/bin/sh
# Render the anc/TikZ/ figures to SVG in this folder.
#
# FusionScale4D is skipped: its SVG lives in art/ (built from art/FusionScale4D.tex).
#
# The figures are compiled to DVI with pgf's dvisvgm driver rather than to PDF,
# because `dvisvgm --pdf` (2.13) drops the opacity of transparent fills and strokes
# and --exact-bbox misplaces the frame; --bbox=papersize keeps the standalone page.
#
# Usage (from anywhere):  sh anc/SVG/build.sh [Figure ...]
set -e

here=$(cd "$(dirname "$0")" && pwd)
src="$here/../TikZ"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

figs="$*"
[ -n "$figs" ] || figs="EnergyElementsCrust FusionFuture ITERtritium NucInterL
PowerInRadOut PowerInRadOut_Boosted PowerInRadOut_He3Spike YieldpB"

cp "$src"/*.tex "$src"/*.csv "$work"/
cd "$work"
for f in $figs; do
    echo "== $f"
    dvilualatex -interaction=nonstopmode -halt-on-error \
        "\PassOptionsToPackage{dvisvgm}{graphicx}\def\pgfsysdriver{pgfsys-dvisvgm.def}\input{$f}" >/dev/null
    dvisvgm --no-fonts --bbox=papersize -o "$here/$f.svg" "$f.dvi"
done
