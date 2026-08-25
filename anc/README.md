# Ancillary files for Fig. `InteractionLength`

`NucInterL.tex` draws the nuclear interaction length `L_int = m_areal/rho`, with `m_areal = A/(N_A sigma) = 1.66054 A / sigma[barn]` g cm^-2, for each entrance channel at its peak fusion cross-section.

The cross-sections hard-coded in `NucInterL.tex` as `\sigma...` macros are produced by the three scripts here.  **Convention:** for each entrance channel `sigma` is summed over all *exothermic* (Q > 0) exit channels and evaluated at the centre-of-mass energy where that sum is largest.  Endothermic channels consume rather than release energy and are excluded -- notably `7Li(p,n)7Be` (Q = -1.64 MeV), `9Be(p,n)9B` (Q = -1.85 MeV), `7Li(d,p)8Li` (Q = -0.19 MeV) and `7Li(d,t)6Li` (Q = -0.99 MeV).

## Scripts

| file | what it does |
|---|---|
| `bosch_hale.py` | Evaluates the Bosch--Hale parametrization for `d+d`, `t+d`, `d+3He` and locates each peak. No network needed. |
| `fetch_exfor.sh` | Downloads the EXFOR excitation functions for the Li/Be/B channels into a local cache. Needs `curl`. |
| `exfor_peaks.py` | Reports the maximum of every cached dataset, so each adopted value is traceable to a measurement. |

```sh
python bosch_hale.py             # peaks for d+d, t+d, d+3He
python bosch_hale.py --table     # sigma(E) and S(E) for d+d vs energy
./fetch_exfor.sh                 # ~90 files into ./exfor-cache (a few hundred kB)
python exfor_peaks.py            # per-dataset maxima
python exfor_peaks.py --adopted  # adopted values + provenance of each
```

`exfor-cache/` is regenerable and deliberately not committed.

## Sources

* **Bosch--Hale** -- H.-S. Bosch and G. M. Hale, *Nucl. Fusion* **32**, 611 (1992). Note their `E` is the **centre-of-mass** energy; the fit reproduces the canonical 5.07 b for D--T at `E_cm = 64.8 keV` (`E_lab = 108 keV`), which is how this was checked.
* **EXFOR** -- N. Otuka *et al.*, *Nucl. Data Sheets* **120**, 272 (2014), accessed through A. J. Koning's flat-file transcription <https://github.com/arjankoning1/exfortables>. Individual measurements behind each number are named by `exfor_peaks.py --adopted`.

## Caveats worth remembering

* `d+6Li` and `d+7Li` are the softest numbers. They combine channels measured by different groups whose normalizations disagree by up to a factor of two, and both are dominated by neutron-producing branches despite being exothermic.
* `p+7Li` has a ~45% normalization discrepancy at its peak (Cassagnou 86 mb vs Mani 131 mb at `E_p = 3.0 MeV`); the lower, fuller excitation function was adopted.
* `d+d` has a very broad maximum: `sigma` is within 10% of peak over `E_cm = 0.5-3 MeV`, so the 1.25 MeV in the legend is a soft number. It falls steeply below that -- 4.7% of peak at 25 keV. What stays flat at tens of keV is the S-factor, not `sigma`.
