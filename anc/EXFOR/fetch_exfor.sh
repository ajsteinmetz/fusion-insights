#!/bin/bash
# Download EXFOR excitation functions for the Li/Be/B channels of Fig. 'InteractionLength'.
#
# Data are pulled from EXFOR (Otuka et al., Nucl. Data Sheets 120, 272 (2014))
# through A. J. Koning's flat-file transcription 'exfortables',
# https://github.com/arjankoning1/exfortables
#
# Layout there is  <projectile>/<Target>/xs/<ENDF MT>/<one file per measurement>,
# with MT = 4 (x,n), 16 (x,2n), 22 (x,n alpha), 103 (x,p), 104 (x,d), 105 (x,t),
# 106 (x,3He), 107 (x,alpha), 201 total neutron production, 600/601 (x,p0)/(x,p1),
# 800/801 (x,alpha0)/(x,alpha1).
#
# Usage:  ./fetch_exfor.sh [cache_dir]      (default: ./exfor-cache)
#
# Requires curl.  ~90 small text files, a few hundred kB total.

set -u
CACHE=${1:-./exfor-cache}
REPO=arjankoning1/exfortables
API=https://api.github.com/repos/$REPO/contents
RAW=https://raw.githubusercontent.com/$REPO/master

# Channels needed for the five EXFOR-derived curves.
PATHS="
p/Li006/xs/106
p/Li007/xs/107
p/Li007/xs/004
p/Be009/xs/104
p/Be009/xs/107
p/B011/xs/800
p/B011/xs/801
d/Li006/xs/004
d/Li006/xs/103
d/Li006/xs/105
d/Li006/xs/107
d/Li006/xs/600
d/Li006/xs/601
d/Li007/xs/004
d/Li007/xs/103
d/Li007/xs/105
d/Li007/xs/107
d/Li007/xs/201
"

for p in $PATHS; do
    out="$CACHE/$p"
    mkdir -p "$out"
    files=$(curl -s -m 60 "$API/$p" \
            | sed -n 's/.*"name": "\([^"]*\)".*/\1/p' | grep -v '\.list$')
    for f in $files; do
        [ -s "$out/$f" ] || curl -s -m 60 "$RAW/$p/$f" -o "$out/$f"
    done
    echo "$p: $(ls -1 "$out" | wc -l) datasets"
done

echo
echo "Cached under $CACHE -- now run:  python exfor_peaks.py $CACHE"
