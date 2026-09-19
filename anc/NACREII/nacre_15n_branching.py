
"""
nacre_15n_branching.py — CNO-I/CNO-II branching at the 15N node.

Computes the ratio of thermal reaction rates

    R_15 = <sigma v>[15N(p,g)16O] / <sigma v>[15N(p,a)12C]

and the fraction of reacting 15N leaking into the CNO-II sequence,

    f_pg = R_15 / (1 + R_15),

from the NACRE II adopted rates tabulated in nacre_15npg.csv and
nacre_15npa.csv. Reproduces the numbers quoted in the CNO section of the
manuscript at the solar core temperature T9 = 0.015.

The NACRE II 15N(p,g)16O evaluation includes the LUNA data of
Caciolli et al., A&A 533, A66 (2011).
"""

import os
import sys

import nacre_reactivity as nr

# -----------------------------
# Configuration
# -----------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PG = os.path.join(HERE, "nacre_15npg.csv")  # NACRE II: 15N(p,g)16O
CSV_PA = os.path.join(HERE, "nacre_15npa.csv")  # NACRE II: 15N(p,a)12C

# Solar core temperature, T_sun ~ 1.5e7 K
T9_SOLAR = 0.015


def branching(T9, which="adopted"):
    """Return (R_15, f_pg) at temperature T9 for the given rate column."""
    pg = nr.load_nacre_rates(CSV_PG, which=which)
    pa = nr.load_nacre_rates(CSV_PA, which=which)
    R = pg.NA_sigmav_T9(T9) / pa.NA_sigmav_T9(T9)
    return R, R / (1.0 + R)


def main():
    T9 = float(sys.argv[1]) if len(sys.argv) > 1 else T9_SOLAR

    print(f"NACRE II rates at T9 = {T9:g} "
          f"(N_A<sigma v>, cm^3 mol^-1 s^-1; adopted [low, high]):")
    for label, path in (("15N(p,g)16O", CSV_PG), ("15N(p,a)12C", CSV_PA)):
        adopted, low, high = (nr.load_nacre_rates(path, which=w).NA_sigmav_T9(T9)
                              for w in ("adopted", "low", "high"))
        print(f"  {label} : {adopted:.4g}   [{low:.4g}, {high:.4g}]")

    R, f = branching(T9)
    print(f"\n  R_15 = <sv>_pg / <sv>_pa = {R:.3e}")
    print(f"  f_pg = R_15 / (1 + R_15)  = {f:.3e}  "
          f"-> {100 * f:.3f}% into CNO-II, {100 * (1 - f):.3f}% back to CNO-I")


if __name__ == "__main__":
    main()
