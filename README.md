# fusion-insights
Science of Nuclear Fusion: Insights and Ideas

<p align="center">
  <img src="art/FusionScale4D.svg" width="600" alt="Comparison of time and scale of fusion environments.">
</p>

## abstract
Advances in several physics domains open up novel paths to smaller scale, higher energy density opportunities to advance small systems for nuclear fusion. Here we survey both legacy and several novel "table-top" approaches which attract current interest. We furthermore address a few related practical and challenging nuclear science topics arising in the context of magnetic confinement and inertial confinement fusion. The contents emphasis includes: By example of solar fusion cycles we draw attention to aneutronic fusion reaction chains. Considering the natural isotopic abundances we assess more carefully the meaning of the term "limitless energy" in the context of actual fusion power realizations. We describe achievements in laser-driven proton-boron fusion, and extensions to a self-sustaining and nearly fully aneutronic proton-boron-nitride reaction cycle. We propose another aneutronic option, where the target is a mix of beryllium and light helium isotope; this 3-helium is arguably the most mentioned fusion component in this article. We look in depth at the plasmonic opto-electric field-enhancement for fusion, and at the particle (muon) catalyzed fusion option. We describe problems in harnessing the *dt* fusion for civilian use. We introduce space travel as forthcoming application of aneutronic fusion.

## authors
<a
id="cy-effective-orcid-url"
class="underline"
href="https://orcid.org/0000-0001-8217-1484"
target="orcid.widget"
rel="me noopener noreferrer"
style="vertical-align: top"><img
src="https://orcid.org/sites/default/files/images/orcid_16x16.png"
style="width: 1em; margin-inline-start: 0.5em"
alt="ORCID iD icon"/> Johann Rafelski</a> and <a
id="cy-effective-orcid-url"
class="underline"
href="https://orcid.org/0000-0001-5474-2649"
target="orcid.widget"
rel="me noopener noreferrer"
style="vertical-align: top"><img
src="https://orcid.org/sites/default/files/images/orcid_16x16.png"
style="width: 1em; margin-inline-start: 0.5em"
alt="ORCID iD icon"/> Andrew J. Steinmetz</a>

## cite as
Rafelski, J. & Steinmetz, A. J. Science of Nuclear Fusion: Insights and Ideas. *Particles* **9**, 94 (2026). https://doi.org/10.3390/particles9040094

Published in the special issue ["Particles and Plasmas in Strong Fields, Part 2"](https://www.mdpi.com/journal/particles/special_issues/C8XU54WI5Z) of *Particles*.

```bibtex
@article{Rafelski:2026fusion,
  author        = {Rafelski, Johann and Steinmetz, Andrew J.},
  title         = {Science of Nuclear Fusion: Insights and Ideas},
  journal       = {Particles},
  volume        = {9},
  number        = {4},
  pages         = {94},
  year          = {2026},
  doi           = {10.3390/particles9040094},
  eprint        = {2609.01366},
  archivePrefix = {arXiv},
  primaryClass  = {nucl-th}
}
```

## doi/arXiv id
- https://doi.org/10.3390/particles9040094
- https://www.mdpi.com/2571-712X/9/4/94
- https://arxiv.org/abs/2609.01366 (preprint)
- https://doi.org/10.48550/arXiv.2609.01366 (preprint)

## contents
- `aneutronic-fusion-v3.tex`, `aneutronic-fusion-v3.bib`, `aneutronic-fusion-v3.bbl` -- manuscript source and bibliography.
- `anc/TikZ/` -- TikZ sources for the figures compiled into the manuscript, with the power curve tables (`*_for_tikz.csv`) plotted by the `PowerInRadOut*` figures.
- `anc/SVG/` -- SVG renders of the `anc/TikZ/` figures, rebuilt with `build.sh`.
- `anc/NACREII/` -- NACRE II reaction rate tables (`nacre_*.csv`) with the cross-section and reactivity scripts built on `nacre_reactivity.py`.
- `anc/ETR25/` -- ETR25 reaction rate tables (`etr25_*.csv`) for the ¹⁷O branch of the CNO bicycle, with the CNO-II/CNO-III branching calculation (`etr25_branching.py`).
- `anc/EXFOR/` -- EXFOR retrieval (`fetch_exfor.sh`) and peak cross-section extraction (`exfor_peaks.py`), Bosch-Hale parameterizations (`bosch_hale.py`), and the optimal ³He spike fraction calculation (`he3_spike_optimum.py`).
- `particles-4572719-for proof/` -- MDPI proof source (`.tex`) and PDF.
- `art/` -- graphical abstract shown above.

## license
Copyright © 2026 by the authors.

The published article is an open access article distributed under the [Creative Commons Attribution (CC BY 4.0) license](https://creativecommons.org/licenses/by/4.0/).
